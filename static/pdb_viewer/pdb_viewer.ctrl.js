pdbViewerApp.controller("pdbViewerCtrl", function($scope, $timeout) {
	pdb = {id:"2VVM",residues:[1,5]}
	
	load_pdb = function() {
		pv.io.fetchPdb('http://files.rcsb.org/download/' + pdb.id + '.pdb', function(newMol) {
			mol = newMol;
			geom = viewer.cartoon('protein', mol, {color : color.bySS()});
			selectedAtoms = [];
			viewer.autoZoom();
		});
	}
	
	$scope.$watch("pdb.id", function(val) {
		$timeout(function() {
			load_pdb()
		}, 0)
	});
});