#!/usr/bin/perl

use strict;
use warnings;
use Getopt::Std;
use POSIX qw(strftime);
use LWP::UserAgent;
use JSON qw(decode_json);

Constants
my $DOMAIN = "";
my $AUTH_KEY = "";
my $SAVE = 1;
my $DELETE = 1;
my $FILEDATE = strftime("%Y%m%d%H%M%S", localtime());

my $FILENAME = "$FILEDATE-$DOMAIN-export.json";
print "\nThinkst Canary Alert Management\n";

sub usage {
print "\nBy default, this script will save, acknowledge and then delete your alerts\n";
print "Results are saved to the current working directory in JSON\n";
print "\t-d Domain of your Canary Console\n";
print "\t-a Auth Token for the Canary API\n";
print "\t-s Don't save the incidents (just acknowledge and delete)\n";
print "\t-r Don't remove the incidents (just acknowledge)\n";

exit -1;
}

my %options = ();
getopts("hd:a:rs", %options);

if (defined $options{h}) {
usage();
}

if (defined $options{d}) {
$DOMAIN = $options{d};
}

if (defined $options{a}) {
$AUTH_KEY = $options{a};
}

if (defined $options{s}) {
$SAVE = 0;
}

if (defined $options{r}) {
$DELETE = 0;
}

my $ua = LWP::UserAgent->new;
my $ping_response = $ua->get("https://$DOMAIN.canary.tools/api/v1/ping?auth_token=$AUTH_KEY");
my $ping_data = decode_json($ping_response->content);

if ($ping_data->{result} ne "success") {
print "\nConnection to the Console unsuccessful\n";
exit -1;
}
print "\nConnection to the Console successful\n";

sub save_incidents {
print "\nSaving the incidents\n";
my $incidents_response = $ua->get("https://$DOMAIN.canary.tools/api/v1/incidents/unacknowledged?auth_token=$AUTH_KEY");
my $incidents_data = decode_json($incidents_response->content);
open(my $fh, '>', $FILENAME);
foreach my $incident (@{$incidents_data->{incidents}}) {
print $fh JSON->new->utf8->encode($incident) . "\n";
}
close($fh);
print "Incidents saved to " . $FILENAME . "\n";
}

sub acknowledge_incidents {
print "\nThe following incidents have been acknowledged:\n";
my $ack_response = $ua->post("https://$DOMAIN.canary.tools/api/v1/incidents/acknowledge?auth_token=$AUTH_KEY");
my $ack_data = decode_json($ack_response->content);
foreach my $key (@{$ack_data->{keys}}) {
print "$key\n";
}
}

sub delete_incidents {
print "\nThe following incidents have been deleted:\n";
my $del_response = $ua->post("https://$DOMAIN.canary.tools/api/v1/incidents/delete?auth_token=$AUTH_KEY");
my $del_data = decode_json($del_response->content);
foreach my $key (@{$del_data->{keys}}) {
print "$key\n";
}
}

if ($SAVE) {
save_incidents();
}

acknowledge_incidents();

if ($DELETE) {
delete_incidents();
}