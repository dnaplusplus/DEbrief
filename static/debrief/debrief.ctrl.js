debriefApp.controller("debriefCtrl", ["$scope", "$timeout", "DEBriefService", function($scope, $timeout, DEBriefService) {
	var self = this;

	self.mutationsList = DEBriefService.mutationsList;
	self.pagination = {current: 1};

	self.mutations = function() {
		return DEBriefService.mutationsList[self.pagination.current - 1];
	}
	
	self.update = function() {
		highlightMutations();
	}

	pdb = DEBriefService.pdb;

	mol = null;
	currentMutations = [];

	load_pdb = function() {
		pv.io.fetchPdb("http://files.rcsb.org/download/" + pdb.id + ".pdb", function(newMol) {
			mol = newMol;
			geom = viewer.cartoon("protein", mol, {color: pv.color.uniform("lightgrey")});
			highlightMutations()
			viewer.autoZoom();
		});
	}

	highlightMutations = function() {
		if(mol) {
			// Revert currently selected atoms:
			for(var i = 0; i < currentMutations.length; i++) {
				setColorForAtom(currentMutations[i].atom, currentMutations[i].color);
			}

			currentMutations = [];

			// Colour newly selected atoms in each chain:
			var chains = mol.chains();

			for(var i = 0; i < chains.length; i++) {
				var chainName = chains[i].name();
				var positions = self.mutations().positions;
				
				for(var j = 0; j < positions.length; j++ ) {
					var atom = mol.atom(chainName + "." + positions[j] + ".CA");

					if(atom !== null) {
						var color = [0,0,0,0];
						geom.getColorForAtom(atom, color);
						currentMutations.push({atom: atom, color: color});
						
						var color = self.mutations().active ? "green" : "red"
						setColorForAtom(atom, color);
						labelAtom(atom, self.mutations().name, color);
					}
				}	
			}

			viewer.requestRedraw();
		}
	}
	
	labelAtom = function(atom, label, color) {
		var options = {
	     fontSize: 16, fontColor: color, backgroundAlpha: 0.4
	    };
		
		viewer.label('label', atom.qualifiedName() + " " + label, atom.pos(), options);
	}

	setColorForAtom = function(atom, color) {
		var view = mol.createEmptyView();
		view.addAtom(atom);
		geom.colorBy(pv.color.uniform(color), view);
	}

	$scope.$watch("pdb.id", function(val) {
		$timeout(function() {
			load_pdb();
		}, 0)
	});
}]);