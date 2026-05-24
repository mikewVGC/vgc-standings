export default {
    data() {
        return {
            season: 0,

            majors: [],
            futureMajors: [],
            inProgressMajors: [],

            eventSearchStr: '',
            eventTypeFilter: 'all',

            currentView: 'loading',

            nav: [],
        }
    },
    computed: {
        currentProps() {

            switch (this.currentView) {
                case 'season-main':
                    return {
                        season: this.season,
                        majors: this.filteredMajors,
                        futureMajors: this.filteredFutureMajors,
                        inProgressMajors: this.filteredInProgressMajors,
                        eventSearchStr: this.eventSearchStr,
                    }
            }

            return {};
        },

        filteredMajors() {
            return this.searchEventList(this.majors, this.eventSearchStr);
        },
        filteredFutureMajors() {
            return this.searchEventList(this.futureMajors, this.eventSearchStr);
        },
        filteredInProgressMajors() {
            return this.searchEventList(this.inProgressMajors, this.eventSearchStr);
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

        searchEventList(events, searchStr) {
            if (searchStr.length < 2) {
                return events;
            }

            return events.filter((e) => {
                return e.name.toLowerCase().includes(
                    searchStr
                        .toLowerCase()
                        .normalize('NFD')
                        .replace(/[\u0300-\u036f]/g, '')
                );
            });
        },

        getList(listName) {
            switch (listName) {
                case 'in-progress':
                    return this.filteredInProgressMajors;
                case 'completed':
                    return this.filteredMajors;
                case 'upcoming':
                    return this.filteredFutureMajors;
            }

            return [];
        },

        showList(listName) {
            if (!this.getList(listName).length) {
                return false;
            }

            if (listName != this.eventTypeFilter && this.eventTypeFilter != 'all') {
                return false;
            }

            return true;
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
                this.majors = d.filter((m) => m.status == 'complete');
                this.futureMajors = d.filter((m) => m.status == 'upcoming').reverse();
                this.inProgressMajors = d.filter((m) => m.status == 'in_progress');
                this.currentView = 'season-main';

                this.inProgressMajors.reverse();

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
            props: [ 'season', 'majors', 'futureMajors', 'inProgressMajors', 'eventSearchStr' ],
            methods: {
                searchEvents(e) {
                    this.$parent.eventSearchStr = e.target.value;
                },
                clearEventSearch() {
                    this.$parent.eventSearchStr = '';
                },
                showList(listName) {
                    return this.$parent.showList(listName);
                },
                updateEventsFilter(e) {
                    this.$parent.eventTypeFilter = e.target.value;
                },
            },
        },
    },
    
};
