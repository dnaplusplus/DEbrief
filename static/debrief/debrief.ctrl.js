debriefApp.controller("debriefCtrl", ["$http", function($http) {
	var self = this;
	
	self.projectId = "MAO-N";
	self.pagination = {current: 1};
	self.data = {'pdb': {'id': null}, 'mutations': []};
	
	self.submit = function() {
		self.pagination = {current: 1};
		self.data = {'pdb': {'id': null}, 'mutations': []};
		
		$http.get("data/" + self.projectId).then(
			function(resp) {
				self.data = resp.data;
				loadPdb();
			},
			function(errResp) {
				alert("Unable to fetch data for project " + self.projectId + ".");
			});
	}
	
	self.update = function() {
		highlightMutations();
	}

	mol = null;
	currentHighlights = [];
	currentLabels = [];

	loadPdb = function() {
		pv.io.fetchPdb("http://files.rcsb.org/download/" + self.data.pdb.id + ".pdb", function(newMol) {
			mol = newMol;
			geom = viewer.cartoon("protein", mol, {color: pv.color.uniform("lightgrey")});
			drawLigands();
			highlightMutations()
			viewer.autoZoom();
		});
	}
	
	drawLigands = function() {
		var ligand = mol.select({rnames : ["FAD"]});
	    viewer.ballsAndSticks('ligand', ligand);
	}

	highlightMutations = function() {
		// Unhighlight previously highlighted mutations:
		unhighlightMutations();
		
		// Selected mutations:
		mutations = self.data.mutations[self.pagination.current - 1];
		
		

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
					currentHighlights.push({atom: atom, color: color});
					
					var color = mutations.active ? "green" : "red"
					setColorForAtom(atom, color);
					labelAtom(atom, positions[j].join(""), color);
				}
			}	
		}

		viewer.requestRedraw();
	}
	
	unhighlightMutations = function() {
		// Revert currently selected residues:
		for(var i = 0; i < currentHighlights.length; i++) {
			setColorForAtom(currentHighlights[i].atom, currentHighlights[i].color);
		}
		
		// Revert currently labeled residues:
		for(var i = 0; i < currentLabels.length; i++) {
			currentLabels[i]._U = false;
		}

		currentHighlights = [];
		currentLabels = [];
	}
	
	labelAtom = function(atom, label, color) {
		var options = {
	     font: "Helvetica Neue", fontSize: 14, fontColor: color, backgroundAlpha: 0.0
	    };
		
		currentLabels.push(viewer.label('label', label, atom.pos(), options));
	}

	setColorForAtom = function(atom, color) {
		var view = mol.createEmptyView();
		view.addAtom(atom);
		geom.colorBy(pv.color.uniform(color), view);
	}
}]);