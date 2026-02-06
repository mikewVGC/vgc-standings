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

$updates_file = __DIR__ . "/../public/data/updates.json";

if (!file_exists($updates_file)) {
    elog("Updates file not found, creating a blank one");
    file_put_contents($updates_file, '{}');
}

// parse regieleki.ini (see README)
[
    'current_season'        => $current_season,
    'tournaments_to_check'  => $tournaments_to_check,
    'tournament_start_time' => $tournament_start_time,
    'tournament_end_time'   => $tournament_end_time,
    'refresh_rate'          => $refresh_rate,
    'build_prod'            => $build_prod,
    'refresh_fuzz_min'      => $fuzz_refresh_min,
    'refresh_fuzz_max'      => $fuzz_refresh_max,

] = parse_ini_file("regieleki.ini");

$data_dir = __DIR__ . "/../data/majors/{$current_season}";

elog("Got " . count($tournaments_to_check) . " tours to check");

$tournament_settings = [];
$tour_tracker = [];

foreach ($tournaments_to_check as $tour => $remote_json) {
    $tournament_settings[$tour] = [
        'start' => time(),
        'end' => time() + 28800, // 8 hours
        'remote' => $remote_json,
        'local' => "{$data_dir}/{$tour}-standings.json",
        'process' => "{$current_season}:{$tour}",
    ];

    $tour_tracker[$tour] = true;
}

if (!empty($tournament_start_time)) {
    foreach ($tournament_start_time as $tour => $start_time) {
        if (!isset($tournament_settings[$tour])) {
            elog("Tour code '{$tour}' is missing from URL list. Typo? Exiting.");
            exit;
        }

        $start = (new DateTime($start_time))->getTimestamp();
        $tournament_settings[$tour]['start'] = $start;
        $tournament_settings[$tour]['end'] = $start + 28800;
        elog("[{$tour}] Initial delay set, will start collecting at " . date("Y-m-d H:i:s", $start));
    }
}

if (!empty($tournament_end_time)) {
    foreach ($tournament_end_time as $tour => $end_time) {
        if (!isset($tournament_settings[$tour])) {
            elog("Tour code '{$tour}' is missing from URL list. Typo? Exiting.");
            exit;
        }

        $end = (new DateTime($end_time))->getTimestamp();
        $tournament_settings[$tour]['end'] = $end;
        elog("[{$tour}] Scheduled to finish at " . date("Y-m-d H:i:s", $end));
    }
}

if ($build_prod) {
    elog("Will build as production (--prod)");
    $build_prod = '--prod';
} else {
    $build_prod = '';
}

elog("Setup done. Running...");

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

    $updates = json_decode(file_get_contents($updates_file), true);

    $process_cmd = [];
    foreach ($to_process as $tour => $process) {
        elog("[{$tour}] Downloading {$process['remote']}... ", '');

        try {
            $remote_data = make_request($process['remote']);
        } catch (Exception $e) {
            elog_cont($e->getMessage());
            continue;
        }

        elog_cont("Done!");
        $updates[$tour] = sha1($remote_data);

        if (file_put_contents($process['local'], $remote_data) === false){
            elog_cont("[{$tour}] Unable to write to '{$local_file}', skipping");
            continue;
        }

        $process_cmd[] = $process['process'];

        // small sleep between downloads
        sleep(mt_rand(1, 3));
    }

    elog("Writing updates file");
    file_put_contents($updates_file, json_encode($updates));

    if (!empty($process_cmd)) {
        elog("Building Reportworm... ", '');
        exec("python3 scripts/porygon.py {$build_prod} --process " . implode(',', $process_cmd));
        elog_cont("Done!");
    } else {
        elog("Nothing to process right now...");
    }

    $sleep_time = $refresh_rate + mt_rand($fuzz_refresh_min, $fuzz_refresh_max);
    elog("Sleeping for {$sleep_time} seconds...");
    sleep($sleep_time);
}

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
        CURLOPT_USERAGENT => 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
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
