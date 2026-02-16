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
            playerCodes: [],
            countryStats: {},
            usage: [],
            allRounds: [],

            favs: [],

            monUsageSearch: '',
            playerStandingsSearch: '',

            filters: {
                items: [],
                teras: [],
                moves: [],
                abilities: [],
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

            latestHash: '',
            liveUpdateFrequency: 240,
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
                        playerStandingsSearch: this.playerStandingsSearch,
                        filteredStandings: this.filteredStandings,
                        validFavs: this.validFavs,
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
                        filteredUsage: this.filteredUsage,
                        monUsageSearch: this.monUsageSearch,
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

        filteredStandings() {
            if (!this.playerStandingsSearch.length) {
                return this.playerCodes;
            }

            return this.playerCodes.filter(
                (pcode) => {
                    // this is hideous
                    return this.standings[pcode].name
                        .toLowerCase()
                        .includes(
                            this.playerStandingsSearch.toLowerCase()
                        );
                }
            );
        },

        filteredUsage() {
            if (!this.monUsageSearch.length) {
                return this.usage;
            }

            return this.usage.filter(
                (usage) => {
                    return usage.code.startsWith(this.monUsageSearch.toLowerCase());
                }
            );
        },

        validFavs() {
            return this.favs
                .filter(f => this.standings[f] !== undefined)
                .sort((a, b) => this.standings[a].place > this.standings[b].place);
        },
    },
    methods: {
        init() {
            if (window.location.hash.length > 1) {
                window.location = `${window.location.pathname}${window.location.hash.slice(1)}`;
                return;
            }

            window.addEventListener('click', (e) => {
                if (e.target && e.target.closest('a')) {
                    if ('pass' in e.target.dataset && e.target.dataset.pass == 1) {
                        return;
                    }

                    const anchor = e.target.closest('a');

                    e.preventDefault();

                    const url = anchor.getAttribute('href');
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

            let maybeFavs = localStorage.getItem('player-favorites');
            if (maybeFavs) {
                this.favs = JSON.parse(maybeFavs);
            }

            const chips = window.location.pathname.split('/');
            history.pushState({ page: window.location.pathname }, null, window.location.pathname);
            this.currentRoute = chips.slice(3).join('/');

            this.setMajor(chips[1], chips[2]);

            if (this.liveUpdateFrequency < 30) {
                this.liveUpdateFrequency = 30;
            }
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
                this.playerCodes = [];

                // compile country stats
                for (const [playerCode, player ] of Object.entries(this.standings)) {
                    this.playerCodes.push(playerCode);

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

                if (this.eventInfo.status == 'in_progress') {
                    // in-progress events go into live update mode... in theory
                    // this should probably be done via websockets, but
                    // this site is all static files, so it's just
                    // going to be the old dumb polling strategy
                    setTimeout(() => {
                        this.checkForUpdates();
                    }, this.liveUpdateFrequency * 1000);
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
            if (this.eventInfo.status != 'in_progress') {
                return;
            }

            fetch(`/api/v1/${this.season}/updates`, {
                method: "GET",
                headers: { "Content-type": "application/json" },
            }).then((r) => {
                return r.json();
            }).then((d) => {
                const latestHash = d[this.eventInfo.code] || false;
                if (this.latestHash.length && latestHash && latestHash != this.latestHash) {
                    this.getRegional(() => {
                        // don't need to fetch usage during an event, probably
                    });
                } else {
                    // the backend only updates every ~7 minutes
                    setTimeout(() => {
                        this.checkForUpdates();
                    }, this.liveUpdateFrequency * 1000);
                }

                this.latestHash = latestHash;
            });
        },

        setLiveUpdateFrequency(frequency) {
            if (frequency >= 30) {
                this.liveUpdateFrequency = frequency;
            }
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

        hasFilter(filterType, filterValue) {
            return this.filters[filterType].includes(filterValue);
        },

        applyFilters(monData) {
            this.filteredPlayers = [];

            for (let i = 0; i < monData.players.length; i++) {
                let pcode = monData.players[i];
                let [ pmon ] = this.standings[pcode].team.filter(m => m.code == monData.code);

                if ((!this.filters.items.length || this.filters.items.includes(pmon.itemcode)) &&
                    (!this.filters.teras.length || this.filters.teras.includes(pmon.tera)) &&
                    (!this.filters.moves.length || this.filters.moves.every(m => pmon.moves.includes(m))) &&
                    (!this.filters.abilities.length || this.filters.abilities.includes(pmon.ability))
                ) {
                    this.filteredPlayers.push(pcode);
                }
            }
        },

        resetFilters() {
            this.filters.items = [];
            this.filters.teras = [];
            this.filters.moves = [];
            this.filters.abilities = [];
        },

        isFiltered() {
            return (
                this.filters.items.length ||
                this.filters.teras.length ||
                this.filters.moves.length ||
                this.filters.abilities.length
            );
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

        toggleFav(playerCode) {
            let findPlayer = this.favs.findIndex(p => p == playerCode);
            if (findPlayer >= 0) {
                this.favs.splice(findPlayer, 1);
            } else {
                this.favs.push(playerCode);
            }

            localStorage.setItem('player-favorites', JSON.stringify(this.favs));
        },

        isFav(playerCode) {
            return this.favs.findIndex(p => p == playerCode) >= 0;
        },
    },
    components: {
        'loading': {
            template: '#loading-template',
        },
        'standings-main': {
            template: '#standings-main-template',
            props: [ 'season', 'standings', 'eventInfo', 'playerStandingsSearch', 'filteredStandings', 'validFavs' ],
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
            components: {
                'standings-row': {
                    template: '#standings-row-template',
                    props: [ 'standings', 'pcode', 'eventInfo', 'season', 'showDrop', 'alwaysShowRes' ],
                    methods: {
                        toggleFav(playerCode) {
                            this.$parent.toggleFav(playerCode);
                        },
                        isFav(playerCode) {
                            return this.$parent.isFav(playerCode);
                        },
                        getSpritePos(name) {
                            return this.$parent.getSpritePos(name);
                        },
                        getPct(dec, precision) {
                            return this.$parent.getPct(dec, precision)
                        },
                    },
                },
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
                searchPlayerStandings(e) {
                    this.$parent.playerStandingsSearch = e.target.value;
                },
                clearStandingsSearch() {
                    document.getElementById('playerStandingsSearch').value = '';
                    this.$parent.playerStandingsSearch = '';
                },
                toggleFav(playerCode) {
                    this.$parent.toggleFav(playerCode);
                },
                isFav(playerCode) {
                    return this.$parent.isFav(playerCode);
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
            components: {
                'standings-row': {
                    template: '#standings-row-template',
                    props: [ 'standings', 'pcode', 'eventInfo', 'season', 'showDrop', 'alwaysShowRes' ],
                    methods: {
                        toggleFav(playerCode) {
                            this.$parent.toggleFav(playerCode);
                        },
                        isFav(playerCode) {
                            return this.$parent.isFav(playerCode);
                        },
                        getSpritePos(name) {
                            return this.$parent.getSpritePos(name);
                        },
                        getPct(dec, precision) {
                            return this.$parent.getPct(dec, precision)
                        },
                    },
                },
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
                toggleFav(playerCode) {
                    this.$parent.toggleFav(playerCode);
                },
                isFav(playerCode) {
                    return this.$parent.isFav(playerCode);
                },
            },
        },
        'usage': {
            template: '#usage-template',
            props: [ 'model', 'season', 'usage', 'eventInfo', 'filteredUsage', 'monUsageSearch' ],
            created: function() {
                document.title = `Usage Stats -- ${this.eventInfo.name} -- Reportworm Standings`;

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
                    active: true,
                }]);

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
                searchMonUsage(e) {
                    this.$parent.monUsageSearch = e.target.value;
                },
                clearMonSearch() {
                    document.getElementById('monUsageNameSearch').value = '';
                    this.$parent.monUsageSearch = '';
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
            components: {
                'standings-row': {
                    template: '#standings-row-template',
                    props: [ 'standings', 'pcode', 'eventInfo', 'season', 'showDrop', 'alwaysShowRes' ],
                    methods: {
                        toggleFav(playerCode) {
                            this.$parent.toggleFav(playerCode);
                        },
                        isFav(playerCode) {
                            return this.$parent.isFav(playerCode);
                        },
                        getSpritePos(name) {
                            return this.$parent.getSpritePos(name);
                        },
                        getPct(dec, precision) {
                            return this.$parent.getPct(dec, precision)
                        },
                    },
                },
            },
            methods: {
                getPct(dec, precision) {
                    return this.$parent.getPct(dec, precision)
                },
                getSpritePos(name) {
                    return this.$parent.getSpritePos(name);
                },
                toggleItemFilter(itemCode) {
                    return this.$parent.toggleFilter('items', itemCode, this.mon);
                },
                hasItemFilter(itemCode) {
                    return this.$parent.hasFilter('items', itemCode);
                },
                toggleTeraFilter(teraName) {
                    return this.$parent.toggleFilter('teras', teraName, this.mon);
                },
                hasTeraFilter(teraName) {
                    return this.$parent.hasFilter('teras', teraName);
                },
                toggleMoveFilter(moveName) {
                    return this.$parent.toggleFilter('moves', moveName, this.mon);
                },
                hasMoveFilter(moveName) {
                    return this.$parent.hasFilter('moves', moveName);
                },
                toggleAbilityFilter(abilityName) {
                    return this.$parent.toggleFilter('abilities', abilityName, this.mon);
                },
                hasAbilityFilter(abilityName) {
                    return this.$parent.hasFilter('abilities', abilityName);
                },
                isFiltered() {
                    return this.$parent.isFiltered();
                },
                setNav(navData) {
                    return this.$parent.setNav(navData);
                },
                toggleFav(playerCode) {
                    this.$parent.toggleFav(playerCode);
                },
                isFav(playerCode) {
                    return this.$parent.isFav(playerCode);
                },
            },
        },
    },
    
};
