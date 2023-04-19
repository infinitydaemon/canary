#!/usr/bin/perl

use strict;
use warnings;
use LWP::UserAgent;
use JSON;

# Constants
my $token = "a1bc3e769fg832hij3"; # Enter your API auth key
my $console = "1234abc.canary.tools"; # Enter your Console domain
my $dateformat = "1990-01-01-00:00:00"; # Enter starting date of Alerts to retrieve e.g. YYYY-MM-DD-HH:MM:SS

my $filedate = `date "+%Y%m%d%H%M%S"`;
chomp($filedate);
my $filename = "$filedate-$console-alert-export.csv";
my $baseurl = "https://$console/api/v1/incidents/all?auth_token=$token&shrink=true&newer_than=";

# Create a UserAgent object
my $ua = LWP::UserAgent->new();

# Get the incidents using the API
my $response = $ua->get("$baseurl$dateformat");
if ($response->is_success()) {
    my $json_string = $response->content();
    my $decoded_json = decode_json($json_string);
    
    # Open the output file for writing
    open(my $output_file, '>', $filename) or die "Unable to open file '$filename' for writing: $!";
    
    # Write the header row to the file
    print $output_file "Datetime,Alert Description,Target,Target Port,Attacker,Attacker RevDNS\n";
    
    # Iterate over the incidents and write them to the file
    foreach my $incident (@{$decoded_json->{'incidents'}}) {
        my $datetime = $incident->{'description'}->{'created_std'};
        my $description = $incident->{'description'}->{'description'};
        my $dst_host = $incident->{'dst_host'};
        my $dst_port = $incident->{'dst_port'};
        my $src_host = $incident->{'src_host'};
        my $src_host_reverse = $incident->{'src_host_reverse'};
        
        # Escape any double quotes in the fields
        $datetime =~ s/"/\\"/g;
        $description =~ s/"/\\"/g;
        $dst_host =~ s/"/\\"/g;
        $dst_port =~ s/"/\\"/g;
        $src_host =~ s/"/\\"/g;
        $src_host_reverse =~ s/"/\\"/g;
        
        # Write the incident to the file as a CSV row
        print $output_file "\"$datetime\",\"$description\",\"$dst_host\",\"$dst_port\",\"$src_host\",\"$src_host_reverse\"\n";
    }
    
    # Close the output file
    close($output_file);
    
    print "Exported alerts to $filename\n";
}
else {
    die "Failed to retrieve incidents using the API. Status code: " . $response->code() . "\n";
}
