#!/usr/bin/perl
# Copyright (c) 2016, Juniper Networks, Inc.
# All rights reserved.

use strict;
use File::Copy qw(copy);

use JSON::XS qw( decode_json );

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
  my $btfsourcenew = "$btf.s.new";
  my $btfcompiled = "$btf.s.o";
  my @br_addresses;
  my $br_address;
  my $br_address_idx=-1;
  my %addresses;
  my @softwires;

  print "reading binding file $btf\n";
  open IN,"$btf" or die $@;
  while(<IN>) {
    chomp;
    if (/br-ipv6-addr\s+([\w:]+)/ or /softwires_([\w:]+)/) {
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
  open BDG,">$btfsourcenew" or die $@;
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

  if (-f $btfsource) {
    print "compare files $btfsourcenew $btfsource\n";
    my $delta = `/usr/bin/cmp $btfsourcenew $btfsource`;
    unless ($delta) {
      print "no change detected between $btfsourcenew $btfsource\n";
      return 0;
    }
  }
  copy $btfsourcenew, $btfsource;
  # trigger binding table compilation
  print "Binding table $btfsource changed. Recompiling ...";
  `/usr/local/bin/snabb lwaftr compile-binding-table $btfsource`;
  print "done.\n\n";
  return 1;
} # /process_binding_table_file/

#------------------------------------------------------------------
#------------------------------------------------------------------
sub check_config {
  `/usr/bin/ssh -o StrictHostKeyChecking=no 128.0.0.1 \"show conf ietf-softwire:softwire-config|display json\" > /tmp/config.new1`;

  my $newfile = "/tmp/config.new";
  open NEW, ">$newfile" or die "can't write to file $newfile";
  open IP, "/tmp/config.new1" or die "can't open file /tmp/config.new1";
  my $file;
  my $R3 = 0;
  $R3 = 1 if -e "/tmp/junos-vmx-x86-64-16.1R3.10.qcow2";
  while (<IP>) {
    # fix a JSON formatting bug 
    if ($R3) {
      # 16.1R3 has a bug omitting ',' for augmented leafs. R4 has this fixed
      $_ =~ s/\s+\"jnx-aug-softwire:/,\"/;
    }
    $_ =~ s/jnx-aug-softwire://;  # remove namespace prefix for our parsing
    $_ =~ s/ietf-softwire://;  # remove namespace prefix for our parsing
    print NEW $_;
    if ($_ =~ /binding-table-file\"\s+:\s+\"([^\"]+)\"/) {
      $file=$1;
      print("getting file $file from 128.0.0.1 ...\n");
      my $f="/var/db/scripts/commit/$file";
      `/usr/bin/scp -o StrictHostKeyChecking=no 128.0.0.1:$f .`;
      my $md5sum=`md5sum $file`;
      chomp $md5sum;
      print NEW ",\"md5sum\" : \"$md5sum\"\n";
      print("done\n");
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
  print ("process_new_config\n");
  # get list of nics, required for cleanup
  my @files = </tmp/mac_*>;
  foreach my $file (@files) {
    my $id;
    $file =~ /_(\w+)/;
    if ($1) {
      $snabbpid{$1} = -1;
    }
  }
  # get list of running snabb instances 
  @files = </run/snabb/*/nic/id>;
  foreach my $file (@files) {
    my $id;
    $file =~ /(\d+)/;
    my $pid = $1;
    open(my $fh, "$file") or die "cannot open file $file";
    $id = <$fh>;
    $id = substr($id,0,3);  # we actually get a string of 256 characters, mostly \0
    close($fh);
    my $len=length($id);
    $snabbpid{$id} = $pid;
    my $psid = $snabbpid{$id};
    print "psid for $id is $psid\n";
  }

  if ($json) {
    my $data = decode_json($json);

    my $instances = $data->{"configuration"}{"softwire-config"}{"binding"}{"br"}{"br-instances"}{"br-instance"};
    unless ($instances) {
      $instances = $data->{"softwire-config"}{"binding"}{"br"}{"br-instances"}{"br-instance"};
    }

    my $globalbdfile = $data->{"configuration"}{"softwire-config"}{"binding"}{"br"}{"binding-table-file"};
    unless ($globalbdfile) {
      $globalbdfile = $data->{"softwire-config"}{"binding"}{"br"}{"binding-table-file"};
    }
    my $reload = 0;

    if (-f $globalbdfile) {
      print "global binding table file $globalbdfile\n";
      $reload = &process_binding_table_file($globalbdfile);
      print "global binding table file $globalbdfile reload=$reload\n";
    } else {
      $globalbdfile="binding_table_empty.txt";
      open (OUT, ">$globalbdfile") || die "Can't write to $globalbdfile";
      close OUT;
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
          my $lwaftripv6 = $xy->{"br-ipv6-addr"}; 
          push @{$bindings{$lwaftripv6}}, $xy->{"binding-ipv6info"} . " " . join(",", $xy->{"binding-ipv4-addr"},$portset->{"psid"},$portset->{"psid-len"},$portset->{"psid-offset"});
        }

        foreach my $lwaftripv6 (sort keys %bindings) {
          print BDF "br-ipv6-addr $lwaftripv6\n";
          foreach my $entry (@{$bindings{$lwaftripv6}}) {
            print BDF $entry . "\n";
          }
        }
        close BDF;
      }

      my $snabbvmx_config_file = "snabbvmx-lwaftr-$id.cfg";
      my $snabbvmx_lwaftr_file = "snabbvmx-lwaftr-$id.conf";

      open CFG,">$snabbvmx_config_file.new" or die $@;
      print CFG <<EOF;
return {
  lwaftr = \"$snabbvmx_lwaftr_file\",
  settings = {
EOF
    print CFG "    ingress_drop_monitor = \"$instance->{'ingress_drop_action'}\",\n" if $instance->{'ingress_drop_action'};
    print CFG "    ingress_drop_threshold = $instance->{'ingress_drop_threshold'},\n" if $instance->{'ingress_drop_threshold'};
    print CFG "    ingress_drop_interval = $instance->{'ingress_drop_interval'},\n" if $instance->{'ingress_drop_interval'};
    print CFG "    ingress_drop_wait = $instance->{'ingress_drop_wait'},\n" if $instance->{'ingress_drop_wait'};
      print CFG <<EOF;
  },
  ipv6_interface = {
    ipv6_address = \"$instance->{"ipv6_address"}\",
    cache_refresh_interval = $instance->{"cache_refresh_interval"},
EOF
      print CFG "    ipv6_ingress_filter = \"$instance->{'ipv6_ingress_filter'}\",\n" if $instance->{'ipv6_ingress_filter'};
      print CFG "    ipv6_egress_filter = \"$instance->{'ipv6_egress_filter'}\",\n" if $instance->{'ipv6_eress_filter'};
      print CFG "    fragmentation = $instance->{'fragmentation'},\n" if $instance->{'fragmentation'};
      print CFG <<EOF;
  },
  ipv4_interface = {
    ipv4_address = \"$instance->{"ipv4_address"}\",
    cache_refresh_interval = $instance->{"cache_refresh_interval"},
EOF
      print CFG "    ipv4_ingress_filter = \"$instance->{'ipv4_ingress_filter'}\",\n" if $instance->{'ipv4_ingress_filter'};
      print CFG "    ipv4_egress_filter = \"$instance->{'ipv4_egress_filter'}\",\n" if $instance->{'ipv4_eress_filter'};
      print CFG "    fragmentation = $instance->{'fragmentation'},\n" if $instance->{'fragmentation'};
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
      my $hairpinning = $instance->{'hairpinning'} ? $instance->{'hairpinning'} : "false";
      print LWA <<EOF;
hairpinning = $hairpinning,
binding_table = $bdf.s,
aftr_ipv6_ip = 2001:db8::1,
aftr_ipv4_ip = $instance->{"ipv4_address"},
aftr_mac_inet_side = $mac,
inet_mac = 02:02:02:02:02:02,
aftr_mac_b4_side = $mac,
next_hop6_mac = 02:02:02:02:02:02,
ipv4_mtu = $ipv4_mtu,
ipv6_mtu = $ipv6_mtu,
EOF
      if ($instance->{'ipv4_vlan'} or $instance->{'ipv6_vlan'}) {
        print LWA "vlan_tagging = true,\n";
        print LWA "v4_vlan_tag = $instance->{'ipv4_vlan'},\n" if $instance->{'ipv4_vlan'};
        print LWA "v6_vlan_tag = $instance->{'ipv6_vlan'},\n" if $instance->{'ipv6_vlan'};
      } else {
        print LWA "vlan_tagging = false,\n";
      }
      print LWA "policy_icmpv4_incoming = $instance->{'policy_icmpv4_incoming'},\n" if $instance->{'policy_icmpv4_incoming'};
      print LWA "policy_icmpv4_outgoing = $instance->{'policy_icmpv4_outgoing'},\n" if $instance->{'policy_icmpv4_outgoing'};
      print LWA "policy_icmpv6_incoming = $instance->{'policy_icmpv6_incoming'},\n" if $instance->{'policy_icmpv6_incoming'};
      print LWA "policy_icmpv6_outgoing = $instance->{'policy_icmpv6_outgoing'},\n" if $instance->{'policy_icmpv6_outgoing'};
      print LWA "max_fragments_per_reassembly_packet = $instance->{'max_fragments_per_reassembly_packet'},\n" if $instance->{'max_fragments_per_reassembly_packet'};
      print LWA "max_ipv4_reassembly_packets = $instance->{'max_ipv4_reassembly_packets'},\n" if $instance->{'max_ipv4_reassembly_packets'};
      print LWA "max_ipv6_reassembly_packets = $instance->{'max_ipv6_reassembly_packets'},\n" if $instance->{'max_ipv6_reassembly_packets'};
      print LWA "icmpv6_rate_limiter_n_packets = $instance->{'icmpv6_rate_limiter_n_packets'},\n" if $instance->{'icmpv6_rate_limiter_n_packets'};
      print LWA "icmpv6_rate_limiter_n_seconds = $instance->{'icmpv6_rate_limiter_n_seconds'},\n" if $instance->{'icmpv6_rate_limiter_n_seconds'};
      close LWA;

      my $rv = &process_binding_table_file($bdf);
      my $psid = $snabbpid{$id};
      print "psid of snabb process for $id is $psid\n";
      delete $snabbpid{$id}; # avoid getting killed during cleanup at the end of this function

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
  print "cleanup\n";
  foreach my $id (keys %snabbpid) {
    print "cleanup for $id\n";
    my $f1 = sprintf("snabbvmx-lwaftr-%s.cfg", $id);
    unlink "snabbvmx-lwaftr-$id.cfg";
    unlink "snabbvmx-lwaftr-$id.conf";
    if ($snabbpid{$id} > 0) {
      print "send TERM to snabb process for $id. Has no longer a lwaftr config\n";
      `kill -TERM $snabbpid{$id}`;
    }
  }
}

#===============================================================
# main()
#===============================================================

my $file = shift;

if (-f $file) {
  &process_new_config($file);
  exit(0);
}

open CMD,'-|',"echo '<rpc><get-syslog-events> <stream>messages</stream> <event>UI_COMMIT_COMPLETED</event></get-syslog-events></rpc>'|/usr/bin/ssh -T -s -p830 -o StrictHostKeyChecking=no 128.0.0.1 netconf" or die $@;
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
