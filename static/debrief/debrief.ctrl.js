debriefApp.controller("debriefCtrl", ["$scope", "$timeout", "DEBriefService", function($scope, $timeout, DEBriefService) {
	var self = this;
	
	self.mutationsList = DEBriefService.mutationsList;
	self.pagination = {current: 1};
	
	pdb = DEBriefService.pdb;
	
	mutations = function() {
		return DEBriefService.mutationsList[self.pagination.current - 1];
	}
	
	mol = null;
	currentMutations = [];

	load_pdb = function() {
		pv.io.fetchPdb("http://files.rcsb.org/download/" + pdb.id + ".pdb", function(newMol) {
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
			
			for(var j = 0; j < mutations().length; j++ ) {
				var atom = mol.atom(chainName + "." + mutations()[j] + ".CA");
				
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
	
	$scope.$watch("pdb.id", function(val) {
		$timeout(function() {
			load_pdb()
		}, 0)
	});
}]);