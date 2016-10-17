var nodes, edges, network;
var selectedDevice;
var removedNodes = [];
var deployedNodesAndEdges, removedNodesAndEdges = {};
var firstSelected = [];
var secondSelected = [];
//removedNodes.length = 0;
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
                    id: selectedDevice + '-' + document.getElementById('node-id').value,
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
                removedNodes[removedNodes.length] = selectedDevice + '-' + document.getElementById('node-id').value
                nodes.remove({id: selectedDevice + '-' + document.getElementById('node-id').value});
            }
            catch (err) {
                alert(err);
            }
        }
        function returnJsonTop(){
            deployedNodesAndEdges = {
                nodes: JSON.stringify(nodes.get(),null,4),
                edges: JSON.stringify(edges.get(),null,4)  
            }
                $.ajax({
                    csrfmiddlewaretoken: '{{ csrf_token }}',
                    method: 'POST',
                    url: '/NetworkTopology/json/',
                    dataType: 'json',
                    data: "[" + deployedNodesAndEdges["nodes"] + "," + deployedNodesAndEdges["edges"] + "]"
                });
                for (var property in nodes._data){
                    nodes._data[property]["deployed"] = "true";
                }
        }
        function tearDown(){
            //removedNodesAndEdges = {
            //    removedNodes: JSON.stringify(removedNodes.get(),null,4),
                //removedEdges: JSON.stringify(removedEdges.get(),null,4)
            //}
            $.ajax({
                    csrfmiddlewaretoken: '{{ csrf_token }}',
                    method: 'POST',
                    url: '/NetworkTopology/json/',
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
            network = new vis.Network(container, data, options);
            network.setOptions(options);

                    network.on('selectNode', function(p) {
                        if(firstSelected.length == 0){
                            firstSelected = network.getSelectedNodes();
                        }else{
                            secondSelected = network.getSelectedNodes();
                        }
                        if((firstSelected[0].includes('vm-') && secondSelected[0].includes('vm-'))||
                            (firstSelected[0].includes('vm-') && secondSelected[0].includes('apache-'))||
                             (firstSelected[0].includes('apache-') && secondSelected[0].includes('vm-'))){
                            firstSelected = [];
                            secondSelected = [];
                            alert("You cannot connect two VMs");
                        }
                        if(firstSelected.length == 1 && secondSelected.length == 1){
                            var nodeID = firstSelected + "-" + secondSelected
                            addEdge(nodeID,firstSelected[0],secondSelected[0]);
                            firstSelected = [];
                            secondSelected = [];
                        }
                    })
        };   