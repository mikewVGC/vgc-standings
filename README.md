# Reportworm VGC Standings

A site for viewing standings, pairings, teamsheets, and some stats for major VGC events like regionals and international championships.

## Info

This was basically built because I was (and still am) sad that Stalruth standings are gone. Is this better? No, probably not. But, it's meant to be fairly fast and have as much useful info as possible, which is what counts.

## Now What?

There's not too much you can get from this repo unless you want to know how everything works. The rest of this readme will detail how to set everything up, which you will likely find to be a terrible pain, if not borderline impossible. Also if you came here to learn how to program or build a website, I'm really sorry. I wouldn't really recommend using this to learn much of anything!

## Setup / Development

This is honestly not worth your time because there's a lot of bespoke data that goes into making this run. In addition to data from Pokedata, I've written scrapers for both RK9 and playlatam which I use for edge cases or missing data. I won't be releasing any of those things for a variety of reasons, so you're going to have to be a self starter. I've also hand edited some of the data for a number of reasons.

In the meantime you can poke around this repo, if you want. 

### Requirements

Python mostly, but also Go and PHP in the event you plan to run a live version (but, again, don't).

### Basic Setup

* Clone this repo to wherever you like.
* In order for the processing scripts know which seasons to look for, and to set the currently active season, create a file named `mainfest.json` in `data/majors` with the following structure:
```json
{
    "seasons": [
        2024,
        2025,
        2026
    ],
    "current": 2026
}
```
* Create `{season}.json` in `data/majors` with this structure (you can add as many events as you like):
```json
[
    {
        "name": "Frankfurt Regional",
        "code": "frankfurt",
        "region": "Europe",
        "country": "Germany",
        "flag": "de",
        "start": "2025-09-13",
        "end": "2025-09-14",
        "game": "Scarlet & Violet",
        "format": "Regulation H"
    }
]
```
* Grab relevant standings JSON from https://pokedata.ovh:
    * Place each one in `data/majors/{season}/{event-code}-standings.json`
    * The relevant `event-code` should match the one in the corresponding `{season}.json` file in `data/majors`.
* Optionally grab the final standings order RK9 (go to the pairings and click the "Standings" tab):
    * Paste the final standings into `data/majors/{season}/{event-code}-official.txt`
* Grab `pokedex.json` from Showdown: https://play.pokemonshowdown.com/data/
    * Place it in `data/common`
* Grab flags from https://flagicons.lipis.dev
    * Copy the 1x1 icons into `public/static/img/flags` (you'll have to create it).
* Retrieve teamsheet/pokepaste art from https://github.com/PokeAPI/sprites
    * This is a huge pain, but they go in `static/img/art`
    * Notably there's a lot of mapping (which can be seen in `formes.py`) due to different formes having different filenames. This part will be a big pain! I'm not including these files in this repo for my own sanity.

## Porygon -- Processing / Build Scripts

Porygon is a simple command line script used to process standings data and rebuild the relevant pages. The easiest thing is to just do a full development run:

```
python3 scripts/porygon.py
```

This will process and build all events found via `manifest.json`. Standings and usage JSON (which serve as the API) will be put in `public/data/{season}` and static HTML pages (which display all the data) will be put in `public/static` as `index.html`, `season.html`, and `tournament.html`.

Notably when first processing regionals you will need to create the corresponding `{season}` directory in `public/data` as Porygon will not create them (I might fix this some day).

You can create a production build by using the `--prod` flag. This will minify the CSS and Javascript and a few other optimizations. You can skip event processing and only rebuild the templates with the `--build-only` flag. If you only want to build a smaller set of events you can use the `--process` argument. The format is a list of one or more years and codes separated by a comma formatted as such: `2025:baltimore,2026:toronto`. You can also process a full season with: `2025:*`.

### Ruff Formatting

I've added ruff to the repo to keep myself honest, at least on the Python side. You should run it on the `scripts/` directory and fix whatever it says to fix:

```
uv run ruff check scripts/
```

### Why???

I know that there are tools that already do all of this stuff, and I would totally use them for a professional project. However, this is entirely done for fun in my free time, so I'm absolutely going to write some weird Python scripts or make a bizarre looking Vue app or whatever else. Also, I'm really trying to avoid using the node ecosystem for this project. Or just in general, I suppose.

### Is This The Best Way To Do... Any Of This?

The answer is probably no. But it's fun!

## Running Locally

There's a simple `docker-compose` file that will just download the latest nginx container. It can be started from the project root as usual: 

```
docker compose up -d
```

Once you edit the templates/stylesheets/scripts you have to rebuild using Porygon to see your changes.

## Running In Production

I wouldn't do it if I were you, but if you have all the things you need from the Setup/Development steps above then it should work? The site is static files, so there's no need to run or compile anything. Just stick the files behind nginx with the same rewrite rules that are in the includes `nginx.conf` and you should be okay.

### config.json

In the root you need to create a simple `config.json` file with the following items:

```
{
    "monImgBase": "",
    "googleTag": ""
}
```

`googleTag` is optional (leave it blank if you don't want to use it) and contains your Google Analytics tag, but only the part *after* the `G-`. `monImgBase` is if you want to load the large Pokemon images from a CDN or object storage and should contain the full root URL of their location. You can leave this blank and it will assume the images are in `public/static/img/art`.

Beyond that, make sure to use the `--prod` flag when you run Porygon.

## Regieleki -- Live Updates

During a regional you might want to do live updates... why would you want to do this? I don't know! Create a file named `regieleki.ini` in the root with the following structure:

```
; ini file for Regieleki

current_season = 2026

; list of tournament data URLs to check (should be pokedata)
tournaments_to_check['<regional_code>'] = "<pokedata json URL>"

; add a start time for when we should start collecting data
tournament_start_time['<regional_code>'] = "2026-02-07 8:00am Australia/Sydney"

; add an end time to stop collecting data
tournament_end_time['<regional_code>'] = "2026-02-07 6:00pm Australia/Sydney"

; refresh rate determines how often tournament standings will be downloaded (in seconds)
refresh_rate = 420

; minimum amount of fuzz to add to the refresh rate (in seconds)
refresh_fuzz_min = 10

; maximum amount of fuzz to add to the refresh rate (in seconds)
refresh_fuzz_max = 45

; if we should do a production build or not
build_prod = 0
```

Get the regional's code from the JSON (`toronto`, `las-vegas`, `lille`, etc.) and URL of JSON data from Pokedata and put them into the correct places. You can leave the rest unchanged, and I honestly don't recommend lowering the refresh rate as it will do a fetch from Pokedata every 7 minutes. Once it fetches the data it will run Porygon to process the data and it should be updated when people reload.

This script is super simple and really non-robust. You can only run it one way:

```
php scripts/regieleki.php
```

I recommend using the values above as they seem pretty stable when I tried them. Note that this script will download files from Pokedata, so be considerate! Using `tournament_start_time` is not required but I really recommend if a regional is starting during off hours for you so you're not trying to download data while nothing is happening.

But, again, nobody should run this thing in production.

## License

Reportworm Standings is licensed with the BSD license.
