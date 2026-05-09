<?php

// This is a super rudimentary script that can be used to simulate "live" events. 
// What it actually does is just download a specified list of Pokedata json at
// an interval, checks for a change, and then runs the process scripts. This
// whole thing is fairly manual, so the easiest way to run this will be via screen
// or tmux or something similar.

// And yes, I did write PHP on purpose!

if (!file_exists(__DIR__ . "/../regieleki.ini")) {
    echo "regieleki.ini not found, exiting\n";
    exit;
}

elog("Regieleki starting!");

$data_dir_base = __DIR__ . "/../data/majors";

// parse regieleki.ini (see README)
$ini_data = parse_ini_file("regieleki.ini", true);

$tournament_settings = [];
$tour_tracker = [];

foreach ($ini_data as $section => $data) {
    if ($section == "main_config") {
        foreach ($data as $key => $value) {
            ${$key} = $value;
        }
        continue;
    }

    $tournament_settings[$section] = [
        'start' => time(),
        'end' => time() + 28800, // 8 hours
        'remote' => $data['pokedata_url'],
        'local' => "{$data_dir_base}/{$current_season}/{$section}-standings.json",
        'process' => "{$current_season}:{$section}",
    ];

    if (!empty($data['start_time'])) {
        $start = (new DateTime("{$data['start_time']} {$data['time_zone']}"))->getTimestamp();
        $tournament_settings[$section]['start'] = $start;
        $tournament_settings[$section]['end'] = $start + 28800;
        elog("[{$section}] Initial delay set, will start collecting at " . date("Y-m-d H:i:s", $start));
    } else {
        elog("[{$section}] No start time set, will start now!");
    }

    if (!empty($data['end_time'])) {
        $end = (new DateTime("{$data['start_time']} {$data['time_zone']}"))->getTimestamp();
        $tournament_settings[$section]['end'] = $end;
    }
    elog("[{$section}] Scheduled to finish at " . date("Y-m-d H:i:s", $tournament_settings[$section]['end']));

    $tour_tracker[$section] = true;
}

$data_dir = "{$data_dir_base}/{$current_season}";

elog("Got " . count($tournament_settings) . " tours to check");

if ($build_prod) {
    elog("Will build as production (--prod)");
    $build_prod = '--prod';
} else {
    $build_prod = '';
}

elog("Setup done. Running...");

$backoff = 0;
$attempts = 0;

$updates_file = __DIR__ . "/../public/data/{$current_season}/updates.json";
if (!file_exists($updates_file)) {
    elog("Updates file not found, creating empty one");
    file_put_contents($updates_file, "{}");
}

$updates = [];

while (1) {
    $to_process = [];

    if (empty(array_filter($tour_tracker))) {
        elog("Scheduled finish time reached for all tours! Exiting.");
        break;
    }

    foreach ($tournament_settings as $tour => $tour_info) {
        if (!$tour_tracker[$tour]) {
            // tour has completed
            continue;
        }

        if (time() < $tour_info['start']) {
            // tour hasn't started yet
            continue;
        }

        if (time() > $tour_info['end']) {
            elog("[{$tour}] Scheduled finish time reached!");
            $tour_tracker[$tour] = false;
            continue;
        }

        $to_process[$tour] = $tour_info;
    }

    $process_cmd = [];
    foreach ($to_process as $tour => $process) {
        elog("[{$tour}] Downloading {$process['remote']}... ", '');

        try {
            $remote_data = make_request($process['remote']);
        } catch (Exception $e) {
            elog_cont($e->getMessage());
            continue;
        }

        if (json_decode($remote_data) === null) {
            $attempts++;

            // backoff starts at +1 minute
            $backoff = 30 * pow(2, $attempts);

            elog_cont("Invalid JSON, starting backoff...");
            break;
        } else {
            $backoff = 0;
            $attempts = 0;
        }

        elog_cont("Done!");

        $tour_hash = sha1($remote_data);

        if (!isset($updates[$tour])) {
            $updates[$tour] = "";
        }

        if ($updates[$tour] !== $tour_hash) {
            if (file_put_contents($process['local'], $remote_data) === false){
                elog_cont("[{$tour}] Unable to write to '{$local_file}', skipping");
                continue;
            }
            $updates[$tour] = $tour_hash;

            $process_cmd[] = $process['process'];
        } else {
            elog("[{$tour}] No changes to tour data, moving on");
        }

        // small sleep between downloads
        sleep(mt_rand(1, 3));
    }

    if (file_put_contents($updates_file, json_encode($updates)) === false) {
        elog("Unable to write to '{$updates_file}'");
    }

    if (!empty($process_cmd)) {
        elog("Building Reportworm... ", '');
        exec("python3 scripts/porygon.py {$build_prod} --process " . implode(',', $process_cmd));
        elog_cont("Done!");
    } else {
        elog("Nothing to process right now...");
    }

    $sleep_time = $refresh_rate + mt_rand($refresh_fuzz_min, $refresh_fuzz_max) + $backoff;
    elog("Sleeping for {$sleep_time} seconds...");
    sleep($sleep_time);
}

elog("Resetting updates file");
file_put_contents($updates_file, "{}");

elog("All done! Thanks for running Regieleki!");
exit;


function elog($text, $end = "\n") {
    echo "[ELEKI] {$text}{$end}";
}

function elog_cont($text, $end = "\n") {
    echo "{$text}{$end}";
}

// Pokedata's hosting is liberal with blocking, so this attempts to fake the request as
// much as possible to look more legit / random. Will it work? No idea! Make sure the
// refresh interval isn't too short. 5 minutes got me banned after a few hours.
function make_request($url) {
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_HTTPHEADER => [
            'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language: en-US,en;q=0.5',
            'Accept-Encoding: gzip, deflate, br',
            'Cache-Control: max-age=0',
            'Connection: keep-alive',
            'Keep-Alive: 300',
            'Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7',
            'Accept-Language: en-us,en;q=0.5',
            'Pragma: ',
        ],
        CURLOPT_USERAGENT => 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
        CURLOPT_ENCODING => 'gzip,deflate',
        CURLOPT_AUTOREFERER => true,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 30,
    ]);

    $result = curl_exec($ch);

    if ($result === false) {
        throw new Exception('Curl Error: ' . curl_error($ch));
    }

    curl_close($ch);

    return $result;
}
