var nodes, edges, networkName
var nodeDataFromPage, edgeDataFromPage, newNodeFromPage, newEdgeFromPage;
var nodeContents = new Array(0);
var edgeContents = new Array(0);
var newNodeContents  = new Array(0);
var newEdgeContents = new Array(0);
var selectedDevice;
var selectedAppName;
var sizeOfApplicationObj;
var removedNodes = [];
var deployedNodesAndEdges, removedNodesAndEdges = {};
var firstSelected = [];
var secondSelected = [];
var sortableListNames = "";
        // convenience method to stringify a JSON object
        function toJSON(obj) {
            return JSON.stringify(obj, null, 4);
        }
        
        //On click of node or edge fields on page.
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
        
        //On blur (click out of field) on the node or edges on the page.
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
                
                //If node has been removed.
                if (newNodeContents.length < nodeContents.length){
                    var copyOfNodes = JSON.parse(JSON.stringify(nodeContents));
                    for (var i=0; i<newNodeContents.length; i++){
                        for (var j=0; j<copyOfNodes.length;j++){
                            if (newNodeContents[i]["id"] == copyOfNodes[j]["id"]){
								copyOfNodes.splice(j,1);
                            }
                        }
                    }
					for (var i=0; i<copyOfNodes.length;i++){
						for (var j=0; j<newEdgeContents.length;j++){
							if(newEdgeContents[j]["from"] == copyOfNodes[i]["id"]){
								edges.remove(newEdgeContents[j]);
							}else if(newEdgeContents[j]["to"] == copyOfNodes[i]["id"]){
								edges.remove(newEdgeContents[j]);
							}
						}
						nodes.remove(copyOfNodes[i]);
					}
				}
                
                //If edge has been removed.
				if (newEdgeContents.length < edgeContents.length){
                    var copyOfEdges = JSON.parse(JSON.stringify(edgeContents));
                    for (var i=0; i<newEdgeContents.length; i++){
                        for (var j=0; j<copyOfEdges.length;j++){
                            if (newEdgeContents[i]["id"] == copyOfEdges[j]["id"]){
								copyOfEdges.splice(j,1);
                            }
                        }
                    }
					for (var i=0; i < copyOfEdges.length; i++){
						edges.remove(copyOfEdges[i]);
					}
				}
				// If edge has been added.
				if (newNodeContents.length > nodeContents.length){
					var copyOfNodes = JSON.parse(JSON.stringify(nodeContents));
					for (var i=0; i<newNodeContents.length;i++){
						for (var j=0; j<copyOfNodes.length;j++){
							if (newNodeContents[i]["id"] == copyOfNodes[j]["id"]){
								copyOfNodes.splice(j,1);
							}
						}
					}
					for (var i=0; i<copyOfNodes.length;i++){
						nodes.add(copyOfNodes[i]);
					}
				}
                //If updates to any names have been made.
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
        }); //End of blur - clicking off editable fields.

        // Drag and drop sortable list. Used to select different VMs for each application.
        function addApplications(applicationRequirements){
            sortableListNames = '#appList';
            var appID = parseInt($('input[name=appName]:checked', '.applicationNameForm')[0].id);
            selectedAppName = $('input[name=appName]:checked', '.applicationNameForm')[0].value;
            var applicationRequirements = applicationRequirements[appID];
            htmlInitData = '<label><ul id="appList" class ="connectedSortable">Applications</label>'
            $('#newAppList').append(htmlInitData);
            htmlInitData = "";
            for (var i=0; i<applicationRequirements.length; i++){
                htmlInitData += '<li class="ui-state-default" value="' + applicationRequirements[i] + '">'+applicationRequirements[i]+'</li>'
            }
            htmlInitData += '</ul>'
            var htmlVMData = ""
            for (var i=0; i<applicationRequirements.length;i++){
                htmlVMData += '<label><ul id="VM'+i+'"'+'class ="connectedSortable">'+ 'VM'+i+'</label>'
                htmlVMData += '</ul>'
                sortableListNames += ',#VM'+i
            }
            $("h4.modal-title").text(selectedAppName)
            $('#newAppList #appList').append(htmlInitData)
            $('#newAppList').append(htmlVMData)
            
            $( function() {
                $(sortableListNames).sortable({
                  placeholder: "ui-state-highlight",
                  connectWith: ".connectedSortable"
                }).disableSelection();
            });
            
            $("#Select-Application-VMs-Modal").modal({backdrop: 'static', keyboard: false});
            destroyModal('Application-Modal');
        }
        
        function saveSelectedAppList(){
            var dataInListObj = {}
            var sortableLists = sortableListNames.replace('#appList,','')
            sortableLists = sortableLists.split(',')
			sizeOfApplicationObj = 0
            for (var i=0; i<sortableLists.length; i++){
                var sortableListData = $("#newAppList " + sortableLists[i].replace(',',''));
                var data = sortableListData[0]["children"]
                for (var j=0; j<data.length;j++){
                    if (j == 0){
                        dataInListObj[sortableLists[i].replace('#','')] = [];
						sizeOfApplicationObj++;
                    }
                    dataInListObj[sortableLists[i].replace('#','')].push(data[j].textContent);
                }
            }
            /*if (sizeOfApplicationObj > 1){
                alert("More than one VM not yet supported");
                resetSortable();
                return;
            }*/
			var groupName = $("#vmGroupName input:text")[0].value
			for (var property in dataInListObj){
				if (dataInListObj.hasOwnProperty(property)){
					nodes.add({
                        id: groupName+"-"+property,
                        type: "vm",
                        deployed: "false",
                        label: groupName+"-"+property,
                        image: "/static/images/vm.png",
                        shape: "image",
						group: groupName,
						application: selectedAppName,
						numVMs: sizeOfApplicationObj,
						requirements: toJSON(dataInListObj[property])
					});
				}
			}
            resetSortable();
        }
        
        function resetSortable(){
            $('#newAppList #appList').html('');
            $('#newAppList').html('');
        }
        
        // Clears a modal of any entered text.
        function destroyModal(modalID){
            $('#'+modalID).on('hidden.bs.modal', function (e) {
              $(this)
                .find("input, textarea, select")
                   .val('')
                   .end()
                .find("input[type=checkbox], input[type=radio]")
                   .prop("checked", "")
                   .end();
            })
        }
        
        
        function addNewApplication(){
            var newNetworkData = [];
			$(".newApplicationForm input:text").each(function(){
                newNetworkData.push($(this).val());
            });
			var selectedOS = $('input[name=chosenOS]:checked', '#newApplicationForm')[0].id
			newNetworkData.push(selectedOS)
            var submit = true;
            var networkName = $('#applicationName');
            var networkReqs = $('#applicationRequirements');
            var imageFile = $('#applicationImage');
            
            if (newNetworkData[0].length == 0){
                networkName.closest('.form-group').removeClass('has-success').addClass('has-error');
                submit = false;
            }else if(newNetworkData[1].length == 0){
                networkReqs.closest('.form-group').removeClass('has-success').addClass('has-error');
                submit = false;
            }
			
            if(submit){
                $.ajax({
                    csrfmiddlewaretoken: '{{ csrf_token }}',
                    method: 'POST',
                    url: '/Home/NetworkTopology/',
                    dataType: 'json',
                    data: "[{'action': 'add_application'}," + "[{'application_info':" + "'" + JSON.stringify(newNetworkData) + "'" + "}]]"
                });
            }
            destroyModal('newApplicationModal');
        }
        
        function removeApplication(){
            var appToRemove = $("#applicationRemoval option:selected").text();
            $.ajax({
                csrfmiddlewaretoken: '{{ csrf_token }}',
                method: 'POST',
                url: '/Home/NetworkTopology/',
                dataType: 'json',
                data: "[{'action': 'remove_application'}," + "[{'application_info':" + "'" + JSON.stringify(appToRemove) + "'" + "}]]"
            });
            destroyModal('removeApplicationModal');
        }
        
        
        //Add selected networks to an array. Pass it to the addNetwork() function.
        function updateNetwork(){
            var selectedNetworks = [];
            $(".networkNameForm input:checked").each(function(){
               selectedNetworks.push($(this).val());
               document.getElementById($(this).val()).disabled = true;
            });
            addNetwork(selectedNetworks);
        }
		
        // Called when the 'New Network' radio button is selected by the user. Opens a new modal form to ask the user for additional input.
		function addNewNetwork(){
            var newNetworkData = [];
			$(".newNetworkForm input:text").each(function(){
                newNetworkData.push($(this).val());
            });
            var submit = true;
            var subnetName = $('#SubnetName');
            var subnetAddr = $('#IPAddress');
            var dhcp_s = $('#poolStart');
            var dhcp_e = $('#poolEnd');
            
            if (!newNetworkData[0]){
                subnetName.closest('.form-group').removeClass('has-success').addClass('has-error');
                submit = false;
            }else{
                subnetName.closest('.form-group').removeClass('has-error').addClass('has-success');
            }
            
            if(!newNetworkData[1]){
                subnetAddr.closest('.form-group').removeClass('has-success').addClass('has-error');
                submit = false;
            }else if(!validateIPAddressWithCIDR(newNetworkData[1])){
                subnetAddr.closest('.form-group').removeClass('has-success').addClass('has-error');
                submit = false;
            }else{
                subnetAddr.closest('.form-group').removeClass('has-error').addClass('has-success');
            }
            
            if(!newNetworkData[2]){
                dhcp_s.closest('.form-group').removeClass('has-success').addClass('has-error');
                submit = false;
            }else if(!validateIPAddressWithoutCIDR(newNetworkData[2])){
                dhcp_s.closest('.form-group').removeClass('has-success').addClass('has-error');
                submit = false;
            }else{
                dhcp_s.closest('.form-group').removeClass('has-error').addClass('has-success');
            }
            
            if(!newNetworkData[3]){
                dhcp_e.closest('.form-group').removeClass('has-success').addClass('has-error');
                submit = false;
            }else if(!validateIPAddressWithoutCIDR(newNetworkData[3])){
                dhcp_e.closest('.form-group').removeClass('has-success').addClass('has-error');
                submit = false;
            }else{
                dhcp_e.closest('.form-group').removeClass('has-error').addClass('has-success');
            }
            
            if(submit){
                
                try{
                    nodes.add({
                        id: newNetworkData[0],
                        type: "network",
                        deployed: "false",
                        label: newNetworkData[0],
                        image: "/static/images/network.png",
                        shape: "image",
                        subnetName: newNetworkData[0],
                        subnet: newNetworkData[1],
                        dhcp_start: newNetworkData[2],
                        dhcp_end: newNetworkData[3]
                    });
                    $("#newNetworkModal").modal('hide');
                }   
                catch(err){
                    alert(err);
                }   
            }
        }
        
        function validateIPAddressWithCIDR(ipaddress){  
            if (/^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\/(3[0-2]|[1-2]?[0-9])$/.test(ipaddress)){  
                return (true)  
            }
            return false;
        }
        
        function validateIPAddressWithoutCIDR(ipaddress){
            if (/^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(ipaddress)){  
                return (true)  
            }
            return false;
        }
        
        function addNetwork(networkList){
            try {
                for(var i=0; i<networkList.length; i++){
                    if (networkList[i] === "newNetwork"){
                        $("#newNetworkModal").modal();
                    }else{
                        nodes.add({
                            id: networkList[i],
                            type: "network",
                            deployed: "false",
                            label: networkList[i],
                            image: "/static/images/network.png",
                            shape: "image",
                            subnetName: "",
                            subnet: "",
                            dhcp_start: "",
                            dhcp_end: ""
                        });
                    }
                }
            }
            catch(err){
                alert(err);
            }
            destroyModal("myNetworkModal");
            destroyModal("newNetworkModal");
        }
        
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
            if ((nodes.get().length) == 0 || (edges.get().length == 0)){
                $.alert("There must be nodes and edges in the topology before deploying to OpenStack.");
                return;
            }
            $.confirm({
                title: 'Confirm Deployment',
                content: 'Topology will be deployed on OpenStack',
                closeIcon: true,
                buttons: {
                    confirm: {
                        btnClass: 'btn-green',
                        action: function () {
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
                        },
                    },
                    cancel: {
                        btnClass: 'btn-red',
                        action: function () {
                            $.alert('Canceled Deployment.');
                        }
                    }
                }
            });
        }
        
        function saveTopology(){
            topology = {
                nodes: JSON.stringify(nodes.get(), null, 4),
                edges: JSON.stringify(edges.get(), null, 4)
            }
            if ((nodes.get().length) == 0 || (edges.get().length == 0)){
                $.alert("There must be nodes and edges in the topology before saving it.");
                return;
            }
            var newTopologyName = [];
			$(".newTopologyForm input:text").each(function(){
                newTopologyName.push($(this).val());
            });
            $.ajax({
                csrfmiddlewaretoken: '{{ csrf_token }}',
                method: 'POST',
                url: '/Home/NetworkTopology/',
                dataType: 'json',
                data: "[{'action': 'save_template','topology_name': " + "'" + newTopologyName[0] + "'}," + topology["nodes"] + "," + topology["edges"] + "]"
            })
        }
        
        function returnTopology(){
            // This will be changed to accept user input later.
            var returnedNodes = [];
            var returnedEdges = [];
            var e = document.getElementById("top_name_retrieve");
			var topology_name = e.options[e.selectedIndex].text;
            $.confirm({
                title: 'Retrieve Topology',
                content: 'The topology named' + topology_name + ' will be retrieved and placed into your Network.',
                closeIcon: true,
                buttons: {
                    confirm: {
                        btnClass: 'btn-green',
                        action: function () {
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
                        },
                    },
                    cancel: {
                        btnClass: 'btn-red',
                        action: function () {return;}
                    }
                }
            });
        }
        
		function deleteTemplate(){
			var e = document.getElementById("top_name_retrieve");
			var topology_name = e.options[e.selectedIndex].text;
            $.confirm({
                title: 'Delete Topology',
                content: 'The topology named' + topology_name + ' will be permanently deleted from the database.',
                closeIcon: true,
                buttons: {
                    confirm: {
                        btnClass: 'btn-green',
                        action: function () {
                            $.ajax({
                                csrfmiddlewaretoken: '{{ csrf_token }}',
                                method: 'POST',
                                url: '/Home/NetworkTopology/',
                                dataType: 'json',
                                data: "[{'action': 'delete_template'}," + "[{'topology_name':" + "'" + topology_name + "'" + "}]]",
                            });
                        },
                    },
                    cancel: {
                        btnClass: 'btn-red',
                        action: function () {return;}
                    }
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
                    url: '/Home/NetworkTopology/',
                    dataType: 'json',
					data: "[{'action': 'teardown'}," + "[{'removed_nodes':" + "'" + JSON.stringify(removedNodes) + "'" + "}]]"
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
                        alert("Only one of the two nodes you are connecting should be a network.");
                    }
                };
            });
        }