debriefApp.factory("DEBriefService", [function() {
	var obj = {};
	obj.pdb = {id: "2VVM"};
	obj.mutationsList = [{'active': true, 'name': 'A1B C5D', 'positions': [1, 5]},
		{'active': false, 'name': 'E134F G345H', 'positions': [134, 345]}];
	return obj;
}]);