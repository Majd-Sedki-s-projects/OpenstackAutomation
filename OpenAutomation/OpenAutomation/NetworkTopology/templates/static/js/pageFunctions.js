var nodes, edges, network;

        // convenience method to stringify a JSON object
        function toJSON(obj) {
            return JSON.stringify(obj, null, 4);
        }

        function addNode() {
			var radios = document.getElementsByName('device');

			for (var i = 0, length = radios.length; i < length; i++) {
				if (radios[i].checked) {
					// do whatever you want with the checked radio
					var selectedDevice = radios[i].value;

					// only one radio can be logically checked, don't check the rest
					break;
				}
			}
            try {
                nodes.add({
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

        function updateNode() {
            try {
                nodes.update({
                    id: document.getElementById('node-id').value,
                    label: document.getElementById('node-label').value
                });
            }
            catch (err) {
                alert(err);
            }
        }
        function removeNode() {
            try {
                nodes.remove({id: document.getElementById('node-id').value});
            }
            catch (err) {
                alert(err);
            }
        }
        function returnJsonTop(){
                $.ajax({
                    csrfmiddlewaretoken: '{{ csrf_token }}',
                    method: 'POST',
                    url: '/NetworkTopology/json/',
                    dataType: 'json',
                    data: JSON.stringify(nodes.get(),null,4)
                });         
        }
        function addEdge() {
            try {
                edges.add({
                    id: document.getElementById('edge-id').value,
                    from: document.getElementById('edge-from').value,
                    to: document.getElementById('edge-to').value
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
            var options = {};
            network = new vis.Network(container, data, options);

        }