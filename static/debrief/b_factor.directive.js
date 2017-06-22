debriefApp.directive("bFactorViewer", function($timeout) {
	return {
		scope: {
			"maxBFactor": "&",
			"currMut": "&"
		},
		templateUrl: "/static/debrief/b_factor.html",
	};
});