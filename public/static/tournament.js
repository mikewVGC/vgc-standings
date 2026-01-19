export default {
    data() {
        return {
            season: '',
            major: '',
            eventInfo: {},

            routes: {
                '/': 'standings-main',
                '/player': 'player',
                '/usage': 'usage',
            },

            currentRoute: '/',

            currentView: 'loading',

            loaded: false,
            standings: {},
            usage: {},

            spriteCoords: {},

            monImgBase: '',

            nav: [{
                text: "𑁔",
                link: '/',
                active: false,
            }],
        }
    },
    computed: {
        currentProps() {
            let route = (this.currentRoute.slice(1) || '/');
            let chunks = [];

            if (!this.loaded) {
                return {};
            }

            this.currentView = 'standings-main';

            if (route != '/') {
                chunks = route.split('/');
                if (chunks[1] == "player") {
                    this.currentView = 'player';
                }
                if (chunks[1] == "usage") {
                    this.currentView = 'usage';
                }
            }

            switch (this.currentView) {
                case 'standings-main':
                    document.title = `${this.eventInfo['name']} Standings -- Reportworm Standings`;

                    if (this.nav.length == 4) {
                        this.nav.pop();
                        this.nav[2].active = true;
                    }

                    return {
                        standings: this.standings,
                        season: this.season,
                        eventInfo: this.eventInfo,
                    };
                case 'player':
                    let player = this.standings[chunks[2]] || {};
                    let opps = {};
                    document.title = `${player['name']} -- ${this.eventInfo['name']} Standings -- Reportworm Standings`;
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

                    if (this.nav.length < 4) {
                        this.nav[2].active = false;
                        this.nav.push({
                            text: `${player.name}`,
                            link: `/${this.season}/${this.major}#/player/${player.code}`,
                            active: true,
                        });
                    } else if (this.nav.length == 4) {
                        this.nav[3] = {
                            text: `${player.name}`,
                            link: `/${this.season}/${this.major}#/player/${player.code}`,
                            active: true,
                        };
                    }

                    return {
                        player: player,
                        opponents: opps,
                        monImgBase: this.monImgBase,
                    };

                case 'usage':
                    if (this.nav.length < 4) {
                        this.nav[2].active = false;
                        this.nav.push({
                            text: "Usage Stats",
                            link: `/${this.season}/${this.major}#/usage`,
                            active: true,
                        });
                    }

                    return {
                        eventInfo: this.eventInfo,
                        usage: this.usage,
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
                this.nav.push({
                    text: `${this.eventInfo['name']}`,
                    link: `/${this.season}/${this.major}#`,
                    active: true,
                });

                this.getUsage();
            });

            this.nav.push({
                text: `${this.season} Season`,
                link: `/${this.season}`,
                active: false,
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
                this.loaded = true;
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
            });
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
        'usage': {
            template: '#usage-template',
            props: [ 'usage', 'eventInfo' ],
            methods: {
                getSpritePos(name) {
                    return this.$parent.getSpritePos(name);
                },
                getPct(dec, precision) {
                    return this.$parent.getPct(dec, precision)
                },
            }
        },
        'player': {
            template: '#player-template',
            props: [ 'opponents', 'player', 'monImgBase' ],
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
    },
    
};
