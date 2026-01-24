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

// parse regieleki.ini
[
    'current_season'       => $current_season,
    'tournaments_to_check' => $tournaments_to_check,
    'refresh_rate'         => $refresh_rate,
    'run_length'           => $run_length,
    'build_prod'           => $build_prod,

] = parse_ini_file("regieleki.ini");

$data_dir = __DIR__ . "/data/majors/{$current_season}";

echo "[ELEKI] Regieleki starting! Got " . count($tournaments_to_check) . " tours to check\n";

$finish_time = time() + $run_length;

echo "[ELEKI] Scheduled to finish at " . date("Y-m-d H:i:s", $finish_time) . "\n";

if ($build_prod) {
    echo "[ELEKI] Will make production build";
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

        $remote_data = file_get_contents($remote_json);
        if ($remote_data === false) {
            echo "Unable to download! Skipping\n";
            continue;
        }

        echo "Done!\n";

        if (file_put_contents($local_file, $remote_data) === false){
            echo "[{$tour}] Unable to write to '{$local_file}', skipping\n";
            continue;
        }

        $to_process[] = "{$current_season}:{$tour}";
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
    sleep($refresh_rate);
}

echo "[ELEKI] All done! Thanks for running!\n";
exit;
