<?php

// This is just because I'm lazy and want to grab limitless data easily
// this just does a basic fetch of the standings/pairings/details

// usage: php limitless_fetch.php [tour hash] [tour code]

if ($argc != 3 || $argv[1] == "help") {
    echo "Usage: php limitless_fetch.php [tour hash] [tour code]\n";
    exit(0);
}

$hash = $argv[1];
$code = $argv[2];

// assumes you run fron the root
$save_location = realpath(__DIR__ . '/../data/majors/grassroots');

$base_url = "https://play.limitlesstcg.com/api/tournaments";

$sections = [
    'details',
    'pairings',
    'standings',
];

foreach ($sections as $section) {
    $url = "{$base_url}/{$hash}/{$section}";

    echo "Fetching {$section} data...";

    $response = file_get_contents($url);
    if ($response === false) {
        echo "Download of '{$section}' failed! Skipping.\n";
        continue;
    }

    echo "Done!\n";

    file_put_contents("{$save_location}/{$code}-{$section}.json", $response);
}

echo "Don't forget to update grassroots.json\n";

echo "Done, good bye!\n";
exit(0);
