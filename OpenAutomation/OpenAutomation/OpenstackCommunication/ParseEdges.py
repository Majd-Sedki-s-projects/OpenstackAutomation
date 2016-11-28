
class ParseEdges(object):
    def __init__(self, edges):
        self.edge_info = edges

    def parse_edges(self, node_name):
        for edge_list in self.edge_info:
            if node_name in edge_list["from"]:
                return edge_list["to"]
            elif node_name in edge_list["to"]:
                return edge_list["from"]

#Gets edge where the node is in the from field and router is in the to field
    def parse_from_to(self, node_name):
        for edge_list in self.edge_info:
            if node_name in edge_list["from"]:
                return edge_list["to"]
