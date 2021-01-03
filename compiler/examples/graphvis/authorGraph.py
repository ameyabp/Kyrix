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

from sklearn.cluster import AgglomerativeClustering
import numpy as np

class Node:
    # author
    def __init__(self, id, name, affiliation):
        self.nodeId = id
        self.name = name
        self.affiliation = affiliation
        self.papers = []
        self.coauthors = set()
        self.parentMetaNode = {}    # a dict to record the parent meta node for each visualized cluster level
        self.parentMetaNode[0] = self.name  # a node is its own parent for cluster level 0
        self.clusterLevel = 0
        self.memberNodes = set()
        self.memberNodes.add(self.name)

class Edge:
    # coauthor relationship
    def __init__(self, id, author1, author2, clusterLevel=0):
        self.edgeId = id
        self.authorName1 = author1
        self.authorName2 = author2
        self.papers = []
        self.clusterLevel = clusterLevel

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

    # gather nodes and index by node id
    nodeDict = {}
    # maintain a separate dict to map authors to node ids
    authorDict = {}

    nodeCounter = 0
    for idx, row in df.iterrows():
        authorList = row['AuthorNames'].split(';')
        cleanedAuthorList = ["".join(filter(lambda x: not x.isdigit(), author)) for author in authorList]

        affiliationList = str(row['AuthorAffiliation']).split(';')

        for idx, author in enumerate(cleanedAuthorList):
            affiliation = affiliationList[idx] if idx < len(affiliationList) else ''
            if author not in authorDict:
                node = Node(id=nodeCounter, name=author, affiliation=affiliation)
                nodeDict[nodeCounter] = node
                authorDict[author] = nodeCounter
                nodeCounter += 1
            
            nodeId = authorDict[author]
            nodeDict[nodeId].papers.append(str(row['Title']) + '-' + str(row['Conference']) + '-' + str(row['Year']))
            for coauthor in cleanedAuthorList:
                if coauthor != author:
                    nodeDict[nodeId].coauthors.add(coauthor)

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
            edgeIdx = author1 + '_0_' + author2 if author1 < author2 else author2 + '_0_' + author1

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
        edgeTuple = (authorDict[edge.authorName1], authorDict[edge.authorName2])
        edgeList.append(edgeTuple)

    g.add_vertex(n=numVertices)
    g.add_edge_list(edgeList)

    # generate the graph layout
    pos = sfdp_layout(g=g, C=1, p=4, mu_p=0)

    # IMPLEMENT LEVEL 1 CANVAS OF GRAPH VIZ (ONE LEVEL OF CLUSTERING)
    # USING AGGLOMERATIVE CLUSTERING
    pos2darray = []
    for nodeId in range(numVertices):
        pos2darray.append(pos[nodeId])

    pos2darray = np.asarray(pos2darray)
    
    csrMatrix = gt.spectral.adjacency(g)
    clustering = AgglomerativeClustering(n_clusters=500, affinity='euclidean', connectivity=csrMatrix, linkage='ward').fit(pos2darray)

    print("Num leaf nodes:", clustering.n_leaves_)
    print("Num clusters found:", clustering.n_clusters_)
    print("Num non-leaf nodes:", len(clustering.children_))
    print(clustering.children_)

    # cluster levels grow bottom up: most detailed layer (most zoomed in) is cluster level 0
    # followed by cluster level 1 and so on, the most coarse layer (most zoomed out) is cluster level 'n'
    numNodesPerClusterLevel = {}
    numNodesPerClusterLevel[0] = numVertices

    # create meta nodes from the agglomerative clustering
    nodeCounter = numVertices   # counter for meta nodes resumes from the counter for original nodes
    for i, pair in enumerate(clustering.children_):
        memberNode1 = nodeDict[pair[0]]
        memberNode2 = nodeDict[pair[1]]
        # the meta node gets the name and affiliation of the first node in the children pair
        # this is just a random choice for now, no semantic meaning behind it as of now
        node = Node(nodeCounter, memberNode1.name, memberNode1.affiliation)
        node.papers = memberNode1.papers + memberNode2.papers
        node.coauthors = memberNode1.coauthors.union(memberNode2.coauthors)
        node.clusterLevel = max(memberNode1.clusterLevel, memberNode2.clusterLevel)+1
        if node.clusterLevel not in numNodesPerClusterLevel:
            numNodesPerClusterLevel[node.clusterLevel] = 1
        else:
            numNodesPerClusterLevel[node.clusterLevel] += 1
        node.memberNodes = memberNode1.memberNodes.union(memberNode2.memberNodes)
        # parentName will be assigned later when deciding the final nodes to be visualized
        # we do not visualize the meta nodes on all the cluster levels to reduce the unnecessary creation of intermediate cluster levels
        nodeDict[nodeCounter] = node
        nodeCounter += 1

    #print("Node dict size:", len(nodeDict))
    #node = nodeDict[nodeCounter-1]
    #print(node.name)
    #print(node.affiliation)
    #print(node.clusterLevel)
    #print(len(node.memberNodes))
    #print(len(node.papers))
    #print(len(node.coauthors))

    #print(numNodesPerClusterLevel)
    # try to understand how come there are more than 1 cluster levels having the same number of nodes

    # we have a total of 196 cluster levels created from the above meta-node creation step
    # level 0: 5492
    # level 1: 1598
    # level 2: 804
    # level 3: 472
    # level 4: 296
    # level 5: 189
    # level 6: 130
    # ...
    # for now, we visualize only the first 3 cluster levels which have 5492 (level 0), 1598 (level 1) and 804 (level 2) nodes respectively
    # we determine the parent node for each node/meta-node from the meta-node creation process
    # each node will have a parent node in each of the visualized cluster levels higher than its own cluster level
    for nodeId in nodeDict:
        node = nodeDict[nodeId]
        # we iterate over all the meta-nodes (nodes of cluster level > 0) and for each node,
        # we iterate over all its children nodes and update the parent meta node dict for those nodes
        if node.clusterLevel == 0:
            continue

        for memberName in node.memberNodes:
            memberNode = nodeDict[authorDict[memberName]]
            assert(node.clusterLevel not in memberNode.parentMetaNode)  # assert to ensure that a particular node does not get its parent meta node at any cluster level reassigned
            # such a situation should not arise, a particular node should belong to only one parent meta node at a given cluster level
            memberNode.parentMetaNode[node.clusterLevel] = node.name

    # create meta-edges for the meta-nodes on every cluster level
    edgeCounter = numEdges  # counter for meta edges resumes from the counter for original edges
    metaEdgeDict = {}
    for edgeId in edgeDict:
        edge = edgeDict[edgeId]
        node1 = nodeDict[authorDict[edge.authorName1]]
        node2 = nodeDict[authorDict[edge.authorName2]]

        # create meta-edge for cluster level 1
        if 1 in node1.parentMetaNode and 1 in node2.parentMetaNode:
            # some nodes might not have a parent at some of the higher cluster levels, that is possible and is an artifact of agglomerative clustering
            metaNode1 = nodeDict[authorDict[node1.parentMetaNode[1]]]
            metaNode2 = nodeDict[authorDict[node2.parentMetaNode[1]]]
            if metaNode1.nodeId != metaNode2.nodeId:
                # if the parent meta nodes of the two nodes are the same, we need not create a meta-edge
                edge = Edge(edgeCounter, metaNode1.name, metaNode2.name, 1)
                edgeCounter += 1
                edgeIdx = metaNode1.name + '_1_' + metaNode2.name if metaNode1.name < metaNode2.name else metaNode2.name + '_1_' + metaNode1.name
                metaEdgeDict[edgeIdx] = edge


        # create meta-edge for cluster level 2
        if 2 in node1.parentMetaNode and 2 in node2.parentMetaNode:
            # some nodes might not have a parent at some of the higher cluster levels, that is possible and is an artifact of agglomerative clustering
            metaNode1 = nodeDict[authorDict[node1.parentMetaNode[2]]]
            metaNode2 = nodeDict[authorDict[node2.parentMetaNode[2]]]
            if metaNode1.nodeId != metaNode2.nodeId:
                edge = Edge(edgeCounter, metaNode1.name, metaNode2.name, 2)
                edgeCounter += 1
                edgeIdx = metaNode1.name + '_2_' + metaNode2.name if metaNode1.name < metaNode2.name else metaNode2.name + '_2_' + metaNode1.name
                metaEdgeDict[edgeIdx] = edge

    # node dataframe
    nodeDf = {'nodeId': [], 'posX': [], 'posY': [], 'authorName': [], 'affiliation': [], 'paperCount': [], 'coauthorCount': [], 'memberNodeCount': [], 'clusterLevel': []}

    for node in list(nodeDict.values()):
        if node.clusterLevel > 2:
            continue

        # only add nodes and meta nodes in cluster levels 0, 1 and 2 to the nodeDict
        nodeDf['nodeId'].append(node.nodeId)
        # the locator node determines where a meta node in the higher cluster levels are positioned
        # for now, this is just a random selection of one of the 2 children nodes of the meta-node, whose author name, the meta node uses
        locatorNodeId = nodeDict[authorDict[node.name]].nodeId
        nodeDf['posX'].append(pos[locatorNodeId][0])
        nodeDf['posY'].append(pos[locatorNodeId][1])

        nodeDf['authorName'].append(node.name)
        nodeDf['affiliation'].append(node.affiliation)
        nodeDf['paperCount'].append(len(node.papers))
        nodeDf['coauthorCount'].append(len(node.coauthors))
        nodeDf['memberNodeCount'].append(len(node.memberNodes))
        nodeDf['clusterLevel'].append(node.clusterLevel)

    # edge dataframe
    edgeDf = {'edgeId': [], 'x1': [], 'y1': [], 'x2': [], 'y2': [], 'author1': [], 'author2': [], 'paperCount': [], 'clusterLevel': []}
    
    for edge in list(edgeDict.values()):
        edgeDf['edgeId'].append(edge.edgeId)
        edgeDf['x1'].append(pos[nodeDict[authorDict[edge.authorName1]].nodeId][0])
        edgeDf['y1'].append(pos[nodeDict[authorDict[edge.authorName1]].nodeId][1])
        edgeDf['x2'].append(pos[nodeDict[authorDict[edge.authorName2]].nodeId][0])
        edgeDf['y2'].append(pos[nodeDict[authorDict[edge.authorName2]].nodeId][1])        
        edgeDf['author1'].append(edge.authorName1)
        edgeDf['author2'].append(edge.authorName2)
        edgeDf['paperCount'].append(len(edge.papers))
        edgeDf['clusterLevel'].append(edge.clusterLevel)

    for edge in list(metaEdgeDict.values()):
        edgeDf['edgeId'].append(edge.edgeId)
        edgeDf['x1'].append(pos[nodeDict[authorDict[edge.authorName1]].nodeId][0])
        edgeDf['y1'].append(pos[nodeDict[authorDict[edge.authorName1]].nodeId][1])
        edgeDf['x2'].append(pos[nodeDict[authorDict[edge.authorName2]].nodeId][0])
        edgeDf['y2'].append(pos[nodeDict[authorDict[edge.authorName2]].nodeId][1])        
        edgeDf['author1'].append(edge.authorName1)
        edgeDf['author2'].append(edge.authorName2)
        edgeDf['paperCount'].append(len(edge.papers))
        edgeDf['clusterLevel'].append(edge.clusterLevel)

    df = pd.DataFrame(data=nodeDf)
    with open('graphNodesData.csv', 'w') as g:
        df.to_csv(path_or_buf=g, index=False)
        g.close()

    df = pd.DataFrame(data=edgeDf)
    with open('graphEdgesData.csv', 'w') as g:
        df.to_csv(path_or_buf=g, index=False)
        g.close()
