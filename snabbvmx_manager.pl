#!/usr/bin/perl

# will be replaced with a Junos JET based script once available

my $ip=shift;
my $identity=shift;
my $cores=shift;

unless ($cores) {
  $cores = "0";
}

my $snabbvmx_binding_file = "snabbvmx-lwaftr.binding";

sub file_changed {
  my ($file) = @_;
  my $new = "$file.new";
#  print("compare file $file with $new ...\n");
  my $delta = `/usr/bin/diff $file $new 2>&1`;
  if ($delta eq "") {
#    print("nothing new in $file\n");
    return 0;
  } else {
    print("file $file has changed\n");
    unlink $file;
    rename $new, $file;
    return 1;
  }
}

sub process_new_config {
  my ($file) = @_;
  open IN,"$file" or die $@;
  my $snabbvmx_config_file;
  my $snabbvmx_lwaftr_file;
  my $closeme = 0;
  my @br_addresses;
  my $br_address;
  my $br_address_idx=-1;
  my $addresses;
  my @softwires;
  my $mac1;
  my $mac2;
  my @files_config;
  my @files_lwaftr;

  while(<IN>) {
    chomp;
    if ($_ =~ /snabbvmx-lwaftr-(\w+)-(\w+)/) {
      if ("" ne $snabbvmx_config_file) {
        if ($closeme == 1) {
          print CFG "  },\n";
        }
        print CFG "}\n";
        close CFG;
        close LWA;
      }
      $mac1 = do{local(@ARGV,$/)="mac_$1";<>};
      chomp($mac1);
      $mac2 = do{local(@ARGV,$/)="mac_$2";<>};
      chomp($mac2);
      print $file_content,"\n";

      $snabbvmx_config_file = "snabbvmx-lwaftr-$1-$2.cfg";
      $snabbvmx_lwaftr_file = "snabbvmx-lwaftr-$1-$2.conf";
      push @files, $snabbvmx_config_file;
      push @files, $snabbvmx_lwaftr_file;
      open CFG,">$snabbvmx_config_file.new" or die $@;
      open LWA,">$snabbvmx_lwaftr_file.new" or die $@;
      print CFG "return {\n  lwaftr = \"$snabbvmx_lwaftr_file\",\n";
      print LWA "vlan_tagging = false,\n";
      print LWA "binding_table = $snabbvmx_binding_file,\n";
    } elsif ($_ =~ /snabbvmx-lwaftr-binding/) {
      open BDG,">$snabbvmx_binding_file.new" or die $@;
    } elsif ($_ =~ /apply-macro ipv6_interface/) {
      if ($closeme == 1) {
        print CFG "  },\n";
        $closeme = 0;
      }
      print CFG "  ipv6_interface = {\n";
      $closeme = 1;
    } elsif ($_ =~ /apply-macro ipv4_interface/) {
      if ($closeme == 1) {
        print CFG "  },\n";
      }
      print CFG "  ipv4_interface = {\n";
      $closeme = 1;
    } elsif ($_ =~ /ipv6_address ([\w:]+)/) {
      print CFG "    ipv6_address = \"$1\",\n";
      print CFG "    description = \"b4\",\n";
      print LWA "aftr_ipv6_ip = $1,\n";
      print LWA "aftr_mac_inet_side = $mac2,\n";
      print LWA "inet_mac = 44:44:44:44:44:44,\n";
    } elsif ($_ =~ /next_hop_mac ([\w.:-]+)/) {
      print CFG "    next_hop_mac = \"$1\",\n";
    } elsif ($_ =~ /service_mac ([\w.:-]+)/) {
      print CFG "    service_mac = \"$1\",\n";
    } elsif ($_ =~ /ipv4_address ([\w.]+)/) {
      print CFG "    ipv4_address = \"$1\",\n";
      print CFG "    description = \"aftr\",\n";
      print LWA "aftr_ipv4_ip = $1,\n";
      print LWA "aftr_mac_b4_side = $mac1,\n";
      print LWA "next_hop6_mac = 66:66:66:66:66:66,\n";
    } elsif ($_ =~ /debug_level (\d+)/) {
      print CFG "    debug_level = $1,\n";
    } elsif ($_ =~ /fragmentation (\w+)/) {
      print CFG "    fragmentation = $1,\n";
    } elsif ($_ =~ /cache_refresh_interval (\d+)/) {
      print CFG "    cache_refresh_interval = $1,\n";
    } elsif ($_ =~ /vlan (\d+)/) {
      print CFG "    vlan = $1,\n";
    } elsif (/apply-macro softwires_([\w:]+)/) {
      $br_address_idx++;
      $br_address=$1;
      push @br_addresses,$br_address;
      print "br_address $br_address_idx is $br_address\n";
    } elsif (/(policy\w+)\s+(\w+)/) {
      print LWA "$1 = " . uc($2) . ",\n";
    } elsif (/(icmp\w+)\s+(\w+)/) {
      print LWA "$1 = $2,\n";
    } elsif (/(ipv\d_mtu)\s+(\d+)/) {
      print LWA "$1 = $2,\n";
    } elsif (/hairpinning/) {
      print LWA "hairpinning = true,\n";
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
    }
  }

  if ($closeme == 1) {
    print CFG "  },\n";
  }
  print CFG "}\n";

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

  close IN;
  close CFG;
  close LWA;
  close BDG;

  # compare the generated files and kick snabbvmx accordingly!
  my $signal="";   # default is no change, no signal needed
  if (&file_changed($snabbvmx_binding_file) > 0) {
    print("Binding table changed. Recompiling on cpus $cores...\n");
    `taskset -c $cores /usr/local/bin/snabb lwaftr compile-binding-table $snabbvmx_binding_file`;
    `ls -l $snabbvmx_binding_file.o`;
    sleep 1;
    print("Recompiling complete. Signaling running snabbvmx ...\n");
    $psids=`ps ax|grep 'snabb snabbvmx'|grep -v grep|awk {'print \$1'}`;
    for (split ' ', $psids) {
      print("Forcing reload for snabb process id $_\n");
      `taskset -c $cores /usr/local/bin/snabb lwaftr control $_ reload`;
    }
    `/usr/local/bin/snabb gc`;  # removing stale counters 
  }

  foreach my $file (@files) {
    if (&file_changed($file))  {
      print("Config has changed for $file\n");
      $signal='TERM';
    }
  }
  if ($signal) {
    print("sending $signal to process snabb snabbvmx\n");
    `pkill -$signal -f 'snabb snabbvmx'`;
  }

}

sub check_config {
  `/usr/bin/ssh -o StrictHostKeyChecking=no -i $identity snabbvmx\@$ip show conf groups > /tmp/config.new1`;

  my $newfile = "/tmp/config.new";
  open NEW, ">$newfile" || die "can't write to file $newfile";
  open IP, "/tmp/config.new1" || die "can't open file /tmp/config.new1";
  my $file;
  while (<IP>) {
    if ($_ =~ /binding_table_file\s+([\w.]+)/) {
      $file=$1;
      print("getting file $file from $ip ...\n");
      my $f="/var/db/scripts/commit/$file";
      `/usr/bin/scp -o StrictHostKeyChecking=no -i $identity snabbvmx\@$ip:$f .`;
      print("reading file $file ...\n");
      open R, "$file" || die "can't open file $file";
      while (<R>) {
        print NEW $_;
      }
      close R;
    } else {
      print NEW $_;
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

#===============================================================
if ("" eq $identity && -f $ip) {
  my $newfile = "/tmp/newfile";
  open NEW, ">$newfile" || die "can't write to file $newfile";
  open IP, "$ip" || die "can't open file $ip";
  my $file;
  while (<IP>) {
    if ($_ =~ /binding_table_file\s+([\w.]+)/) {
      $file=$1;
      print("reading file $file ...\n");
      open R, "$file" || die "can't open file $file";
      while (<R>) {
        print NEW $_;
      }
      close R;
    } else {
      print NEW $_;
    }
  }
  close IP;
  close NEW;
  &process_new_config($newfile);
  exit(0);
}


open CMD,'-|',"echo '<rpc><get-syslog-events> <stream>messages</stream> <event>UI_COMMIT_COMPLETED</event></get-syslog-events></rpc>'|/usr/bin/ssh -T -s -p830 -o StrictHostKeyChecking=no -i $identity snabbvmx\@$ip netconf" or die $@;
my $line;
while (defined($line=<CMD>)) {
  chomp $line;
  if ($line =~ /<syslog-events>/ || $line =~ /UI_COMMIT_COMPLETED/) {
    print("check for config change...\n");
    &check_config();

  }
}
close CMD;

exit;
