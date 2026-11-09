
## Processing (partial) rewrite

New team format example. All other data stays as it is currently

```json
{
  "standings": {
    "event": {
      // stays the same
    },
    "javier-varela": {
      // non-team data (truncated) stays the same
      "team": [
        {
          "name": "Gholdengo",
          "code": "gholdengo",
          "alt": {}, // empty if no alt form
          "dex": 1000,
          "types": [
            "steel",
            "ghost"
          ],
          "tera": null,
          "ability": "Good as Gold",
          "nature": "Modest",
          "item": "Life Orb",
          "itemcode": "lifeorb",
          "moves": [
            {
              "name": "Shadow Ball",
              "type": "ghost"
            },
            {
              "name": "Make It Rain",
              "type": "steel"
            },
            {
              "name": "Nasty Plot",
              "type": "dark"
            },
            {
              "name": "Protect",
              "type": "normal"
            }
          ]
        },
        {
          "name": "Tyranitar",
          "code": "tyranitar",
          "alt": {
            "name": "Tyranitar-Mega",
            "code": "tyranitarmega",
            "dex": 10049,
            "types": [
                "rock",
                "dark"
            ],
            "ability": "Sand Stream",
            "type": "mega"
          },
          "dex": 10049,
          "types": [
            "rock",
            "dark"
          ],
          "tera": null,
          "ability": "Sand Stream",
          "nature": "Jolly",
          "item": "Tyranitarite",
          "itemcode": "tyranitarite",
          "moves": [
            {
              "name": "Rock Slide",
              "type": "rock"
            },
            {
              "name": "Knock Off",
              "type": "dark"
            },
            {
              "name": "Dragon Dance",
              "type": "dragon"
            },
            {
              "name": "Protect",
              "type": "normal"
            }
          ]
        },
        {
          "name": "Staraptor",
          "code": "staraptor",
          "alt": {
            "name": "Staraptor-Mega",
            "code": "staraptormega",
            "dex": 10308, // mega dex/image
            "ability": "Contrary",
            "types": [
              "flying",
              "fighting"
            ],
            "type": "mega"
          },
          "dex": 10308, // regular dex/image
          "types": [
            "normal",
            "flying"
          ],
          "tera": null,
          "ability": "Intimidate",
          "nature": "Jolly",
          "item": "Staraptite",
          "itemcode": "staraptite",
          "moves": [
            {
              "name": "Brave Bird",
              "type": "flying"
            },
            {
              "name": "Close Combat",
              "type": "fighting"
            },
            {
              "name": "Tailwind",
              "type": "flying"
            },
            {
              "name": "Protect",
              "type": "normal"
            }
          ]
        },
        // ...
      ],
      "rounds": [
        // stays the same
      ]
```
