export default {
    data() {
        return {
            currentSeason: 0,
            seasonStatus: '',
            seasonDates: '',
            worldsDate: '',
            recent: [],
            upcoming: [],
            inProgress: [],

            strRuns: "runs",
            strWill: "will be",

            pastSeasons: [],
            futureSeasons: [],

            showCredits: false,

            nav: [],
        }
    },
    methods: {
        init() {
        },

        toggleCredits() {
            this.showCredits = !this.showCredits;
        },

        setBootstrapData(data) {
            this.currentSeason = data.currentSeason;
            this.seasonStatus = data.seasonStatus;
            this.seasonDates = data.seasonDates;
            this.worldsDate = data.worldsDate;
            this.recent = data.recent;
            this.upcoming = data.upcoming;
            this.inProgress = data.inProgress;
            this.pastSeasons = data.pastSeasons;
            this.futureSeasons = data.futureSeasons;

            if (!this.upcoming.length) {
                this.strRuns = "ran";
                this.strWill = "were";
            }
        },
    }
}
