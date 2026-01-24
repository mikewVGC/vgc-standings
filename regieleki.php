<?php

// This is a super rudimentary script that can be used to simulate "live" events. 
// What it actually does is just download a specified list of Pokedata json at
// an interval, checks for a change, and then runs the process scripts. This
// whole thing is fairly manual, so the easiest way to run this will be via screen
// or tmux or something similar.

// And yes, I did write PHP on purpose!

if (!file_exists("regieleki.ini")) {
    echo "regieleki.ini not found, exiting\n";
    exit;
}

// parse regieleki.ini (see README)
[
    'current_season'       => $current_season,
    'tournaments_to_check' => $tournaments_to_check,
    'refresh_rate'         => $refresh_rate,
    'run_length'           => $run_length,
    'build_prod'           => $build_prod,
    'refresh_fuzz_min'     => $fuzz_refresh_min,
    'refresh_fuzz_max'     => $fuzz_refresh_max,

] = parse_ini_file("regieleki.ini");

$data_dir = __DIR__ . "/data/majors/{$current_season}";

echo "[ELEKI] Regieleki starting! Got " . count($tournaments_to_check) . " tours to check\n";

$finish_time = time() + $run_length;

echo "[ELEKI] Scheduled to finish at " . date("Y-m-d H:i:s", $finish_time) . "\n";

if ($build_prod) {
    echo "[ELEKI] Will build as production (--prod)\n";
    $build_prod = '--prod';
} else {
    $build_prod = '';
}

while (1) {

    echo "[ELEKI] Running...\n";

    $to_process = [];
    foreach ($tournaments_to_check as $tour => $remote_json) {
        $local_file = "{$data_dir}/{$tour}-standings.json";

        echo "[ELEKI] [{$tour}] Downloading {$remote_json}... ";

        try {
            $remote_data = make_request($remote_json);
        } catch (Exception $e) {
            echo $e->getMessage() . "\n";
            continue;
        }

        echo "Done!\n";

        if (file_put_contents($local_file, $remote_data) === false){
            echo "[{$tour}] Unable to write to '{$local_file}', skipping\n";
            continue;
        }

        $to_process[] = "{$current_season}:{$tour}";

        // small sleep between downloads
        sleep(mt_rand(1, 3));
    }

    if (!empty($to_process)) {
        echo "[ELEKI] Building Reportworm... ";
        exec("python3 scripts/porygon.py {$build_prod} --process " . implode(',', $to_process));
        echo "Done!\n";
    } else {
        echo "[ELEKI] Nothing to process right now...\n";
    }

    if (time() >= $finish_time) {
        echo "[ELEKI] Scheduled finish time reached! Exiting.\n";
        break;
    }

    echo "[ELEKI] Sleeping...\n";
    sleep($refresh_rate + mt_rand($fuzz_refresh_min, $fuzz_refresh_max));
}

echo "[ELEKI] All done! Thanks for running!\n";
exit;

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
