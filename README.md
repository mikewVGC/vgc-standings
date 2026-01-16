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

Porygon is a simple command line script used to process standings data and rebuild the relevant pages. Right now you have to build all regionals for a season in one go:

```
python3 porygon.py 2026
```

This will process and build all events from the 2026 season. Standings JSON (which serve as the API) will be put in `public/data/{season}` and static HTML pages (which display all the data) will be put in `public/static` as `index.html`, `season.html`, and `tournament.html`.

You can create a production build by using the `--prod` flag. This will minify the CSS and Javascript and a few other optimizations.

### Why???

I know that there are tools that already do all of this stuff, and I would totally use them for a professional project. However, this is entirely done for fun in my free time, so I'm going to write some weird Python scripts and whatever else. Plus I don't really want to install node.

## Running Locally

There's a simple `docker-compose` file that will just download the latest nginx container. It can be started from the project root as usual: 

```
docker compose up -d
```

## Running Live

If for some reason you want a live version... I wouldn't do it! But if you really want to, make sure you have the necessary data outlined in the Setup section.

### Redis Cache

The final-ish step for running in production is to use the Redis cache instead of serving static files. You can use static files if you want, but Redis will be much faster. If you add `"cacheJson": true` to your `config.json` file then Porygon will automatically cache items in Redis.

Having this work requires both the Lua module as well as lua-resty-redis bundle. Using the included `nginx.conf` as a base, you can add a `content_by_lua_block`:

```
location ~ "^/api/v1/[0-9]{4}/[a-z-]+$" {
    default_type application/json;
    content_by_lua_block {
        local redis = require "resty.redis"
        local ngx_ctx = ngx.ctx

        local red, _ = redis:new()
        local ok, _ = red:connect("127.0.0.1", 6379)
        if not ok then
            return
        end

        local res, _ = red:get("vgc-standings::" + )

        if res != ngx.null then
            ngx.say(res)
        end

        return
    }

    rewrite "^/api/v1/([0-9]{4})/([a-z-]+)$" /data/$1/$2.json last;
}
```

This functionality is not supported in the docker version out of the box.
