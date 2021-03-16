class Node:
    # author
    def __init__(self, id, name, affiliation):
        self.nodeId = id
        self.name = name
        self.affiliation = affiliation
        self.papers = []
        self.coauthors = set()
        self.parentMetaNode = {}    # a dict to record the parent meta node for each visualized cluster level {1: nodeId, 2: nodeID2, 3:}
        self.clusterLevel = 0
        self.memberNodes = set()
        # index everything using the node and edge IDs
        # node position
        self.x = 0
        self.y = 0

class Edge:
    # coauthor relationship
    def __init__(self, id, author1, author2, clusterLevel=0):
        self.edgeId = id
        self.author1Id = author1
        self.author2Id = author2
        self.papers = []
        self.clusterLevel = clusterLevel
        # edge position
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0

class Paper:
    # attribute of edge
    def __init__(self, title, authors, conferenceName, year):
        self.paperTitle = title
        self.authors = authors
        self.conferenceName = conferenceName
        self.year = year
