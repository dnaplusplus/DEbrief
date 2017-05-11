debriefApp.directive("debriefViewer", function($timeout) {
	return {
		templateUrl: "/static/debrief/debrief.html",
		link: function(scope, element) {
			$timeout(function() {
				// Initialise structure viewer:
				var options = {
						width: 'auto',
						height: 'auto',
						antialias: true,
						quality: 'medium'
				};

				document = element[0]
				viewer = pv.Viewer(document.getElementById("pdb-viewer"), options);
				viewer.fitParent();

				window.onresize = function(event) {
					viewer.fitParent();
				}
			}, 0)
		}
	};
});