export default {
    data() {
        return {
            currentSeason: 0,
            seasonStatus: '',
            seasonStart: '',
            seasonEnd: '',
            worldsDate: '',
            recent: [],
            upcoming: [],

            nav: [{
                text: "𑁔",
                link: '/',
                active: true,
            }],
        }
    },
    methods: {
        init() {
        },

        setBootstrapData(data) {
            this.currentSeason = data.currentSeason;
            this.seasonStatus = data.seasonStatus;
            this.seasonStart = data.seasonStart;
            this.seasonEnd = data.seasonEnd;
            this.worldsDate = data.worldsDate;
            this.recent = data.recent;
            this.upcoming = data.upcoming;
        },
    }
}
