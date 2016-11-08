var nodes, edges, networkName
var nodeDataFromPage, edgeDataFromPage, newNodeFromPage, newEdgeFromPage;
var nodeContents, edgeContents, newNodeContents, newEdgeContents = [];
var selectedDevice;
var removedNodes = [];
var deployedNodesAndEdges, removedNodesAndEdges = {};
var firstSelected = [];
var secondSelected = [];
        // convenience method to stringify a JSON object
        function toJSON(obj) {
            return JSON.stringify(obj, null, 4);
        }
        
        $(document).ready(function(){
            $('#nodes, #edges').on('click', function(e){
                nodeDataFromPage = $('#nodes').html();
                edgeDataFromPage = $('#edges').html();
				//JSON.parse Converts to JS object.
				if(nodeDataFromPage.length > 0){
					nodeContents = JSON.parse(nodeDataFromPage);
				}
				if(edgeDataFromPage.length > 0){
					edgeContents = JSON.parse(edgeDataFromPage);
				}
                console.log($('#nodes, #edges').html());
                return false;
            });
        });
        
        $(document).ready(function(){
            $('#nodes, #edges').on('blur', function(e){
                console.log($('#nodes, #edges').html());
				newNodeFromPage = $('#nodes').html();
				newEdgeFromPage = $('#edges').html();
				//JSON.parse converts to JS object.
				if(newNodeFromPage.length > 0){
					newNodeContents = JSON.parse(newNodeFromPage);
				}
				if(newEdgeFromPage.length > 0){
					newEdgeContents = JSON.parse(newEdgeFromPage);
				}
				if(!_.isEqual(nodeContents, newNodeContents)){
					for(var i=0; i<newNodeContents.length;i++){
						nodes.update(newNodeContents[i]);
					}
				}
				if(!_.isEqual(edgeContents, newEdgeContents)){
					for(var i=0; i<newNodeContents.length;i++){
						edges.update(newEdgeContents[i]);
					}
				}
            });
        });
		 
		/*function findObjDifferences(obj1, obj2){
			var differences = {};
			//If different lengths
			if(obj1.length !== obj2.length){
				return false;
			}
			for(var i=0; i<obj1.length; i++){
				for(property in obj1[i]){
					if(obj1[i][property] !== obj2[i][property]){
						differences[obj1[i]["id"]] = {}
						differences[obj1[i]["id"]][property] = obj2[i][property];
						alert(obj1[i][property] + " is different from " + obj2[i][property]);
					}
				}
			}
		}*/
		
        function addNode(deviceType) {
            try {
                nodes.add({
                    id: document.getElementById('node-id').value,
                    type: deviceType,
                    deployed: "false",
                    label: document.getElementById('node-id').value,
					image: "/static/images/" + deviceType + ".png",
					shape: "image"
                });
            }
            catch (err) {
                alert(err);
            }
        }
		
		function initialLoadAddNetworks(deviceType, networkName){
			alert(networkName);
			try{
				nodes.add({
					id: networkName,
					type: deviceType,
					deployed: "true",
					label: networkName,
					image: "/static/images/" + deviceType + ".png",
					shape: "image"
				});
			}
			catch (err){
				alert(err);
			}
		}
		
        function updateNode() {
            try {
                nodes.update({
                    id: document.getElementById('node-id').value,
                    label: document.getElementById('node-id').value,
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
                    url: '/Home/NetworkTopology/',
                    dataType: 'json',
                    data: "[{'type': 'deploy'}," + deployedNodesAndEdges["nodes"] + "," + deployedNodesAndEdges["edges"] + "]",
                    success: function(data){
                        var deployed_status = data;
                        
                    }
                });
                for (var property in nodes._data){
                    nodes._data[property]["deployed"] = "true";
                }
        }
        
        function updateDeployedStatus(){
            
        }
        function saveTopology(){
            topology = {
                nodes: JSON.stringify(nodes.get(), null, 4),
                edges: JSON.stringify(edges.get(), null, 4)
            }
            $.ajax({
                csrfmiddlewaretoken: '{{ csrf_token }}',
                method: 'POST',
                url: '/Home/NetworkTopology/',
                dataType: 'json',
                data: "[{'action': 'save_template','topology_name': " + "'" + requestTopologyName("Please enter a name to save this topology as") + "'}," + topology["nodes"] + "," + topology["edges"] + "]"
            })
        }
        
        function returnTopology(){
            // This will be changed to accept user input later.
            var returnedNodes = [];
            var returnedEdges = [];
            var e = document.getElementById("top_name_retrieve");
			var topology_name = e.options[e.selectedIndex].text;
			$.ajax({
                csrfmiddlewaretoken: '{{ csrf_token }}',
                method: 'POST',
                url: '/Home/NetworkTopology/',
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
        
		function deleteTemplate(){
			var e = document.getElementById("top_name_retrieve");
			var topology_name = e.options[e.selectedIndex].text;
			$.ajax({
                csrfmiddlewaretoken: '{{ csrf_token }}',
                method: 'POST',
                url: '/Home/NetworkTopology/',
                dataType: 'json',
                data: "[{'action': 'delete_template'}," + "[{'topology_name':" + "'" + topology_name + "'" + "}]]",
			});
		}
		
        function requestTopologyName(messageToUser){
            var input = prompt(messageToUser,"");
            return input;
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
                    url: '/Home/NetworkTopology/',
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
                document.getElementById('nodes').innerHTML = JSON.stringify(nodes.get(), undefined, 4);
            });
            //nodes.add([
            //]);

            // create an array with edges
            edges = new vis.DataSet();
            edges.on('*', function () {
                document.getElementById('edges').innerHTML = JSON.stringify(edges.get(), null, 4);
            });
            //edges.add([
            //]);

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