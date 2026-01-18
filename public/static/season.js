export default {
    data() {
        return {
            season: 0,

            majors: [],
            futureMajors: [],
            inProgressMajors: [],

            currentView: 'loading',

            nav: [{
                text: "𑁔",
                link: '/',
                active: false,
            }],
        }
    },
    computed: {
        currentProps() {

            switch (this.currentView) {
                case 'season-main':
                    return {
                        season: this.season,
                        majors: this.majors,
                        futureMajors: this.futureMajors,
                        inProgressMajors: this.inProgressMajors,
                    }
            }

            return {};
        },
    },
    methods: {
        init() {
            const chips = window.location.pathname.split('/');

            if (chips.length != 2) {
                window.location = '/';
            }

            this.setSeason(chips[1]);
        },

        setSeason(season) {
            this.season = season;

            this.nav.push({
                text: `${this.season} Season`,
                link: `/${this.season}`,
                active: true,
            });

            this.getSeason();
        },

        getSeason() {
            fetch(`/api/v1/${this.season}`, {
                method: "GET",
                headers: { "Content-type": "application/json" },
            }).then(r => {
                if (!r.ok) {
                    window.location = '/';
                }
                return r.json();
            }).then(d => {
                this.majors = d.filter((m) => m.processed == true && m.in_progress == false);
                this.futureMajors = d.filter((m) => m.processed == false).reverse();
                this.inProgressMajors = d.filter((m) => m.in_progress == true);
                this.currentView = 'season-main';

                document.title = `VGC Events for the ${this.season} Season -- Reportworm Standings`;
            });
        },
    },
    components: {
        'loading': {
            template: '#loading-template',
        },
        'season-main': {
            template: '#season-main-template',
            props: [ 'season', 'majors', 'futureMajors', 'inProgressMajors' ],
            methods: {
            },
        },
    },
    
};
