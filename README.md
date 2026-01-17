# Reportworm VGC Standings

Yet another VGC standings site!

## Info

This was basically built because I'm sad that Stalruth standings are gone. Is this better? No. But it's meant to be fast and have as much useful info as possible, which is what counts, I suppose.

## Setup / Development

It's a little annoying to set this up because I'm not including any of the data or images in this repo, so fair warning.

* You need Python! So install that if you don't have it already.
* If you plan on making production builds (I don't know why you'd want to), you also need Go.
* Clone this repo to anywhere you like.
* Grab relevant standings JSON from https://pokedata.ovh:
    * Place in `data/majors/{season}/{event-code}-standings.json`
    * The relevant `event-code` should be in the `{season}.json` file in `data/majors`.
* Optionally grab the final standings from RK9 (go to the event standings):
    * Paste the final standings into `data/majors/{season}/{event-code}-official.txt`
* Grab `pokedex.json` from Showdown: https://play.pokemonshowdown.com/data/
    * Place it in `data/common`
* Retrieve teamsheet art from https://github.com/PokeAPI/sprites
    * This is a huge pain, but they go in `static/img/art`
    * Notably there's a lot of mapping (which can be seen in `formes.py`) due to different formes having different filenames. This part will be a big pain! I'm not including these files in the repo just to avoid any number of issues.

## Processing / Build Scripts (Porygon)

Porygon is a simple command line script used to process standings data and rebuild the relevant pages. The easiest thing is to just do a full development run:

```
python3 scripts/porygon.py
```

This will process and build all events found via `manifest.json`. Standings JSON (which serve as the API) will be put in `public/data/{season}` and static HTML pages (which display all the data) will be put in `public/static` as `index.html`, `season.html`, and `tournament.html`.

You can create a production build by using the `--prod` flag. This will minify the CSS and Javascript and a few other optimizations. You can also skip event processing and only rebuild the templates with the `--build-only` flag.

### Why???

I know that there are tools that already do all of this stuff, and I would totally use them for a professional project. However, this is entirely done for fun in my free time, so I'm going to write some weird Python scripts and whatever else. Plus I don't really want to install node.

## Running Locally

There's a simple `docker-compose` file that will just download the latest nginx container. It can be started from the project root as usual: 

```
docker compose up -d
```

## Running Live

If for some reason you want a live version... I wouldn't do it! But if you really want to, make sure you have the necessary data outlined in the Setup section.
