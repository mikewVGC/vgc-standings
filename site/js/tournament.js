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
            allRounds: [],

            filters: {
                items: [],
                teras: [],
            },

            filteredPlayers: [],

            sorts: {
                usage: { column: 'total', dir: 1 },
            },

            opponentsCompact: false,

            spriteCoords: {},
            hdItemCoords: {},
            countryCodes: {},

            monImgBase: '',

            nav: [],

            liveUpdates: '',
        }
    },
    computed: {
        currentProps() {
            let route = (this.currentRoute || '/');
            let chunks = [];
            let secondary = "";

            if (!this.loaded) {
                return {};
            }

            this.currentView = 'standings-main';

            if (route != '/') {
                chunks = route.split('/');
                switch (chunks[0]) {
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

                secondary = chunks[1] || "";
            }

            switch (this.currentView) {
                case 'loading':
                    return {};

                case 'standings-main':
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

                    return {
                        season: this.season,
                        player: player,
                        opponents: opps,
                        monImgBase: this.monImgBase,
                        eventInfo: this.eventInfo,
                    };

                case 'pairings':
                    if (!secondary) {
                        if (this.allRounds.length) {
                            secondary = this.allRounds[this.allRounds.length - 1].num;
                        } else {
                            secondary = 1;
                        }
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

                    return {
                        season: this.season,
                        eventInfo: this.eventInfo,
                        pairings: pairings,
                        standings: this.standings,
                        round: { name: roundName, num: roundNum },
                        allRounds: this.allRounds,
                    };

                case 'country-stats':
                    return {
                        season: this.season,
                        eventInfo: this.eventInfo,
                        countryStats: this.countryStats,
                        standings: this.standings,
                        countryCodes: this.countryCodes,
                    };

                case 'country':
                    let country = this.countryCodes[secondary.toUpperCase()] || "";
                    if (!country) {
                        document.location = `/${this.season}/${this.major}/countries`;
                        return {};
                    }

                    return {
                        season: this.season,
                        eventInfo: this.eventInfo,
                        countryStats: this.countryStats.find(c => c.country == secondary),
                        standings: this.standings,
                        countryCodes: this.countryCodes,
                        country: country,
                        countryCode: secondary,
                    };

                case 'usage':
                    return {
                        season: this.season,
                        eventInfo: this.eventInfo,
                        usage: this.usage,
                    };

                case 'mon':
                    let mon = this.usage.find((m) => m.code == secondary);

                    if (!mon) {
                        document.location = `/${this.season}/${this.major}/usage`;
                        return {};
                    }

                    return {
                        season: this.season,
                        eventInfo: this.eventInfo,
                        mon: mon,
                        monImgBase: this.monImgBase,
                        standings: this.standings,
                        filteredPlayers: this.filteredPlayers,
                    };
            }

            return {};
        },
    },
    methods: {
        init() {
            if (window.location.hash.length > 1) {
                window.location = `${window.location.pathname}${window.location.hash.slice(1)}`;
                return;
            }

            window.addEventListener('click', (e) => {
                let targetEl = e.target;
                if (targetEl && e.target.tagName === 'A') {
                    if ('pass' in targetEl.dataset && targetEl.dataset.pass == 1) {
                        return;
                    }

                    e.preventDefault();
                    const url = e.target.getAttribute('href');
                    history.pushState({ page: url }, null, url);

                    const chips = window.location.pathname.split('/');
                    this.currentRoute = chips.slice(3).join('/');
                }
            });

            window.addEventListener('popstate', (e) => {
                if (e.state) {
                    const chips = e.state.page.split('/');
                    this.currentRoute = chips.slice(3).join('/');
                }
            });

            const chips = window.location.pathname.split('/');
            history.pushState({ page: window.location.pathname }, null, window.location.pathname);
            this.currentRoute = chips.slice(3).join('/');

            this.setMajor(chips[1], chips[2]);
        },

        setNav(navData) {
            this.nav = navData;
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

                this.getAllRounds();

                this.countryStats = {};

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

                // this should probably be done via websockets, but
                // this site is all static files, so it's just
                // going to be the old dumb polling strategy
                if (this.eventInfo.in_progress) {
                    setTimeout(this.checkForUpdates, 120 * 1000);
                }

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

        checkForUpdates() {
            if (!this.eventInfo.in_progress) {
                return;
            }

            fetch(`/api/v1/updates`, {
                method: "GET",
                headers: { "Content-type": "application/json" },
            }).then((r) => {
                if (!r.ok) {
                    return false;
                }
                return r.json();
            }).then((d) => {
                if (!d) {
                    return;
                }

                if (d[this.major]) {
                    if (this.liveUpdates != d[this.major]) {
                        this.getRegional(() => {
                            this.getUsage();
                        });
                        this.liveUpdates = d[this.major];
                    }
                }
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
                    'player': playerCode,
                    'opp': (!match.bye && !match.late && opp) ? opp : false,
                    'winner': winner,
                    'table': match.tbl,
                    'other': match.late ? 'Late' : (match.bye ? 'Bye' : ''),
                });
            }

            pairings.sort((a, b) => a.table > b.table);

            return pairings;
        },

        getAllRounds() {
            this.allRounds = [];

            // the first place player should have played in all possible rounds
            for (const [playerCode, player ] of Object.entries(this.standings)) {
                for (let i = 0; i < player.rounds.length; i++) {
                    this.allRounds.push({
                        name: player.rounds[i].rname,
                        num: player.rounds[i].round,
                    });
                }
                break;
            }

            this.allRounds.reverse();
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

        setFilteredPlayers(players) {
            this.filteredPlayers = players.slice();
        },

        toggleFilter(filterType, filterCode, monData) {
            if (this.filters[filterType].filter(item => item == filterCode).length == 0) {
                this.filters[filterType].push(filterCode);
            } else {
                this.filters[filterType] = this.filters[filterType].filter(v => v != filterCode);
            }

            this.applyFilters(monData);
        },

        applyFilters(monData) {
            const filterCheck = {
                items: 'itemcode',
                teras: 'tera',
            };

            this.filteredPlayers = [];

            for (let i = 0; i < monData.players.length; i++) {
                let pcode = monData.players[i];
                let [ pmon ] = this.standings[pcode].team.filter(m => m.code == monData.code);

                if ((!this.filters.items.length || this.filters.items.includes(pmon.itemcode)) &&
                    (!this.filters.teras.length || this.filters.teras.includes(pmon.tera))
                ) {
                    this.filteredPlayers.push(pcode);
                }
            }
        },

        resetFilters() {
            this.filters.items = [];
            this.filters.teras = [];
        },

        isFiltered() {
            return this.filters.items.length || this.filters.teras.length;
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
            return `-${pos[0] + 2}px -${pos[1]}px`;
        },

        setHDItemCoords(data) {
            this.hdItemCoords = data;
        },

        getHDItemSpritePos(name) {
            let pos = this.hdItemCoords[name] || [ 4000, 4000 ];
            return `-${pos[0] * 40}px -${pos[1] * 40}px`;
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

        toggleOpponentsCompact() {
            this.opponentsCompact = !this.opponentsCompact;
        },
    },
    components: {
        'loading': {
            template: '#loading-template',
        },
        'standings-main': {
            template: '#standings-main-template',
            props: [ 'season', 'standings', 'eventInfo' ],
            created: function() {
                document.title = `${this.eventInfo.name} Standings -- Reportworm Standings`;

                this.setNav([{
                    text: `${this.season} Season`,
                    link: `/${this.season}`,
                    active: false,
                    pass: 1,
                }, {
                    text: `${this.eventInfo.name}`,
                    link: `/${this.season}/${this.eventInfo.code}`,
                    active: true,
                }]);
            },
            methods: {
                getSpritePos(name) {
                    return this.$parent.getSpritePos(name);
                },
                getPct(dec, precision) {
                    return this.$parent.getPct(dec, precision)
                },
                setNav(navData) {
                    return this.$parent.setNav(navData);
                },
            },
        },
        'player': {
            template: '#player-template',
            props: [
                'season',
                'opponents',
                'player',
                'monImgBase',
                'eventInfo',
                'opponentsCompact',
            ],
            created: function() {
                document.title = `${this.player.name} -- ${this.eventInfo.name} -- Reportworm Standings`;

                this.setNav([{
                    text: `${this.season} Season`,
                    link: `/${this.season}`,
                    active: false,
                    pass: 1,
                }, {
                    text: `${this.eventInfo.name}`,
                    link: `/${this.season}/${this.eventInfo.code}`,
                    active: false,
                }, {
                    text: `${this.player.name}`,
                    link: `/${this.season}/${this.eventInfo.code}/player/${this.player.code}`,
                    active: true,
                }]);
            },
            methods: {
                getSpritePos(name) {
                    return this.$parent.getSpritePos(name);
                },
                getHDItemSpritePos(name) {
                    return this.$parent.getHDItemSpritePos(name);
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
                toggleOpponentsCompact() {
                    this.$parent.toggleOpponentsCompact();
                },
                isOpponentsCompact() {
                    return this.$parent.opponentsCompact;
                },
                setNav(navData) {
                    return this.$parent.setNav(navData);
                },
            },
        },
        'pairings': {
            template: '#pairings-template',
            props: [ 'season', 'eventInfo', 'pairings', 'allRounds', 'round', 'standings' ],
            created: function() {
                document.title = `${this.round.name} Pairings -- ${this.eventInfo.name} -- Reportworm Standings`;

                this.setNav([{
                    text: `${this.season} Season`,
                    link: `/${this.season}`,
                    active: false,
                    pass: 1,
                }, {
                    text: `${this.eventInfo.name}`,
                    link: `/${this.season}/${this.eventInfo.code}`,
                    active: false,
                }, {
                    text: `${this.round.name} Pairings`,
                    link: `/${this.season}/${this.eventInfo.code}/pairings/${this.round.num}`,
                    active: true,
                }]);
            },
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
                getRecordThroughRound(playerCode, round) {
                    let wins = 0;
                    let loss = 0;
                    const player = this.standings[playerCode];

                    for (let x = 0; x <= player.rounds.length; x++) {
                        if (!player.rounds[x]) {
                            continue;
                        }
                        if (player.rounds[x].round > round) {
                            continue;
                        }
                        if (player.rounds[x].res == 'W' || player.rounds[x].bye) {
                            wins++;
                        }
                        if (player.rounds[x].res == 'L' || player.rounds[x].late) {
                            loss++;
                        }
                    }

                    return `${wins} - ${loss}`;
                },
                setNav(navData) {
                    return this.$parent.setNav(navData);
                },
            },
        },
        'country-stats': {
            template: '#country-stats-template',
            props: [ 'season', 'countryStats', 'standings', 'eventInfo', 'countryCodes' ],
            created: function() {
                document.title = `Country Stats -- ${this.eventInfo.name} -- Reportworm Standings`;

                this.setNav([{
                    text: `${this.season} Season`,
                    link: `/${this.season}`,
                    active: false,
                    pass: 1,
                }, {
                    text: `${this.eventInfo.name}`,
                    link: `/${this.season}/${this.eventInfo.code}`,
                    active: false,
                }, {
                    text: "Country Stats",
                    link: `/${this.season}/${this.eventInfo.code}/countries`,
                    active: true,
                }]);
            },
            methods: {
                getCountryName(code) {
                    if (!code) {
                        return "";
                    }
                    return this.countryCodes[code.toUpperCase()] || "";
                },
                setNav(navData) {
                    return this.$parent.setNav(navData);
                },
            },
        },
        'country': {
            template: '#country-template',
            props: [ 'season', 'countryStats', 'standings', 'eventInfo', 'countryCodes', 'countryCode', 'country' ],
            created: function() {
                document.title = `${this.country} Players -- Country Stats -- ${this.eventInfo.name} -- Reportworm Standings`;

                this.setNav([{
                    text: `${this.season} Season`,
                    link: `/${this.season}`,
                    active: false,
                    pass: 1,
                }, {
                    text: `${this.eventInfo.name}`,
                    link: `/${this.season}/${this.eventInfo.code}`,
                    active: false,
                }, {
                    text: "Country Stats",
                    link: `/${this.season}/${this.eventInfo.code}/countries`,
                    active: false,
                }, {
                    text: `${this.country}`,
                    link: `/${this.season}/${this.eventInfo.code}/country/${this.countryCode}`,
                    active: true,
                }]);
            },
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
                setNav(navData) {
                    return this.$parent.setNav(navData);
                },
            },
        },
        'usage': {
            template: '#usage-template',
            props: [ 'season', 'usage', 'eventInfo' ],
            created: function() {
                document.title = `Usage Stats -- ${this.eventInfo.name} -- Reportworm Standings`;

                this.nav = [{
                    text: `${this.season} Season`,
                    link: `/${this.season}`,
                    active: false,
                    pass: 1,
                }, {
                    text: `${this.eventInfo.name}`,
                    link: `/${this.season}/${this.eventInfo.code}`,
                    active: false,
                }, {
                    text: "Usage Stats",
                    link: `/${this.season}/${this.eventInfo.code}/usage`,
                    active: true,
                }];

            },
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
                setNav(navData) {
                    return this.$parent.setNav(navData);
                },
            }
        },
        'mon': {
            template: '#mon-template',
            props: [ 'season', 'monImgBase', 'eventInfo', 'mon', 'standings', 'filteredPlayers' ],
            created: function(self) {
                document.title = `${this.mon.name} -- Usage Stats -- ${this.eventInfo.name} -- Reportworm Standings`;

                this.setNav([{
                    text: `${this.season} Season`,
                    link: `/${this.season}`,
                    active: false,
                    pass: 1,
                }, {
                    text: `${this.eventInfo.name}`,
                    link: `/${this.season}/${this.eventInfo.code}`,
                    active: false,
                }, {
                    text: "Usage Stats",
                    link: `/${this.season}/${this.eventInfo.code}/usage`,
                    active: false,
                }, {
                    text: `${this.mon.name}`,
                    link: `/${this.season}/${this.eventInfo.code}/mon/${this.mon.code}`,
                    active: true,
                }]);

                this.$parent.setFilteredPlayers(this.mon.players);

                this.$parent.resetFilters();
            },
            methods: {
                getPct(dec, precision) {
                    return this.$parent.getPct(dec, precision)
                },
                getSpritePos(name) {
                    return this.$parent.getSpritePos(name);
                },
                toggleItemFilter(e) {
                    return this.$parent.toggleFilter('items', e.target.value, this.mon);
                },
                toggleTeraFilter(e) {
                    return this.$parent.toggleFilter('teras', e.target.value, this.mon);
                },
                isFiltered() {
                    return this.$parent.isFiltered();
                },
                setNav(navData) {
                    return this.$parent.setNav(navData);
                },
            },
        },
    },
    
};
