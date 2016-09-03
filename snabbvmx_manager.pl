#!/usr/bin/env perl

use strict;

use JSON::XS qw( decode_json );

my $ip = shift;
my $identity = shift;

#------------------------------------------------------------------
#------------------------------------------------------------------
sub file_changed {
  my ($file) = @_;
  my $new = "$file.new";
  my $delta = `/usr/bin/diff $file $new 2>&1`;
  if ($delta eq "") {
    return 0;
  } else {
    print("file $file has changed\n");
    unlink $file;
    rename $new, $file;
    return 1;
  }
}

#------------------------------------------------------------------
# read binding table from file in compact form:
# b4_ipv6_address ipv4_address,psid,psid_len,offset
# create snabb formatted binding table file and compile it 
#------------------------------------------------------------------
sub process_binding_table_file {
  my ($btf) = @_;
  my $btfsource = "$btf.s";
  my $btfcompiled = "$btf.s.o";
  my @br_addresses;
  my $br_address;
  my $br_address_idx=-1;
  my %addresses;
  my @softwires;

  if (-f $btfcompiled and -M $btf > -M $btfcompiled) {
    print "$btf: file $btfcompiled is newer, no need to recompile\n";
    return 0;
  }

  # binding table file has changed. Process it.
 
  print "reading binding file $btf\n";
  open IN,"$btf" or die $@;
  while(<IN>) {
    chomp;
    if (/lwaftr-ipv6-addr\s+([\w:]+)/ or /softwires_([\w:]+)/) {
      $br_address_idx++;
      $br_address=$1;
      push @br_addresses,$br_address;
      print "$btf br_address $br_address_idx is $br_address\n";
    } elsif (/([\w:]+)+\s+(\d+.\d+.\d+.\d+),(\d+),(\d+),(\d+)/) {
      # binding entry ipv6 ipv4,psid,psid_len,offset
      my $shift=16 - $4 - $5;
      my $sw = "{ ipv4=$2, psid=$3, b4=$1, aftr=$br_address_idx }";
      push @softwires,$sw;
      if ($shift > 0) {
        $addresses{"$2"} = "{psid_length=$4, shift=$shift}";
      } else {
        $addresses{"$2"} = "{psid_length=$4}";
      }
    } else {
      print "$btf ignoring line $_\n";
    }
  }
  close(IN);
  # create the snabb source binding table file
  open BDG,">$btfsource" or die $@;
  print BDG "psid_map {\n";
  foreach my $key (sort keys %addresses) {
    print BDG "  $key $addresses{$key}\n";
  }

  print BDG "}\nbr_addresses {\n";
  foreach my $ipv6 (@br_addresses) {
    print BDG "  $ipv6,\n"
  }
  print BDG "}\nsoftwires {\n";
  foreach my $sw (@softwires) {
    print BDG "  $sw\n";
  }
  print BDG "}\n";
  close BDG;

  # trigger binding table compilation
  print "Binding table $btfsource changed. Recompiling ...";
  `/usr/local/bin/snabb lwaftr compile-binding-table $btfsource`;
  print "done.\n\n";
  return 1;
} # /process_binding_table_file/

#------------------------------------------------------------------
#------------------------------------------------------------------
sub check_config {
  `/usr/bin/ssh -o StrictHostKeyChecking=no -i $identity snabbvmx\@$ip \"show conf ietf-softwire:softwire-config|display json\" > /tmp/config.new1`;

  my $newfile = "/tmp/config.new";
  open NEW, ">$newfile" or die "can't write to file $newfile";
  open IP, "/tmp/config.new1" or die "can't open file /tmp/config.new1";
  my $file;
  while (<IP>) {
    print NEW $_;
    if ($_ =~ /\"binding-table-file\"\s+:\s+\"([\w.]+)\"/) {
      $file=$1;
      print("getting file $file from $ip ...\n");
      my $f="/var/db/scripts/commit/$file";
      `/usr/bin/scp -o StrictHostKeyChecking=no -i $identity snabbvmx\@$ip:$f .`;
      print("reading file $file ...\n");
#      open R, "$file" or die "can't open file $file";
#      while (<R>) {
#        print NEW $_;
#      }
#      close R;
    } 
  }
  close IP;
  close NEW;

  my $delta = `/usr/bin/diff /tmp/config.new /tmp/config.old 2>&1`;
  if ($delta eq "") {
    print("snabbvmx_manager: no config change related to snabbvmx found\n");
  } else {
    print("snabbvmx_manager: updated config for snabbvmx!\n");
    unlink "/tmp/config.old";
    rename "/tmp/config.new","/tmp/config.old";
    &process_new_config("/tmp/config.old");
  }
}

#------------------------------------------------------------------
#------------------------------------------------------------------
sub process_new_config {
  my ($file) = @_;
  my $json;
  {
    local $/; # enable slurp mode
    open my $fh,"<", $file;
    $json = <$fh>;
    close $fh;
  }


  my %snabbpid;
  my @files = </run/snabb/*/nic/id>;
  foreach my $file (@files) {
    my $id;
    $file =~ /(\d+)/;
    my $pid = $1;
    open(my $fh, '<', "$file") or die "cannot open file $file";
    {
      local $/;
      $id = <$fh>;
    }
    close($fh);
    # print "dir=$file pid=$pid id=$id\n";
    $snabbpid{$id} = $pid;
  }

  if ($json) {
    my $data = decode_json($json);

    my $instances = $data->{"configuration"}{"softwire-config"}{"lw4over6"}{"lwaftr"}{"lwaftr-instances"}{"lwaftr-instance"};

    my $globalbdfile = $data->{"configuration"}{"softwire-config"}{"lw4over6"}{"lwaftr"}{"binding-table-file"};
    my $reload = 0;

    if (-f $globalbdfile) {
      print "global binding table file $globalbdfile\n";
      $reload = &process_binding_table_file($globalbdfile);
      print "global binding table file $globalbdfile reload=$reload\n";
    }

    foreach my $instance (@$instances) {

      my $id = "xe" . $instance->{"id"};
      print "--------> snabb $id:\n";

      my $bdf = $globalbdfile;

      if ($instance->{"binding-table"}) {
        $bdf = "binding_table_$id.txt";
        print "creating binding table file $bdf\n";
        open BDF,">$bdf" or die $@;
        my $be = $instance->{"binding-table"}{"binding-entry"};
        my %bindings;
        my %array;
        foreach my $xy (@$be) {
          my $portset = $xy->{"port-set"};
          my $lwaftripv6 = $xy->{"lwaftr-ipv6-addr"}; 
          push @{$bindings{$lwaftripv6}}, $xy->{"binding-ipv6info"} . " " . join(",", $xy->{"binding-ipv4-addr"},$portset->{"psid"},$portset->{"psid-len"},$portset->{"offset"});
        }

        foreach my $lwaftripv6 (sort keys %bindings) {
          print BDF "lwaftr-ipv6-addr $lwaftripv6\n";
          foreach my $entry (@{$bindings{$lwaftripv6}}) {
            print BDF $entry . "\n";
          }
        }
        close BDF;
      }

      my $snabbvmx_config_file = "snabbvmx-lwaftr-$id.cfg";
      my $snabbvmx_lwaftr_file = "snabbvmx-lwaftr-$id.conf";

      open CFG,">$snabbvmx_config_file.new" or die $@;
      # WARN user if ipv6 and ipv4 vlan differ
      my $vlan = "nil";
      if ($instance->{"ipv6_vlan"}) {
        $vlan = $instance->{"ipv6_vlan"};
      }
      if ($instance->{"ipv4_vlan"}) {
        $vlan = $instance->{"ipv4_vlan"};
      }
      print CFG <<EOF;
return {
  lwaftr = \"$snabbvmx_lwaftr_file\",
  settings = {
    vlan = $vlan,
  },
  ipv6_interface = {
    ipv6_address = \"$instance->{"ipv6_address"}\",
    cache_refresh_interval = $instance->{"cache_refresh_interval"},
EOF
      print CFG "    ipv6_ingress_filter = \"$instance->{'ipv6_ingress_filter'}\"," if $instance->{'ipv6_ingress_filter'};
      print CFG "    ipv6_egress_filter = \"$instance->{'ipv6_egress_filter'}\"," if $instance->{'ipv6_eress_filter'};
      print CFG "    fragmentation = $instance->{'fragmentation'}," if $instance->{'fragmentation'};
      print CFG <<EOF;
  },
  ipv4_interface = {
    ipv4_address = \"$instance->{"ipv4_address"}\",
    cache_refresh_interval = $instance->{"cache_refresh_interval"},
EOF
      print CFG "    ipv4_ingress_filter = \"$instance->{'ipv4_ingress_filter'}\"," if $instance->{'ipv4_ingress_filter'};
      print CFG "    ipv4_egress_filter = \"$instance->{'ipv4_egress_filter'}\"," if $instance->{'ipv4_eress_filter'};
      print CFG "    fragmentation = $instance->{'fragmentation'}," if $instance->{'fragmentation'};
      print CFG <<EOF;
  },
}
EOF
      close CFG;

      my $mac = "00:00:00:00:00:00";
      if (-f "mac_$id") {
        $mac = do{local(@ARGV,$/)="mac_$id";<>};
        chomp $mac;
      }

      my $ipv4_mtu = $instance->{"tunnel-payload-mtu"};
      my $ipv6_mtu = $instance->{"tunnel-path-mru"};

      open LWA,">$snabbvmx_lwaftr_file.new" or die $@;
      print LWA <<EOF;
vlan_tagging = false,
binding_table = $bdf.s,
aftr_ipv6_ip = 2001:db8::1,
aftr_ipv4_ip = $instance->{"ipv4_address"},
aftr_mac_inet_side = $mac,
inet_mac = 44:44:44:44:44:44,
aftr_mac_b4_side = $mac,
next_hop6_mac = 66:66:66:66:66:66,
ipv4_mtu = $ipv4_mtu,
ipv6_mtu = $ipv6_mtu,
EOF
      print LWA "hairpinning = $instance->{'hairpinning'}," if $instance->{'hairpinning'};
      print LWA "policy_icmpv4_incoming = $instance->{'policy_icmpv4_incoming'}," if $instance->{'policy_icmpv4_incoming'};
      print LWA "policy_icmpv4_outgoing = $instance->{'policy_icmpv4_outgoing'}," if $instance->{'policy_icmpv4_outgoing'};
      print LWA "policy_icmpv6_incoming = $instance->{'policy_icmpv6_incoming'}," if $instance->{'policy_icmpv6_incoming'};
      print LWA "policy_icmpv6_outgoing = $instance->{'policy_icmpv6_outgoing'}," if $instance->{'policy_icmpv6_outgoing'};
      close LWA;

      my $rv = &process_binding_table_file($bdf);
      my $psid = $snabbpid{$id};
      delete $snabbpid{$id}; # avoid getting killed during cleanup at the end of this function
      print "psid of snabb process for $id is $psid\n";

      if ($rv or $reload) {
        # reload binding table
        if ($psid) {
          print "forcing binding table reload for $id ($psid)\n";
          `/usr/local/bin/snabb lwaftr control $psid reload`;
        }
      }

      if (0 < &file_changed($snabbvmx_lwaftr_file) + &file_changed($snabbvmx_config_file)) {
        if ($psid) {
          print "sending TERM to snabb process for $id ($psid)\n"; 
          `kill -TERM $psid`;
        }
      }
    }
  }

  # cleanup of snabb processes no longer needed
  foreach my $id (keys %snabbpid) {
    unlink "/tmp/snabbvmx-lwaftr-$id.cfg";
    unlink "/tmp/snabbvmx-lwaftr-$id.conf";
    print "send TERM to snabb process for $id. Has no longer a lwaftr config\n";
    `kill -TERM $snabbpid{$id}`;
  }
}

#===============================================================
# main()
#===============================================================

if ("" eq $identity && -f $ip) {
  my $file = $ip;
  &process_new_config($file);
  exit(0);
}

open CMD,'-|',"echo '<rpc><get-syslog-events> <stream>messages</stream> <event>UI_COMMIT_COMPLETED</event></get-syslog-events></rpc>'|/usr/bin/ssh -T -s -p830 -o StrictHostKeyChecking=no -i $identity snabbvmx\@$ip netconf" or die $@;
my $line;
while (defined($line=<CMD>)) {
  chomp $line;
  if ($line =~ /<syslog-events>/ or $line =~ /UI_COMMIT_COMPLETED/) {
    print("check for config change...\n");
    &check_config();

  }
}
close CMD;

exit;

