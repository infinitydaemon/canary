#!/usr/bin/perl

use strict;
use warnings;

use POSIX qw(strftime);
use LWP::UserAgent;
use JSON qw(decode_json);

use constant {
    AUTH_TOKEN_DEFAULT => 'deadbeef12345678',
    DOMAIN_HASH_DEFAULT => '1234abcd',
};

my $auth_token = $ENV{AUTH_TOKEN} // AUTH_TOKEN_DEFAULT;
my $domain_hash = $ENV{DOMAIN_HASH} // DOMAIN_HASH_DEFAULT;

my $results_file_name = "${domain_hash}_alerts.csv";
my $state_store_file_name = "${domain_hash}_state_store.txt";

my $base_url = "https://$domain_hash.canary.tools";
my $page_size = 1500;
my $incidents_since = 0;
my $loaded_state = 0;
my $sort_on_column = 1;
my $add_blank_notes_column = 0;
my $add_additional_event_details = 0;

sub sort_results {
    system("cp $results_file_name $results_file_name.unsorted");
    open(my $results_fh, ">", $results_file_name) or die "Cannot open file $results_file_name for writing: $!";
    open(my $header_fh, "<", "$results_file_name.unsorted") or die "Cannot open file $results_file_name.unsorted for reading: $!";
    print $results_fh <$header_fh>; # Save the header in the file
    close $header_fh;
    open(my $data_fh, "-|", "tail -n+2 $results_file_name.unsorted | sort -t ',' -k $sort_on_column,$sort_on_column -n") or die "Cannot open pipe from sort command: $!";
    while (<$data_fh>) {
        print $results_fh $_;
    }
    close $data_fh;
    close $results_fh;
    unlink("$results_file_name.unsorted");
}

sub stop {
    sort_results();
    print "\n"; # Newline to not override status feedback
    if (!$loaded_state) {
        print "Results saved in $results_file_name\n";
    } else {
        print "Updated results in $results_file_name\n";
    }
    exit 0;
}

sub fail {
    print "\n"; # Newline to not override status feedback
    print "$_\n" for @_;
    exit 1;
}

sub create_csv_header {
    my $header = "";

    if ($add_blank_notes_column) {
        $header .= "Notes,";
        $sort_on_column++;
    }

    $header .= "Updated ID";
    $header .= ",Date and Time";
    $header .= ",Alert Description";
    $header .= ",Target";
    $header .= ",Target Port";
    $header .= ",Attacker";
    $header .= ",Attacker RevDNS";

    if ($add_additional_event_details) {
        $header .= ",Additional Events";
    }

    open(my $results_fh, ">", $results_file_name) or die "Cannot open file $results_file_name for writing: $!";
    print $results_fh "$header\n";
    close $results_fh;
}

sub extract_incident_data {
    my ($content) = @_;

    my $description_fields = ".created_std,.description,.dst_host,.dst_port,.src_host,.src_host_reverse";
    if ($add_additional_event_details) {
        $description_fields .= ",(.events | tostring)";
    }

    my $json = eval { decode_json($content) };
    fail("Error parsing JSON response: $@") if $@;

    my $data = '';
    for my $incident (@{ $json->{incidents} }) {
        my $id = $incident->{updated_id};
