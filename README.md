# Reportworm VGC Standings

Yet another VGC standings site!

## Info

This was basically built because I'm sad that Stalruth standings are gone. Is this better? No. But it's meant to be fast and have as much useful info as possible, which is what counts, I suppose.

## Setup / Development

It's a little annoying to set this up because I'm not including any of the data or images in this repo, so fair warning.

* You need Python! So install that if you don't have it already. You also need Go and optionally PHP. Sorry!
* If you plan on making production builds (I don't know why you'd want to), you also need Go.
* Clone this repo to anywhere you like.
* Grab relevant standings JSON from https://pokedata.ovh:
    * Place in `data/majors/{season}/{event-code}-standings.json`
    * The relevant `event-code` should be in the `{season}.json` file in `data/majors`.
* Create `{season}.json` in `data/majors` with this structure:
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
* Optionally grab the final standings order from RK9 (go to the event standings):
    * Paste the final standings into `data/majors/{season}/{event-code}-official.txt`
* Grab `pokedex.json` from Showdown: https://play.pokemonshowdown.com/data/
    * Place it in `data/common`
* Grab flags from https://flagicons.lipis.dev
    * Copy the 1x1 icons into `public/static/img/flags` (you'll have to create it).
* Retrieve teamsheet art from https://github.com/PokeAPI/sprites
    * This is a huge pain, but they go in `static/img/art`
    * Notably there's a lot of mapping (which can be seen in `formes.py`) due to different formes having different filenames. This part will be a big pain! I'm not including these files in this repo for my own sanity.

## Porygon -- Processing / Build Scripts

Porygon is a simple command line script used to process standings data and rebuild the relevant pages. The easiest thing is to just do a full development run:

```
python3 scripts/porygon.py
```

This will process and build all events found via `manifest.json`. Standings and usage JSON (which serve as the API) will be put in `public/data/{season}` and static HTML pages (which display all the data) will be put in `public/static` as `index.html`, `season.html`, and `tournament.html`.

Notably when processing regionals you will need to create the corresponding `season` directory in `public/data` as Porygon will not create them.

You can create a production build by using the `--prod` flag. This will minify the CSS and Javascript and a few other optimizations. You can also skip event processing and only rebuild the templates with the `--build-only` flag. You can also build a set of events with the `--process` argument. The format is a list of years and codes formatted as such: `2025:baltimore,2026:toronto`

### Why???

I know that there are tools that already do all of this stuff, and I would totally use them for a professional project. However, this is entirely done for fun in my free time, so I'm totally going to write some weird Python scripts or make a bizarre looking Vue app or whatever else. Also I'm really trying to avoid using the node ecosystem.

### Is This The Best Way To Do

The answer is probably no! The only thing I can recommend is not using this repo to learn anything.

## Running Locally

There's a simple `docker-compose` file that will just download the latest nginx container. It can be started from the project root as usual: 

```
docker compose up -d
```

Edit the templates/stylesheets/scripts and rebuild using Porygon to see your changes.

## Running In Production

I wouldn't do it if I were you, but if you have all the things you need from the Setup/Development steps above then it should work as is. This builds static files, so there's no need to run or compile anything. Just stick the files behind nginx with the same rewrite rules that are in the includes `nginx.conf` and you should be okay.

### config.json

In the root you need to create a simple `config.json` file with the following items:

```
{
    "monImgBase": "",
    "googleTag": ""
}
```

`googleTag` is optional (leave it blank if you don't want to use it) and contains your Google Analytics tag, but only the part *after* the `G-`. `monImgBase` is if you want to load the large Pokemon images from a CDN or object storage and should contain the full root URL of where you keep them. You can leave this blank and it will assume the images are in `public/static/img/art`.

Beyond that, make sure to use the `--prod` flag when you run Porygon as it will minify CSS and Javascript and make a few other things more optimal.

## Regieleki -- Live Updates

During a regional you might want to do live updates... why would you want to do this? I don't know. Create a file named `regieleki.ini` in the root with the following structure:

```
; ini file for Regieleki

current_season = 2026

tournaments_to_check['<regional_code>'] = "<pokedata json url>"

; add a start time to delay the initial start
start_time = ""

; refresh rate determines how often tournament standings will be downloaded
refresh_rate = 420

; minimum amount of fuzz to add to the refresh rate (in seconds)
refresh_fuzz_min = 10

; maximum amount of fuzz to add to the refresh rate (in seconds)
refresh_fuzz_max = 45

; run length is how long the script will run for before exiting
run_length = 360000

; production build
build_prod = 1
```

Get the regional's code from the JSON (`toronto`, `las-vegas`, `lille`, etc.) and URL of JSON data from Pokedata and put them into the correct places. You can leave the rest unchanged, and I honestly don't recommend lowering the refresh rate as it will do a fetch from Pokedata every 5 minutes. Once it fetches the data it will run Porygon to process the data and it should be updated when people reload.

This script is super simple and really non-robust. You can only run it one way:

```
php scripts/regieleki.php
```

I recommend using the values above as they seem pretty stable when I tried them. Note that this script will download files from Pokedata, so be considerate! I also recommend using the `start_time` setting as a way to reduce calls if you want to set this to run for a regional that might start at an inconvienant time for you due to time zones.

But, again, nobody should run this thing in production.
