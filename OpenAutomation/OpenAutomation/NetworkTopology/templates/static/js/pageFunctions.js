var nodes, edges, network;
var selectedDevice;
var removedNodes = [];
var deployedNodesAndEdges, removedNodesAndEdges = {};
var firstSelected = [];
var secondSelected = [];
        // convenience method to stringify a JSON object
        function toJSON(obj) {
            return JSON.stringify(obj, null, 4);
        }

        function addNode() {
			var radios = document.getElementsByName('device');

			for (var i = 0, length = radios.length; i < length; i++) {
				if (radios[i].checked) {
					// do whatever you want with the checked radio
					selectedDevice = radios[i].value;
					// only one radio can be logically checked, don't check the rest
					break;
				}
			}
            try {
                nodes.add({
                    id: document.getElementById('node-id').value,
                    type: selectedDevice,
                    deployed: "false",
                    label: document.getElementById('node-label').value,
					image: "/static/images/" + selectedDevice + ".png",
					shape: "image"
                });
            }
            catch (err) {
                alert(err);
            }
        }

        function updateNode() {
            try {
                nodes.update({
                    id: document.getElementById('node-id').value,
                    label: document.getElementById('node-label').value,
                    image: "/static/images/" + selectedDevice + ".png",
					shape: "image"
                });
            }
            catch (err) {
                alert(err);
            }
        }
        function removeNode() {
            try {
                var nodeToRemove = document.getElementById('node-id').value
                removedNodes[removedNodes.length] = nodeToRemove
                nodes.remove({id: nodeToRemove});
                // Removes edges that are left behind by the removed nodes.
                for (var property in edges._data){
                    if (edges._data[property]["to"] == nodeToRemove){
                        edges.remove({id: edges._data[property]["id"]})
                    }else if (edges._data[property]["from"] == nodeToRemove){
                        edges.remove({id: edges._data[property]["id"]})
                    }
                }
            }
            catch (err) {
                alert(err);
            }
        }
        function deploy(){
            deployedNodesAndEdges = {
                nodes: JSON.stringify(nodes.get(),null,4),
                edges: JSON.stringify(edges.get(),null,4)  
            }
                $.ajax({
                    csrfmiddlewaretoken: '{{ csrf_token }}',
                    method: 'POST',
                    url: '/NetworkTopology/',
                    dataType: 'json',
                    data: "[{'type': 'deploy'}," + deployedNodesAndEdges["nodes"] + "," + deployedNodesAndEdges["edges"] + "]"
                });
                for (var property in nodes._data){
                    nodes._data[property]["deployed"] = "true";
                }
        }
        
        function saveTopology(){
            topology = {
                nodes: JSON.stringify(nodes.get(), null, 4),
                edges: JSON.stringify(edges.get(), null, 4)
            }
            $.ajax({
                csrfmiddlewaretoken: '{{ csrf_token }}',
                method: 'POST',
                url: '/NetworkTopology/',
                dataType: 'json',
                data: "[{'action': 'save_template'}," + topology["nodes"] + "," + topology["edges"] + "]"
            })
        }
        
        function returnTopology(){
            // This will be changed to accept user input later.
            var returnedNodes = [];
            var returnedEdges = [];
            var topology_name = "TEMPORARY_NAME"
            $.ajax({
                csrfmiddlewaretoken: '{{ csrf_token }}',
                method: 'POST',
                url: '/NetworkTopology/',
                dataType: 'json',
                data: "[{'action': 'return_topology'}," + "[{'topology_name':" + "'" + topology_name + "'" + "}]]",
            
                success: function(data){
                    var returnedTopology = data;
                    returnedNodes = returnedTopology[0];
                    returnedEdges = returnedTopology[1];
                    addTopology(returnedNodes, returnedEdges);
                }
            });
        }
        
        function addTopology(returnedNodes, returnedEdges){
            if (returnedNodes.length > 0){
                for (var i = 0; i < returnedNodes.length; ++i){
                    nodes.add(returnedNodes[i]);
                }
            }
            if (returnedEdges.length > 0){
                for (var i = 0; i < returnedEdges.length; ++i){
                    edges.add(returnedEdges[i]);
                }
            }
        }
        
        function tearDown(){
            $.ajax({
                    csrfmiddlewaretoken: '{{ csrf_token }}',
                    method: 'POST',
                    url: '/NetworkTopology/',
                    dataType: 'json',
                    data: JSON.stringify(removedNodes)
                });
        }
        function addEdge(nodeID, firstNode, secondNode) {
            try {
                edges.add({
                    id: nodeID,
                    from: firstNode,
                    to: secondNode
                });
              }
            catch (err) {
                alert(err);
            }
        }
        function updateEdge() {
            try {
                edges.update({
                    id: document.getElementById('edge-id').value,
                    from: document.getElementById('edge-from').value,
                    to: document.getElementById('edge-to').value
                });
            }
            catch (err) {
                alert(err);
            }
        }
        function removeEdge() {
            try {
                edges.remove({id: document.getElementById('edge-id').value});
            }
            catch (err) {
                alert(err);
            }
        }
        function draw() {
            // create an array with nodes
            nodes = new vis.DataSet();
            nodes.on('*', function () {
                document.getElementById('nodes').innerHTML = JSON.stringify(nodes.get(), null, 4);
            });
            nodes.add([
            ]);

            // create an array with edges
            edges = new vis.DataSet();
            edges.on('*', function () {
                document.getElementById('edges').innerHTML = JSON.stringify(edges.get(), null, 4);
            });
            edges.add([
            ]);

            // create a network
            var container = document.getElementById('network');
            var data = {
                nodes: nodes,
                edges: edges
            };
            var options = {interaction:{
                                hover:true,
                                selectable:true
            }};
            // Create the network.
            network = new vis.Network(container, data, options);
            network.setOptions(options);

                    network.on('selectNode', function(p) {
                        // If no nodes have been selected yet.
                        if(firstSelected.length == 0){
                            firstSelected = network.getSelectedNodes();
                        // If one node has already been selected.
                        }else{
                            secondSelected = network.getSelectedNodes();
                        }
                        if(firstSelected.length == 1 && secondSelected.length == 1){
                                var linkCreated = false;
                                upperLoop:
                                for (var property in nodes._data){
                                    // If the first node selected is a network and the second is not a network.
                                    if (nodes._data[property]["id"] == firstSelected[0] && nodes._data[property]["type"] == "network"){
                                        for (var property in nodes._data){
                                            if(nodes._data[property]["id"] == secondSelected[0] && nodes._data[property]["type"] != "network"){
                                                var nodeID = firstSelected + "-" + secondSelected;
                                                addEdge(nodeID,firstSelected[0],secondSelected[0]);
                                                firstSelected = [];
                                                secondSelected = [];
                                                linkCreated = true;
                                                break upperLoop;
                                            }
                                        }
                                    // If the first node selected is not a network and the second node selected is a network.
                                    }else if (nodes._data[property]["id"] == firstSelected[0] && nodes._data[property]["type"] != "network"){
                                        for (var property in nodes._data){
                                            if(nodes._data[property]["id"] == secondSelected[0] && nodes._data[property]["type"] == "network"){
                                                var nodeID = firstSelected + "-" + secondSelected;
                                                addEdge(nodeID,firstSelected[0],secondSelected[0]);
                                                firstSelected = [];
                                                secondSelected = [];
                                                linkCreated = true;
                                                break upperLoop;
                                            }
                                        }
                                    }
                                }
                            // If the link was not created, empty the selected arrays and alert the user that an error was made.
                            if (!linkCreated){
                                firstSelected = [];
                                secondSelected = [];
                                alert("One of the two nodes you are connecting must be a network.");
                            }
                        };
                    });
        }