export default {
    data() {
        return {
            season: '',
            major: '',
            eventInfo: {},

            currentRoute: '/',
            currentView: 'loading',

            loaded: false,
            standings: {},
            countryStats: {},
            usage: [],

            sorts: {
                usage: { column: 'total', dir: 1 },
            },

            spriteCoords: {},
            countryCodes: {},

            monImgBase: '',

            nav: [],
        }
    },
    computed: {
        currentProps() {
            let route = (this.currentRoute.slice(1) || '/');
            let chunks = [];
            let secondary = "";

            if (!this.loaded) {
                return {};
            }

            this.currentView = 'standings-main';

            if (route != '/') {
                chunks = route.split('/');
                switch (chunks[1]) {
                    case 'player':
                        this.currentView = 'player';
                        break;
                    case 'pairings':
                        this.currentView = 'pairings';
                        break;
                    case 'countries':
                        this.currentView = 'country-stats';
                        break;
                    case 'country':
                        this.currentView = 'country';
                        break;
                    case 'usage':
                        this.currentView = 'usage';
                        break;
                    case 'mon':
                        this.currentView = 'mon';
                        break;
                }

                secondary = chunks[2] || "";
            }

            switch (this.currentView) {
                case 'loading':
                    return {};

                case 'standings-main':
                    document.title = `${this.eventInfo.name} Standings -- Reportworm Standings`;

                    this.nav = [{
                        text: `${this.season} Season`,
                        link: `/${this.season}`,
                        active: false,
                    }, {
                        text: `${this.eventInfo.name}`,
                        link: `/${this.season}/${this.eventInfo.code}#`,
                        active: true,
                    }];

                    return {
                        standings: this.standings,
                        season: this.season,
                        eventInfo: this.eventInfo,
                    };

                case 'player':
                    let player = this.standings[secondary] || undefined;
                    if (!player) {
                        document.location = `/${this.season}/${this.major}`;
                        return {};
                    }

                    let opps = {};
                    document.title = `${player.name} -- ${this.eventInfo.name} Standings -- Reportworm Standings`;
                    if (player?.rounds) {
                        for (let i = 0; i < player.rounds.length; i++) {
                            let oppCode = player.rounds[i].opp;
                            opps[oppCode] = this.standings[oppCode] || {};

                            if (player.rounds[i].bye == 1) {
                                opps[oppCode].name = "bye";
                            }
                        }

                        if (!player.groupedRounds) {
                            let phases = [
                                { phase: 3, rounds: player.rounds.filter(g => g.phase == 3) },
                                { phase: 2, rounds: player.rounds.filter(g => g.phase == 2) },
                                { phase: 1, rounds: player.rounds.filter(g => g.phase == 1) },
                            ];

                            player.groupedRounds = phases.filter(p => p.rounds.length > 0);
                        }
                    }

                    this.nav = [{
                        text: `${this.season} Season`,
                        link: `/${this.season}`,
                        active: false,
                    }, {
                        text: `${this.eventInfo.name}`,
                        link: `/${this.season}/${this.major}#`,
                        active: false,
                    }, {
                        text: `${player.name}`,
                        link: `/${this.season}/${this.major}#/player/${player.code}`,
                        active: true,
                    }];

                    return {
                        player: player,
                        opponents: opps,
                        monImgBase: this.monImgBase,
                        eventInfo: this.eventInfo,
                    };

                case 'pairings':
                    let allRounds = this.getAllRounds();
                    if (!secondary) {
                        secondary = allRounds[allRounds.length - 1].num;
                    }

                    let pairings = this.getPairings(secondary);
                    let roundName = secondary;
                    let roundNum = secondary;
                    if (pairings.length) {
                        roundName = pairings[0].rname;
                        roundNum = pairings[0].round;
                    }

                    if (roundName == roundNum) {
                        roundName = `Round ${roundNum}`;
                    }

                    this.nav = [{
                        text: `${this.season} Season`,
                        link: `/${this.season}`,
                        active: false,
                    }, {
                        text: `${this.eventInfo.name}`,
                        link: `/${this.season}/${this.major}#`,
                        active: false,
                    }, {
                        text: `${roundName} Pairings`,
                        link: `/${this.season}/${this.major}#/pairings/${secondary}`,
                        active: true,
                    }];

                    return {
                        eventInfo: this.eventInfo,
                        pairings: pairings,
                        round: { name: roundName, num: roundNum },
                        allRounds: allRounds,
                    };

                case 'country-stats':
                    document.title = `Country Stats -- ${this.eventInfo.name} Standings -- Reportworm Standings`;

                    this.nav = [{
                        text: `${this.season} Season`,
                        link: `/${this.season}`,
                        active: false,
                    }, {
                        text: `${this.eventInfo.name}`,
                        link: `/${this.season}/${this.eventInfo.code}#`,
                        active: false,
                    }, {
                        text: "Country Stats",
                        link: `/${this.season}/${this.major}#/countries`,
                        active: true,
                    }];

                    return {
                        eventInfo: this.eventInfo,
                        countryStats: this.countryStats,
                        standings: this.standings,
                        countryCodes: this.countryCodes,
                    };

                case 'country':
                    let country = this.countryCodes[secondary.toUpperCase()] || "";
                    if (!country) {
                        document.location = `/${this.season}/${this.major}/#countries`;
                        return {};
                    }

                    document.title = `${country} Players -- Country Stats -- ${this.eventInfo.name} Standings -- Reportworm Standings`;

                    this.nav = [{
                        text: `${this.season} Season`,
                        link: `/${this.season}`,
                        active: false,
                    }, {
                        text: `${this.eventInfo.name}`,
                        link: `/${this.season}/${this.eventInfo.code}#`,
                        active: false,
                    }, {
                        text: "Country Stats",
                        link: `/${this.season}/${this.major}#/countries`,
                        active: false,
                    }, {
                        text: `${country}`,
                        link: `/${this.season}/${this.major}#/country/${secondary}`,
                        active: true,
                    }];

                    return {
                        eventInfo: this.eventInfo,
                        countryStats: this.countryStats.find(c => c.country == secondary),
                        standings: this.standings,
                        countryCodes: this.countryCodes,
                        country: secondary,
                    };

                case 'usage':
                    document.title = `Usage Stats -- ${this.eventInfo.name} Standings -- Reportworm Standings`;

                    this.nav = [{
                        text: `${this.season} Season`,
                        link: `/${this.season}`,
                        active: false,
                    }, {
                        text: `${this.eventInfo.name}`,
                        link: `/${this.season}/${this.eventInfo.code}#`,
                        active: false,
                    }, {
                        text: "Usage Stats",
                        link: `/${this.season}/${this.major}#/usage`,
                        active: true,
                    }];

                    return {
                        eventInfo: this.eventInfo,
                        usage: this.usage,
                    };

                case 'mon':
                    let mon = this.usage.find((m) => m.code == secondary);

                    if (!mon) {
                        document.location = `/${this.season}/${this.major}#/usage`;
                        return {};
                    }

                    document.title = `${mon.name} -- Usage Stats -- ${this.eventInfo.name} Standings -- Reportworm Standings`;

                    this.nav = [{
                        text: `${this.season} Season`,
                        link: `/${this.season}`,
                        active: false,
                    }, {
                        text: `${this.eventInfo.name}`,
                        link: `/${this.season}/${this.eventInfo.code}#`,
                        active: false,
                    }, {
                        text: "Usage Stats",
                        link: `/${this.season}/${this.major}#/usage`,
                        active: false,
                    }, {
                        text: `${mon.name}`,
                        link: `/${this.season}/${this.major}#/mon/${mon.code}`,
                        active: true,
                    }];

                    return {
                        eventInfo: this.eventInfo,
                        mon: mon,
                        monImgBase: this.monImgBase,
                        standings: this.standings,
                    };
            }

            return {};
        },
    },
    methods: {
        init() {
            window.addEventListener('hashchange', () => {
                this.currentRoute = window.location.hash;
            });

            const chips = window.location.pathname.split('/');

            if (chips.length != 3) {
                window.location = '/';
            }

            this.setMajor(chips[1], chips[2]);

            this.currentRoute = window.location.hash;
        },

        setMajor(season, name) {
            this.season = season;
            this.major = name;

            this.getRegional(() => {
                this.getUsage();
            });
        },

        getRegional(cb) {
            fetch(`/api/v1/${this.season}/${this.major}`, {
                method: "GET",
                headers: { "Content-type": "application/json" },
            }).then((r) => {
                if (!r.ok) {
                    window.location = '/';
                }

                return r.json();
            }).then((d) => {
                this.standings = d.standings;
                this.eventInfo = d.event;

                // compile country stats
                for (const [playerCode, player ] of Object.entries(this.standings)) {
                    let country = player.country;
                    if (!country) {
                        continue;
                    }
                    if (!(country in this.countryStats)) {
                        this.countryStats[country] = {
                            country: country,
                            players: [],
                            phase2: 0,
                            cut: 0,
                            topPlayer: { place: 9999 },
                        };
                    }
                    if (player.place < this.countryStats[country].topPlayer.place) {
                        this.countryStats[country].topPlayer = {
                            place: player.place,
                            code: playerCode,
                        };
                    }

                    this.countryStats[country].players.push(playerCode);
                    this.countryStats[country].cut += player.cut;
                    this.countryStats[country].phase2 += player.p2;
                }

                this.countryStats = Object.values(this.countryStats);
                this.countryStats.sort((a, b) => a.players.length < b.players.length);

                cb();
            });
        },

        getUsage() {
            fetch(`/api/v1/${this.season}/${this.major}/usage`, {
                method: "GET",
                headers: { "Content-type": "application/json" },
            }).then((r) => {
                if (!r.ok) {
                    window.location = `/${this.season}/${this.major}`;
                }
                return r.json();
            }).then((d) => {
                this.usage = d;

                this.usage.forEach(usage => {
                    usage.counts['phase2Conversion'] = usage.counts.phase2 / usage.counts.total;
                    usage.counts['cutConversion'] = usage.counts.cut / usage.counts.phase2;
                });

                this.loaded = true;
            });
        },

        getPairings(round) {
            let pairings = [];
            let checked = {};

            for (const [playerCode, player ] of Object.entries(this.standings)) {
                if (checked[playerCode] || !playerCode) {
                    continue;
                }

                let match = player.rounds.find(m => m.round == round);
                if (!match) {
                    continue;
                }

                let opp = match?.opp || "";
                if (opp) {
                    checked[opp] = true;
                }
                checked[playerCode] = true;

                let winner = "";
                if (match.res == 'W') {
                    winner = playerCode;
                } else if (match.res == 'L') {
                    winner = opp;
                }

                if (!winner && !opp && !match.late && !match.bye) {
                    continue;
                }

                pairings.push({
                    'round': match.round,
                    'rname': match.rname,
                    'player': this.standings[playerCode],
                    'opp': (!match.bye && !match.late && opp) ? this.standings[opp] : false,
                    'winner': winner,
                    'table': match.tbl,
                    'other': match.late ? 'Late' : (match.bye ? 'Bye' : ''),
                });
            }

            pairings.sort((a, b) => a.table > b.table);

            return pairings;
        },

        getAllRounds() {
            let rounds = [];
            // the first place player should have played in all possible rounds
            for (const [playerCode, player ] of Object.entries(this.standings)) {
                for (let i = 0; i < player.rounds.length; i++) {
                    rounds.push({
                        name: player.rounds[i].rname,
                        num: player.rounds[i].round,
                    });
                }
                break;
            }

            rounds.reverse();

            return rounds;
        },

        sortUsage(column) {
            let sortInfo = this.sorts.usage;
            if (column == sortInfo.column) {
                sortInfo.dir *= -1;
            } else {
                sortInfo.column = column;
                sortInfo.dir = 1;
            }

            this.usage.sort((a, b) => {
                if (column in a.counts) {
                    a = a.counts;
                    b = b.counts;
                }
                if (a[column] < b[column]) {
                    return sortInfo.dir;
                } else if (a[column] > b[column]) {
                    return -sortInfo.dir;
                }
                return 0;
            });
        },

        getSortedClass(column) {
            const sortInfo = this.sorts.usage;
            if (sortInfo.column == column) {
                if (sortInfo.dir == -1) {
                    return "up";
                }
                if (sortInfo.dir == 1) {
                    return "down";
                }
            }
            return "";
        },

        setMonImgBase(base) {
            this.monImgBase = base;
        },

        copyToClipboard(value) {
            navigator.clipboard.writeText(value);
        },

        setSpriteCoords(data) {
            this.spriteCoords = data;
        },

        getSpritePos(name) {
            let pos = this.spriteCoords[name] || [ 0, 0 ];
            return `-${pos[0]}px -${pos[1]}px`;
        },

        getPct(dec, precision) {
            if (isNaN(dec)) {
                return "-";
            }
            if (precision == undefined) {
                precision = 5;
            }
            return (dec * 100).toPrecision(dec >= 1 ? precision : dec < .1 ? precision - 2 : precision - 1) + "%";
        },

        setCountryCodes(data) {
            this.countryCodes = data;
        },
    },
    components: {
        'loading': {
            template: '#loading-template',
        },
        'standings-main': {
            template: '#standings-main-template',
            props: [ 'standings', 'eventInfo', 'season' ],
            methods: {
                getSpritePos(name) {
                    return this.$parent.getSpritePos(name);
                },
                getPct(dec, precision) {
                    return this.$parent.getPct(dec, precision)
                },
            },
        },
        'player': {
            template: '#player-template',
            props: [ 'opponents', 'player', 'monImgBase', 'eventInfo' ],
            methods: {
                getSpritePos(name) {
                    return this.$parent.getSpritePos(name);
                },
                getPct(dec, precision) {
                    return this.$parent.getPct(dec, precision)
                },
                getPhaseString(phase) {
                    if (phase == 3) {
                        return 'Top Cut';
                    }
                    return `Phase ${phase}`;
                },
                teamCopy() {
                    this.$parent.copyToClipboard(
                        document.getElementById('team').innerText
                    );
                
                    document.getElementById('team-copy').innerText = "Copied!";
                    setTimeout(() => {
                        document.getElementById('team-copy').innerText = "Copy";
                    }, 2000);
                },
            },
        },
        'pairings': {
            template: '#pairings-template',
            props: [ 'eventInfo', 'pairings', 'allRounds', 'round' ],
            methods: {
                pairingWinClass(pairing, player) {
                    if (!player) {
                        return '';
                    }
                    if (!pairing.winner) {
                        if (pairing.other == 'Late') {
                            return 'L';
                        }
                        if (pairing.other == 'Bye') {
                            return 'W';
                        }
                        return '';
                    }
                    if (pairing.winner == player) {
                        return 'W';
                    }
                    return 'L';
                },
                getRecordThroughRound(player, round) {
                    let wins = 0;
                    let loss = 0;

                    for (let x = 0; x < round; x++) {
                        if (!player.rounds[x]) {
                            continue;
                        }
                        if (player.rounds[x].res == 'W') {
                            wins++;
                        }
                        if (player.rounds[x].res == 'L') {
                            loss++;
                        }
                    }

                    return `${wins} - ${loss}`;
                },
            },
        },
        'country-stats': {
            template: '#country-stats-template',
            props: [ 'countryStats', 'standings', 'eventInfo', 'countryCodes' ],
            methods: {
                getCountryName(code) {
                    if (!code) {
                        return "";
                    }
                    return this.countryCodes[code.toUpperCase()] || "";
                },
            },
        },
        'country': {
            template: '#country-template',
            props: [ 'countryStats', 'standings', 'eventInfo', 'countryCodes', 'country' ],
            methods: {
                getCountryName(code) {
                    if (!code) {
                        return "";
                    }
                    return this.countryCodes[code.toUpperCase()] || "";
                },
                getSpritePos(name) {
                    return this.$parent.getSpritePos(name);
                },
                getPct(dec, precision) {
                    return this.$parent.getPct(dec, precision);
                },
            },
        },
        'usage': {
            template: '#usage-template',
            props: [ 'usage', 'eventInfo' ],
            methods: {
                getSpritePos(name) {
                    return this.$parent.getSpritePos(name);
                },
                getPct(dec, precision) {
                    return this.$parent.getPct(dec, precision);
                },
                sortUsage(column) {
                    return this.$parent.sortUsage(column);
                },
                getSortedClass(column) {
                    return this.$parent.getSortedClass(column);
                },
            }
        },
        'mon': {
            template: '#mon-template',
            props: [ 'monImgBase', 'eventInfo', 'mon', 'standings' ],
            methods: {
                getPct(dec, precision) {
                    return this.$parent.getPct(dec, precision)
                },
                getSpritePos(name) {
                    return this.$parent.getSpritePos(name);
                },
            },
        },
    },
    
};
