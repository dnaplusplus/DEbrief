debriefApp.controller("debriefCtrl", ["$http", "$log", "$scope", "$timeout", function($http, $log, $scope, $timeout) {
	var self = this;
	
	self.project_id = "MAO-N";
	self.pagination = {current: 1};
	self.data = {'pdb': {'id': null}, 'mutations': []};
	
	self.submit = function() {
		$http.get("data/" + self.project_id).then(
			function(resp) {
				self.data = resp.data;
				load_pdb();
			},
			function(errResp) {
				$log.error(errResp.data.message);
			});
	}
	
	self.update = function() {
		highlightMutations();
	}

	mol = null;
	currentMutations = [];

	load_pdb = function() {
		pv.io.fetchPdb("http://files.rcsb.org/download/" + self.data.pdb.id + ".pdb", function(newMol) {
			mol = newMol;
			geom = viewer.cartoon("protein", mol, {color: pv.color.uniform("lightgrey")});
			highlightMutations()
			viewer.autoZoom();
		});
	}

	highlightMutations = function() {
		// Selected mutations:
		mutations = self.data.mutations[self.pagination.current - 1];
		
		// Revert currently selected atoms:
		for(var i = 0; i < currentMutations.length; i++) {
			setColorForAtom(currentMutations[i].atom, currentMutations[i].color);
		}

		currentMutations = [];

		// Colour newly selected atoms in each chain:
		var chains = mol.chains();

		for(var i = 0; i < chains.length; i++) {
			var chainName = chains[i].name();
			var positions = mutations.positions;
			
			for(var j = 0; j < positions.length; j++ ) {
				var atom = mol.atom(chainName + "." + positions[j][1] + ".CA");

				if(atom !== null) {
					var color = [0,0,0,0];
					geom.getColorForAtom(atom, color);
					currentMutations.push({atom: atom, color: color});
					
					var color = mutations.active ? "green" : "red"
					setColorForAtom(atom, color);
					labelAtom(atom, positions[j].join(""), color);
				}
			}	
		}

		viewer.requestRedraw();
	}
	
	labelAtom = function(atom, label, color) {
		var options = {
	     fontSize: 16, fontColor: color, backgroundAlpha: 0.4
	    };
		
		viewer.label('label', label, atom.pos(), options);
	}

	setColorForAtom = function(atom, color) {
		var view = mol.createEmptyView();
		view.addAtom(atom);
		geom.colorBy(pv.color.uniform(color), view);
	}
}]);