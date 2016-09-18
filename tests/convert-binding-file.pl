#!/usr/bin/perl

# apply-macro softwires_2001:db8:ffff::100
# 2001:db8::40 10.10.0.0,1,6,0
# 2001:db8::41 10.10.0.0,2,6,0
#
use strict;

my $filename = shift;

unless (-f $filename) {
  print <<EOF;
  Usage: $0 <binding-table-file>

EOF
  exit(1);
}

open IN,"$filename" or die "Can't read file $filename";
my $aftr;
print <<EOF;
binding-table {
EOF
while(<IN>) {
  chomp;
  if (/softwires_/) {
    $aftr = $';
#    print "aftr=$aftr\n";
  } else {
    my ($b4,$set) = split(/ /);
    my ($ip,$psid,$psidlen,$offset) = split(/,/,$set);
    print <<EOF;
  binding-entry $b4 {
    binding-ipv4-addr $ip;
    port-set {
      psid-offset $offset;
      psid-len $psidlen;
      psid $psid;
    }
    br-ipv6-addr $aftr;
  }
EOF
  }
}
close IN;
print <<EOF;
}
EOF
exit(0);
