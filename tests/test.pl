#!/usr/bin/env perl

use strict;

use JSON::XS qw( decode_json );

my $file=shift;

my $json;
{
  local $/; # enable slurp mode
  open my $fh,"<", $file;
  $json = <$fh>;
  close $fh;
}

#my $json = '[{"Year":"2012","Quarter":"Q3","DataType":"Other 3","Environment":"STEVE","Amount":125},{"Year":"2012","Quarter":"Q4","DataType":"Other 2","Environment":"MIKE","Amount":500}]';

my $data = decode_json($json);

my $instances = $data->{"configuration"}{"softwire-config"}{"lw4over6"}{"lwaftr"}{"lwaftr-instances"}{"lwaftr-instance"};

my $bdfile = $data->{"configuration"}{"softwire-config"}{"lw4over6"}{"lwaftr"}{"binding-table-file"};

print "global binding table file $bdfile\n";

foreach my $instance (@$instances) {

  print "--------> snabb xe" . $instance->{"id"} . ":\n";

  if ($instance->{"binding-table"}) {
    my $be = $instance->{"binding-table"}{"binding-entry"};
    my %bindings;
    foreach my $xy (@$be) {
      my $portset = $xy->{"port-set"};
      $bindings{$xy->{"lwaftr-ipv6-addr"}} .= join(",", $xy->{"binding-ipv6info"},$xy->{"binding-ipv4-addr"},$portset->{"psid"},$portset->{"psid-len"},$portset->{"offset"}) . "\n";
    }
    foreach my $ipv6 (sort keys %bindings) {
      print "apply-macro softwires_$ipv6\n";
      print $bindings{$ipv6};
    }
  }

  # assume any other entry as a key value pair for Snabb
  for my $record (keys($instance)) {
    my $val = $instance->{$record};
    unless ( $record eq "binding-table" or $record eq "id") {
      print "$record = $val\n";
    }
  }

  print "\n";
}

