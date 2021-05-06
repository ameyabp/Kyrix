
class dataStructures:
    """
        Dynamically create node and edge class definitions for use
        in the clustering/partitioning/sampling code. Node and edge attributes are
        provided as arguments to the constructor of this class. These attributes 
        become the member variables of the node and edge classes respectively
    """

    """
        Parameters:
        numNodeAttributes: list of strings representing the names of attributes for the node class
        numEdgeAttributes: list of strings representing the names of attributes for the edge class
    """
    def __init__(self, nodeAttributes, edgeAttributes):
        self.nodeAttributes = nodeAttributes
        self.edgeAttributes = edgeAttributes

        nodeAttributeDict = {}
        # naming the following member variables with '_' prefix to avoid
        # possible naming conflicts with actual attributes in the dataset
        nodeAttributeDict['_id'] = None
        nodeAttributeDict['_x'] = None
        nodeAttributeDict['_y'] = None
        nodeAttributeDict['_level'] = None
        nodeAttributeDict['_memberNodes'] = None

        for nodeAttribute in self.nodeAttributes:
            nodeAttributeDict[nodeAttribute] = None

        """
            This is the constructor method definition for the node class
        """
        def nodeCtor(obj, **kwargs):
            for varName, varValue in kwargs.items():
                setattr(obj, varName, varValue)

        nodeAttributeDict['__init__'] = nodeCtor

        edgeAttributeDict = {}
        # naming the following member variables with '_' prefix to avoid
        # possible naming conflicts with actual attributes in the dataset
        edgeAttributeDict['_id'] = None
        edgeAttributeDict['_srcId'] = None
        edgeAttributeDict['_dstId'] = None
        edgeAttributeDict['_level'] = None
        edgeAttributeDict['_memberEdges'] = None
        edgeAttributeDict['_edgeWeight'] = None

        for edgeAttribute in self.edgeAttributes:
            edgeAttributeDict[edgeAttribute] = None

        """
            This is the constructor method definition for the edge class
        """
        def edgeCtor(obj, **kwargs):
            for varName, varValue in kwargs.items():
                setattr(obj, varName, varValue)

        edgeAttributeDict['__init__'] = edgeCtor

        # syntax for creating class using 'type'
        # type('className', superclasses as a tuple, attributeDict)
        self.nodeClass = type('Node', (), nodeAttributeDict)
        self.edgeClass = type('Edge', (), edgeAttributeDict)

    """
        Parameters:
        None

        Returns:
        The node class definition
    """
    def getNodeClass(self):
        return self.nodeClass

    """
        Parameters:
        None

        Returns:
        The edge class definition
    """
    def getEdgeClass(self):
        return self.edgeClass


if __name__ == '__main__':
    """
        Call this .py file standalone to unit test the dataStructures class
        Refer this for example usage of dataStructures class
    """
    nodeAttributes = ['name', 'affiliation', 'papers', 'coauthors']
    edgeAttributes = ['author1_name', 'author2_name', 'papers']
    ds = dataStructures(nodeAttributes, edgeAttributes)

    Node = ds.getNodeClass()
    Edge = ds.getEdgeClass()

    # map node id to node object
    nodeDict = {}

    # the constructor for the node and edge classes has to be called as <var_name>=<var_value>
    node = Node(_id=0, _x=2, _y=5, _level=0, name='Ameya B Patil', affiliation='University of Maryland, College Park', papers=['Kyrix-G'], coauthors=['Ishan Sen'])
    nodeDict[node._id] = node

    node = Node(_id=1, _x=5, _y=2, _level=0, name='Ishan Sen', affiliation='University of Maryland, College Park', papers=['Kyrix-G'], coauthors=['Ameya Patil'])
    nodeDict[node._id] = node

    # map edge id to edge object
    edgeDict = {}

    # edge id created as <lex_smaller_node_id>_<level>_<lex_bigger_node_id>
    edge = Edge(_id='0_0_1', _srcId=0, _dstId=1, _level=0, author1_name='Ameya B Patil', author2_name='Ishan Sen', papers=['Kyrix-G'])
    edgeDict[edge._id] = edge

    for _id in nodeDict:
        node = nodeDict[_id]
        print("Node:", node._id, node.name, node.affiliation, node.papers, node.coauthors)

    for _id in edgeDict:
        edge = edgeDict[_id]
        print("Edge:", edge._id, edge.author1_name, edge.author2_name, edge.papers)
