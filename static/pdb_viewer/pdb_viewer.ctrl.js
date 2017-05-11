pdbViewerApp.controller("pdbViewerCtrl", function($scope, $timeout) {
	result = {"pdb": {id:"2VVM", mutations:[[1,5], [134, 345]]}}
	mol = null;
	mutationIndex = 0;
	currentMutations = [];
	
	load_pdb = function() {
		pv.io.fetchPdb("http://files.rcsb.org/download/" + result.pdb.id + ".pdb", function(newMol) {
			mol = newMol;
			geom = viewer.cartoon("protein", mol, {color : color.bySS()});
			highlightResidues()
			viewer.autoZoom();
		});
	}
	
	highlightMutations = function() {
		// Revert currently selected atoms:
		for(var i = 0; i < currentMutations.length; i++) {
			setColorForAtom(currentMutations[i].atom, currentMutations[i].color);
		}
	
		currentMutations = [];
		
		// Colour newly selected atoms in each chain:
		var chains = mol.chains();
		
		for(var i = 0; i < chains.length; i++) {
			var chainName = chains[i].name();
			
			for(var j = 0; j < result.pdb.mutations[mutationIndex].length; j++ ) {
				var atom = mol.atom(chainName + "." + result.pdb.mutations[mutationIndex][j] + ".CA");
				
				if(atom !== null) {
					var color = [0,0,0,0];
					geom.getColorForAtom(atom, color);
					currentMutations.push({atom: atom, color: color});
					setColorForAtom(atom, "red");
				}
			}	
		}
		
		viewer.requestRedraw();
	}
	
	setColorForAtom = function(atom, color) {
	    var view = mol.createEmptyView();
	    view.addAtom(atom);
	    geom.colorBy(pv.color.uniform(color), view);
	}
	
	$scope.$watch("result.pdb.id", function(val) {
		$timeout(function() {
			load_pdb()
		}, 0)
	});
});