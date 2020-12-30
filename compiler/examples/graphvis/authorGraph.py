"""
Co-author network graph
Creating a graph dataset of authors as nodes and co-authorship as edges
Each edge would have as its attribute a list of papers coauthored by the connected author nodes
The edges in such a dataset would be undirected unlike a dataset of papers citing each other.
In the latter, papers are nodes and citations are directed edges.

Nodes table:
NodeID | Author Name | Affiliation | Paper count | Co-author count | Is Meta Node | Member Node Count

Edges table:
EdgeID | Paper name | Author1 | Author2 | Paper count | Is Meta Edge

The vispub dataset has the data for 3109 papers, with following schema
0 - Conference
1 - Year
2 - Title
3 - AuthorNames
4 - AuthorAffiliation

"""

import pandas as pd
from itertools import combinations
import random
# graph_tool is installed outside the virtual environment
# add the path to the graph_tool package in sys.path
import sys
sys.path.append('/usr/lib/python3/dist-packages')
import graph_tool as gt
from graph_tool.draw import sfdp_layout

class Node:
    # author
    def __init__(self, id, name, affiliation):
        self.nodeId = id
        self.name = name
        self.affiliation = affiliation
        self.papers = []
        self.coauthors = set()
        self.parentMetaNode = self.name  # by default a node is initialized to be its own parent
        self.isMetaNode = False
        self.memberNodes = set()

class Edge:
    # coauthor relationship
    def __init__(self, id, author1, author2, isMetaEdge=False):
        self.edgeId = id
        self.authorName1 = author1
        self.authorName2 = author2
        self.papers = []
        self.isMetaEdge = isMetaEdge

class Paper:
    # attribute of edge
    def __init__(self, title, authors, conferenceName, year):
        self.paperTitle = title
        self.authors = authors
        self.conferenceName = conferenceName
        self.year = year

if __name__ == '__main__':
    # PARSE THE CSV TO EXTRACT REQUIRED DATA
    df = pd.read_csv('vispub.csv', dtype={'Conference': str, 'Year': int, 'Title': str, 'AuthorNames': str, 'AuthorAffiliation': str}, na_values=[''])
    df.AuthorAffiliation.astype(str)

    # gather nodes and index by author name
    nodeDict = {}

    nodeCounter = 0
    for idx, row in df.iterrows():
        authorList = row['AuthorNames'].split(';')
        cleanedAuthorList = ["".join(filter(lambda x: not x.isdigit(), author)) for author in authorList]

        affiliationList = str(row['AuthorAffiliation']).split(';')

        for idx, author in enumerate(cleanedAuthorList):
            affiliation = affiliationList[idx] if idx < len(affiliationList) else ''
            if author not in nodeDict:
                node = Node(id=nodeCounter, name=author, affiliation=affiliation)
                nodeDict[author] = node
                nodeCounter += 1
            
            nodeDict[author].papers.append(str(row['Title']) + '-' + str(row['Conference']) + '-' + str(row['Year']))
            for coauthor in cleanedAuthorList:
                if coauthor != author:
                    nodeDict[author].coauthors.add(coauthor)

    # gather edges and index by author names
    # author1 + '_' + author2
    edgeDict = {}

    edgeCounter = 0
    for idx, row in df.iterrows():
        authorList = row['AuthorNames'].split(';')
        cleanedAuthorList = ["".join(filter(lambda x: not x.isdigit(), author)) for author in authorList]

        pairs = combinations(cleanedAuthorList, 2)

        for pair in pairs:
            author1 = pair[0]
            author2 = pair[1]
            edgeIdx = author1 + '_' + author2 if author1 < author2 else author2 + '_' + author1

            if edgeIdx not in edgeDict:
                edge = Edge(id=edgeCounter, author1=author1, author2=author2)
                edgeDict[edgeIdx] = edge
                edgeCounter += 1

            paper = Paper(title=row['Title'], authors=cleanedAuthorList, conferenceName=row['Conference'], year=row['Year'])

            edgeDict[edgeIdx].papers.append(paper)


    numVertices = len(nodeDict)
    numEdges = len(edgeDict)
    print('Number of nodes', numVertices)
    print('Number of edges', numEdges)

    # GENERATE LAYOUT FOR THE GRAPH
    # create graph object
    g = gt.Graph(directed=False)

    # create edge list for providing to the graph tool sfdp_layout API
    edgeList = []
    for edge in list(edgeDict.values()):
        edgeTuple = (nodeDict[edge.authorName1].nodeId, nodeDict[edge.authorName2].nodeId)
        edgeList.append(edgeTuple)

    g.add_vertex(n=numVertices)
    g.add_edge_list(edgeList)

    # generate the graph layout
    pos = sfdp_layout(g)

    # IMPLEMENT LEVEL 1 CANVAS OF GRAPH VIZ (ONE LEVEL OF CLUSTERING)
    # SIMPLE GREEDY CLUSTERING BASED ON PAPER COUNT OF AUTHOR WHICH IS A BETTER MEASURE OF
    # RESEARCHER'S QUALITY COMPARED TO COAUTHOR COUNT
    # CREATE ONE CLUSTER FOR EACH HIGH PAPER COUNT AUTHOR
    sortedNodeDict = dict(sorted(nodeDict.items(), key=lambda x: len(x[1].papers), reverse=True))

    clusterMetaNodes = []
    metaEdgeDict = {}

    numClusters = 1000
    nodesClustered = set()

    # create only 1000 meta nodes or clusters
    # initialize the clusters first, then fill up the member nodes for each cluster
    for authorName in list(sortedNodeDict.keys())[:numClusters]:
        nodeDict[authorName].isMetaNode = True
        nodesClustered.add(authorName)
        clusterMetaNodes.append(authorName)

    print("Init meta nodes:", len(nodesClustered))

    # mark the authors who do not have any coauthors as meta nodes
    # as they cannot be clustered with any other node
    for node in list(nodeDict.values()):
        if len(node.coauthors) == 0:
            node.isMetaNode = True
            nodesClustered.add(node.name)

    print("Init meta nodes + single authors:", len(nodesClustered))

    # cluster the remaining nodes into one of the 1000 clusters
    # first add the 1-hop neighbors to the member nodes of each meta node
    for authorName in list(sortedNodeDict.keys())[:numClusters]:
        metaNode = nodeDict[authorName]
        for coauthor in metaNode.coauthors:
            if coauthor not in nodesClustered:
                metaNode.memberNodes.add(coauthor)
                nodesClustered.add(coauthor)
                nodeDict[coauthor].parentMetaNode = authorName

    print("Init meta nodes + single authors + 1-hop neighbors:", len(nodesClustered))

    # following iterations over all the remaining nodes which haven't been clustered yet
    # these are the 2 and higher hop neighbors of meta nodes
    numNodesClustered = 0
    while numNodesClustered != len(nodesClustered):
        numNodesClustered = len(nodesClustered)
        for authorName in nodeDict:
            if authorName in nodesClustered:
                continue

            node = nodeDict[authorName]
            paperCount = 0
            for coauthor in node.coauthors:
                parentMetaNode = nodeDict[nodeDict[coauthor].parentMetaNode]
                if parentMetaNode.isMetaNode and len(parentMetaNode.papers) > paperCount:
                    nodesClustered.add(authorName)
                    nodeDict[authorName].parentMetaNode = parentMetaNode.name
                    paperCount = len(parentMetaNode.papers)

            if authorName in nodesClustered:
                nodeDict[nodeDict[authorName].parentMetaNode].memberNodes.add(authorName)

    print("Init meta nodes + single authors + > 1-hop neighbors:", len(nodesClustered))

    # if after the first pass, we do not cover all the nodes, we also include the 2-hop neighbours
    if len(nodesClustered) != numVertices:
        #print("Need to cluster disconnected components")
        # randomly assign the remaining nodes to one of the clusters
        for authorName in nodeDict:
            if authorName in nodesClustered:
                continue

            node = nodeDict[authorName]
            clusterNumber = random.randint(0, numClusters-1)
            parentMetaNode = nodeDict[clusterMetaNodes[clusterNumber]]
            node.parentMetaNode = parentMetaNode.name
            parentMetaNode.memberNodes.add(authorName)
            nodesClustered.add(authorName)

        print("Init meta nodes + single authors + > 1-hop neighbors + disconnected nodes:", len(nodesClustered))

    edgeCounter = len(edgeDict)
    # continue the number for meta edges from the numbering for edges
    # create edge dict and edge list for level 1 graph layout
    for edge in list(edgeDict.values()):
        metaNode1 = nodeDict[edge.authorName1].parentMetaNode
        metaNode2 = nodeDict[edge.authorName2].parentMetaNode
        edgeIdx = metaNode1 + '_' + metaNode2 if metaNode1 < metaNode2 else metaNode2 + '_' + metaNode1
        if edgeIdx not in metaEdgeDict:
            metaEdgeDict[edgeIdx] = Edge(id=edgeCounter, author1=metaNode1, author2=metaNode2, isMetaEdge=True)
            edgeCounter += 1
            metaEdge = metaEdgeDict[edgeIdx]
        else:
            metaEdge = metaEdgeDict[edgeIdx]

        metaEdge.papers.extend(edge.papers)

    
    # node dataframe
    nodeDf = {'nodeId': [], 'posX': [], 'posY': [], 'authorName': [], 'affiliation': [], 'paperCount': [], 'coauthorCount': [], 'memberNodeCount': [], 'isMetaNode': []}

    for node in list(nodeDict.values()):
        nodeDf['nodeId'].append(node.nodeId)
        nodeDf['posX'].append(pos[node.nodeId][0])
        nodeDf['posY'].append(pos[node.nodeId][1])
        nodeDf['authorName'].append(node.name)
        nodeDf['affiliation'].append(node.affiliation)
        nodeDf['paperCount'].append(len(node.papers))
        nodeDf['coauthorCount'].append(len(node.coauthors))
        nodeDf['memberNodeCount'].append(len(node.memberNodes))
        nodeDf['isMetaNode'].append(node.isMetaNode)

    # edge dataframe
    edgeDf = {'edgeId': [], 'x1': [], 'y1': [], 'x2': [], 'y2': [], 'author1': [], 'author2': [], 'paperCount': [], 'isMetaEdge': []}
    
    for edge in list(edgeDict.values()):
        edgeDf['edgeId'].append(edge.edgeId)
        edgeDf['x1'].append(pos[nodeDict[edge.authorName1].nodeId][0])
        edgeDf['y1'].append(pos[nodeDict[edge.authorName1].nodeId][1])
        edgeDf['x2'].append(pos[nodeDict[edge.authorName2].nodeId][0])
        edgeDf['y2'].append(pos[nodeDict[edge.authorName2].nodeId][1])        
        edgeDf['author1'].append(edge.authorName1)
        edgeDf['author2'].append(edge.authorName2)
        edgeDf['paperCount'].append(len(edge.papers))
        edgeDf['isMetaEdge'].append(False)

    for edge in list(metaEdgeDict.values()):
        edgeDf['edgeId'].append(edge.edgeId)
        edgeDf['x1'].append(pos[nodeDict[edge.authorName1].nodeId][0])
        edgeDf['y1'].append(pos[nodeDict[edge.authorName1].nodeId][1])
        edgeDf['x2'].append(pos[nodeDict[edge.authorName2].nodeId][0])
        edgeDf['y2'].append(pos[nodeDict[edge.authorName2].nodeId][1])        
        edgeDf['author1'].append(edge.authorName1)
        edgeDf['author2'].append(edge.authorName2)
        edgeDf['paperCount'].append(len(edge.papers))
        edgeDf['isMetaEdge'].append(True)

    df = pd.DataFrame(data=nodeDf)
    with open('graphNodesData.csv', 'w') as g:
        df.to_csv(path_or_buf=g, index=False)
        g.close()

    df = pd.DataFrame(data=edgeDf)
    with open('graphEdgesData.csv', 'w') as g:
        df.to_csv(path_or_buf=g, index=False)
        g.close()