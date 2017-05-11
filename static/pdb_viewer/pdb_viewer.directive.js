pdbViewerApp.directive("pdbViewer", function($timeout) {
	return {
		template: '<div id="structure-viewer"></div>',
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
				viewer = pv.Viewer(document.getElementById("structure-viewer"), options);
				viewer.fitParent();

				window.onresize = function(event) {
					viewer.fitParent();
				}
			}, 0)
		}
	};
});