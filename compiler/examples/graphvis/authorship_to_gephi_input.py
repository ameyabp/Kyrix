"""
Co-author network graph
Creating a graph dataset of authors as nodes and co-authorship as edges
Each edge would have as its attribute a list of papers coauthored by the connected author nodes
The edges in such a dataset would be undirected unlike a dataset of papers citing each other.
In the latter, papers are nodes and citations are directed edges.

Nodes table:
NodeID | Author Name | Affiliation | Paper count | Co-author count | Member Node Count | Cluster Level

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
import pickle
# graph_tool is installed outside the virtual environment
# add the path to the graph_tool package in sys.path
# import sys
# sys.path.append('/usr/lib/python3/dist-packages')
# import graph_tool as gt
# from graph_tool.draw import sfdp_layout

from sklearn.cluster import SpectralClustering
from sklearn.preprocessing import MinMaxScaler
import numpy as np

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

class Edge:
    # coauthor relationship
    def __init__(self, id, author1, author2, clusterLevel=0):
        self.edgeId = id
        self.author1Id = author1
        self.author2Id = author2
        self.papers = []
        self.clusterLevel = clusterLevel

class Paper:
    # attribute of edge
    def __init__(self, title, authors, conferenceName, year):
        self.paperTitle = title
        self.authors = authors
        self.conferenceName = conferenceName
        self.year = year



# PARSE THE CSV TO EXTRACT REQUIRED DATA
df = pd.read_csv('./compiler/examples/graphvis/vispub.csv', dtype={'Conference': str, 'Year': int, 'Title': str, 'AuthorNames': str, 'AuthorAffiliation': str}, na_values=[''])
df.AuthorAffiliation.astype(str)

# gather nodes and index by node id
nodeDict = {}
# maintain a separate dict to map authors to node ids
authorDict = {}

nodeCounter = 0
for ridx, row in df.iterrows():
    authorList = row['AuthorNames'].split(';')
    cleanedAuthorList = ["".join(filter(lambda x: not x.isdigit(), author)) for author in authorList]

    affiliationList = str(row['AuthorAffiliation']).split(';')

    for idx, author in enumerate(cleanedAuthorList):
        affiliation = affiliationList[idx] if idx < len(affiliationList) else ''
        if author not in authorDict:
            node = Node(id=nodeCounter, name=author, affiliation=affiliation)
            node.memberNodes.add(nodeCounter)   # add its own node ID as a member node ID
            # for a node, its level 0 parent does not mean anything, no node on level 0 is a parent
            nodeDict[nodeCounter] = node
            authorDict[author] = nodeCounter
            nodeCounter += 1

        node = nodeDict[authorDict[author]]
        paper = Paper(title=row['Title'], authors=cleanedAuthorList, conferenceName=row['Conference'], year=row['Year'])
        node.papers.append(paper)

# add coauthors as node IDs for all authors
for ridx, row in df.iterrows():
    authorList = row['AuthorNames'].split(';')
    cleanedAuthorList = ["".join(filter(lambda x: not x.isdigit(), author)) for author in authorList]

    for idx, author in enumerate(cleanedAuthorList):   
        node = nodeDict[authorDict[author]]     
        for coauthor in cleanedAuthorList:
            if coauthor != author:
                node.coauthors.add(authorDict[coauthor])

# gather edges and index by author names
# author1 + '_' + author2
edgeDict = {}

edgeCounter = 0
for ridx, row in df.iterrows():
    authorList = row['AuthorNames'].split(';')
    cleanedAuthorList = ["".join(filter(lambda x: not x.isdigit(), author)) for author in authorList]

    pairs = combinations(cleanedAuthorList, 2)

    for pair in pairs:
        author1Id = authorDict[pair[0]]
        author2Id = authorDict[pair[1]]
        # these are level 0 edges
        edgeIdx = str(author1Id) + '_0_' + str(author2Id) if str(author1Id) < str(author2Id) else str(author2Id) + '_0_' + str(author1Id)

        if edgeIdx not in edgeDict:
            edge = Edge(id=edgeCounter, author1=author1Id, author2=author2Id)
            edgeDict[edgeIdx] = edge
            edgeCounter += 1

        paper = Paper(title=row['Title'], authors=cleanedAuthorList, conferenceName=row['Conference'], year=row['Year'])
        edgeDict[edgeIdx].papers.append(paper)

numVertices = len(nodeDict)
numEdges = len(edgeDict)
numPapers = len(df)
print('Number of nodes', numVertices)
print('Number of edges', numEdges)
print('Number of papers', numPapers)

with open('nodeDict.pkl', 'wb') as f:
    pickle.dump(nodeDict, f)
    f.close()

with open('edgeDict.pkl', 'wb') as f:
    pickle.dump(edgeDict, f)
    f.close()

# Create clusters bottom up - first level 1 clustering (less clusters)
# then level 2 clustering (slightly more clusters)
# finally level3 clustering (most clustered view)

# CREATE CLUSTER LEVEL 1
# create the affinity matrix for the graph
# we use the following criteria for the affinity score of an edge
# two authors get an affinity score proportional to the number of publications coauthored between them
# two authors affiliated to the same institution get high affinity score
# diagonal elements are all ones
diag = np.ones(numVertices)
affinity_matrix = np.diag(diag)
for edgeIdx in edgeDict:
    edge = edgeDict[edgeIdx]
    author1Id = edge.author1Id
    author2Id = edge.author2Id
    # affinity score is set by the number of papers coauthored together
    affinity_score = len(edge.papers) / numPapers
    # affinity score is further boosted if the authors belong to the same affiliation
    if (nodeDict[author1Id].affiliation == nodeDict[author2Id].affiliation):
        affinity_score = pow(affinity_score, 0.5)

    affinity_matrix[author1Id, author2Id] = affinity_score
    affinity_matrix[author2Id, author1Id] = affinity_score

# perform spectral clustering
clustering = SpectralClustering(n_clusters=2000, random_state=0, affinity='precomputed', assign_labels='kmeans').fit(affinity_matrix)
print(len(clustering.labels_))

# create meta nodes for level 1
nodeCounter = numVertices
nodeDict_l1 = {}
clusterId2NodeId_l1 = {}   # this dict holds the mapping from cluster ID to node ID
for idx, clusterId in enumerate(clustering.labels_):
    node = nodeDict[idx]
    if clusterId not in clusterId2NodeId_l1:
        # the node with the highest paper count will represent the meta node
        # to be computed once all the nodes have been distributed into clusters
        # as default, just set the first node of that cluster as the representative node
        clusterId2NodeId_l1[clusterId] = nodeCounter
        nodeDict_l1[nodeCounter] = Node(nodeCounter, node.name, node.affiliation)
        nodeDict_l1[nodeCounter].clusterLevel = 1   # change to level 3 later
        nodeCounter += 1

    metaNode = nodeDict_l1[clusterId2NodeId_l1[clusterId]]
    metaNode.memberNodes = metaNode.memberNodes.union(node.memberNodes)
    metaNode.papers.extend(node.papers)
    metaNode.coauthors = metaNode.coauthors.union(node.coauthors)

# correct the representative node for each meta node
for clusterId in clusterId2NodeId_l1:
    metaNode = nodeDict_l1[clusterId2NodeId_l1[clusterId]]
    repNode = nodeDict[authorDict[metaNode.name]]
    for nodeId in metaNode.memberNodes:
        node = nodeDict[nodeId]
        if len(node.papers) > len(repNode.papers):
            repNode = node
            metaNode.name = node.name
            metaNode.affiliation = node.affiliation

    # set the parent meta node for all member nodes of a meta node
    for nodeId in metaNode.memberNodes:
        node = nodeDict[nodeId]
        # every level 0 node should be assigned to one and only one cluster in level 1
        node.parentMetaNode[1] = metaNode.nodeId

# create meta edges for level 1
edgeCounter = numEdges
edgeDict_l1 = {}
for edgeIdx in edgeDict:
    edge = edgeDict[edgeIdx]
    author1Id = nodeDict[edge.author1Id].parentMetaNode[1]
    author2Id = nodeDict[edge.author2Id].parentMetaNode[1]

    if author1Id != author2Id:
        edgeIdx_l1 = str(author1Id) + '_1_' + str(author2Id) if str(author1Id) < str(author2Id) else str(author2Id) + '_1_' + str(author1Id)
        if edgeIdx_l1 not in edgeDict_l1:
            edgeDict_l1[edgeIdx_l1] = Edge(edgeCounter, author1Id, author2Id, 1)
            edgeCounter += 1

        metaEdge = edgeDict_l1[edgeIdx_l1]
        metaEdge.papers.extend(edge.papers)

numVertices_l1 = len(nodeDict_l1)
numEdges_l1 = len(edgeDict_l1)

print("Created cluster level 1:", numVertices_l1, "nodes", numEdges_l1, "edges")

# CREATE CLUSTER LEVEL 2
# create the affinity matrix for the graph
# we use the following criteria for the affinity score of an edge
# two authors get an affinity score proportional to the number of publications coauthored between them
# two authors affiliated to the same institution get high affinity score
# diagonal elements are all ones
diag = np.ones(numVertices_l1)
affinity_matrix_l1 = np.diag(diag)
for edgeIdx in edgeDict_l1:
    edge = edgeDict_l1[edgeIdx]
    author1Id = edge.author1Id
    author2Id = edge.author2Id
    # affinity score is set by the number of papers coauthored together
    affinity_score = len(edge.papers) / numPapers
    # affinity score is further boosted if the authors belong to the same affiliation
    if (nodeDict_l1[author1Id].affiliation == nodeDict_l1[author2Id].affiliation):
        affinity_score = pow(affinity_score, 0.5)

    # subtract numVertices because meta edges link meta nodes
    # whose IDs start from numVertices onward
    affinity_matrix_l1[author1Id-numVertices, author2Id-numVertices] = affinity_score
    affinity_matrix_l1[author2Id-numVertices, author1Id-numVertices] = affinity_score

# perform spectral clustering
clustering = SpectralClustering(n_clusters=500, random_state=0, affinity='precomputed', assign_labels='kmeans').fit(affinity_matrix_l1)
print(len(clustering.labels_))

# create meta nodes for level 2
nodeCounter = numVertices + numVertices_l1
nodeDict_l2 = {}
clusterId2NodeId_l2 = {}   # this dict holds the mapping from cluster ID to node ID
for idx, clusterId in enumerate(clustering.labels_):
    # add numVertices because the IDs for level 1 nodes
    # start from numVertices onward
    node = nodeDict_l1[idx+numVertices]
    if clusterId not in clusterId2NodeId_l2:
        # the node with the highest paper count will represent the meta node
        # to be computed once all the nodes have been distributed into clusters
        # as default, just set the first node of that cluster as the representative node
        clusterId2NodeId_l2[clusterId] = nodeCounter
        nodeDict_l2[nodeCounter] = Node(nodeCounter, node.name, node.affiliation)
        nodeDict_l2[nodeCounter].clusterLevel = 2
        nodeCounter += 1

    metaNode = nodeDict_l2[clusterId2NodeId_l2[clusterId]]
    metaNode.memberNodes = metaNode.memberNodes.union(node.memberNodes)
    metaNode.memberNodes.add(node.nodeId)
    metaNode.papers.extend(node.papers)
    metaNode.coauthors = metaNode.coauthors.union(node.coauthors)

# correct the representative node for each meta node
for clusterId in clusterId2NodeId_l2:
    metaNode = nodeDict_l2[clusterId2NodeId_l2[clusterId]]
    repNode = nodeDict[authorDict[metaNode.name]]
    for nodeId in metaNode.memberNodes:
        node = nodeDict_l1[nodeId] if nodeId in nodeDict_l1 else nodeDict[nodeId]
        if len(node.papers) > len(repNode.papers):
            repNode = node
            metaNode.name = node.name
            metaNode.affiliation = node.affiliation

    # set the parent meta node for all member nodes of a meta node
    for nodeId in metaNode.memberNodes:
        node = nodeDict_l1[nodeId] if nodeId in nodeDict_l1 else nodeDict[nodeId]
        node.parentMetaNode[2] = metaNode.nodeId

# create meta edges for level 2
edgeCounter = numEdges + numEdges_l1
edgeDict_l2 = {}
for edgeIdx in edgeDict_l1:
    edge = edgeDict_l1[edgeIdx]
    author1Id = nodeDict_l1[edge.author1Id].parentMetaNode[2]
    author2Id = nodeDict_l1[edge.author2Id].parentMetaNode[2]

    if author1Id != author2Id:
        edgeIdx_l2 = str(author1Id) + '_2_' + str(author2Id) if str(author1Id) < str(author2Id) else str(author2Id) + '_2_' + str(author1Id)
        if edgeIdx_l2 not in edgeDict_l2:
            edgeDict_l2[edgeIdx_l2] = Edge(edgeCounter, author1Id, author2Id, 2)
            edgeCounter += 1

        metaEdge = edgeDict_l2[edgeIdx_l2]
        metaEdge.papers.extend(edge.papers)

numVertices_l2 = len(nodeDict_l2)
numEdges_l2 = len(edgeDict_l2)

print("Created cluster level 2")

# CREATE CLUSTER LEVEL 3
# create the affinity matrix for the graph
# we use the following criteria for the affinity score of an edge
# two authors get an affinity score proportional to the number of publications coauthored between them
# two authors affiliated to the same institution get high affinity score
# diagonal elements are all ones
diag = np.ones(numVertices_l2)
affinity_matrix_l2 = np.diag(diag)
for edgeIdx in edgeDict_l2:
    edge = edgeDict_l2[edgeIdx]
    # subtract numVertices and numVertices_l1 because meta edges link meta nodes
    # whose IDs start from numVertices+numVertices_l1 onward
    author1Id = edge.author1Id
    author2Id = edge.author2Id
    # affinity score is set by the number of papers coauthored together
    affinity_score = len(edge.papers) / numPapers
    # affinity score is further boosted if the authors belong to the same affiliation
    if (nodeDict_l2[author1Id].affiliation == nodeDict_l2[author2Id].affiliation):
        affinity_score = pow(affinity_score, 0.5)

    affinity_matrix_l2[author1Id - numVertices - numVertices_l1, author2Id - numVertices - numVertices_l1] = affinity_score
    affinity_matrix_l2[author2Id - numVertices - numVertices_l1, author1Id - numVertices - numVertices_l1] = affinity_score

# perform spectral clustering
clustering = SpectralClustering(n_clusters=100, random_state=0, affinity='precomputed', assign_labels='kmeans').fit(affinity_matrix_l2)

# create meta nodes for level 3
nodeCounter = numVertices + numVertices_l1 + numVertices_l2
nodeDict_l3 = {}
clusterId2NodeId_l3 = {}   # this dict holds the mapping from cluster ID to node ID
for idx, clusterId in enumerate(clustering.labels_):
    # add numVertices and numVertices_l1 because the IDs for level 2 nodes
    # start from numVertices+numVertices_l1 onward
    node = nodeDict_l2[idx+numVertices+numVertices_l1]
    if clusterId not in clusterId2NodeId_l3:
        # the node with the highest paper count will represent the meta node
        # to be computed once all the nodes have been distributed into clusters
        # as default, just set the first node of that cluster as the representative node
        clusterId2NodeId_l3[clusterId] = nodeCounter
        nodeDict_l3[nodeCounter] = Node(nodeCounter, node.name, node.affiliation)
        nodeDict_l3[nodeCounter].clusterLevel = 3
        nodeCounter += 1

    metaNode = nodeDict_l3[clusterId2NodeId_l3[clusterId]]
    metaNode.memberNodes = metaNode.memberNodes.union(node.memberNodes)
    metaNode.memberNodes.add(node.nodeId)
    metaNode.papers.extend(node.papers)
    metaNode.coauthors = metaNode.coauthors.union(node.coauthors)

# correct the representative node for each meta node
for clusterId in clusterId2NodeId_l3:
    metaNode = nodeDict_l3[clusterId2NodeId_l3[clusterId]]
    repNode = nodeDict[authorDict[metaNode.name]]
    for nodeId in metaNode.memberNodes:
        node = nodeDict_l2[nodeId] if nodeId in nodeDict_l2 else (nodeDict_l1[nodeId] if nodeId in nodeDict_l1 else nodeDict[nodeId])
        if len(node.papers) > len(repNode.papers):
            repNode = node
            metaNode.name = node.name
            metaNode.affiliation = node.affiliation

    # set the parent meta node for all member nodes of a meta node
    for nodeId in metaNode.memberNodes:
        node = nodeDict_l2[nodeId] if nodeId in nodeDict_l2 else (nodeDict_l1[nodeId] if nodeId in nodeDict_l1 else nodeDict[nodeId])
        node.parentMetaNode[3] = metaNode.nodeId

# create meta edges for level 3
edgeCounter = numEdges + numEdges_l1 + numEdges_l2
edgeDict_l3 = {}
for edgeIdx in edgeDict_l2:
    edge = edgeDict_l2[edgeIdx]
    author1Id = nodeDict_l2[edge.author1Id].parentMetaNode[3]
    author2Id = nodeDict_l2[edge.author2Id].parentMetaNode[3]

    if author1Id != author2Id:
        edgeIdx_l3 = str(author1Id) + '_3_' + str(author2Id) if str(author1Id) < str(author2Id) else str(author2Id) + '_3_' + str(author1Id)
        if edgeIdx_l3 not in edgeDict_l3:
            edgeDict_l3[edgeIdx_l3] = Edge(edgeCounter, author1Id, author2Id, 3)
            edgeCounter += 1

        metaEdge = edgeDict_l3[edgeIdx_l3]
        metaEdge.papers.extend(edge.papers)

numVertices_l3 = len(nodeDict_l3)
numEdges_l3 = len(edgeDict_l3)

print("Created cluster level 3")

print("Total vertices across all cluster levels:", numVertices + numVertices_l1 + numVertices_l2 + numVertices_l3)
print("Total edges across all cluster levels:", numEdges + numEdges_l1 + numEdges_l2 + numEdges_l3)


# Create the dataframes
# node dataframe
nodeDf_l0 = {'id': [], 'posX': [], 'posY': [], 'authorName': [], 'affiliation': [], 'paperCount': [], 'coauthorCount': [], 'memberNodeCount': [], 'clusterLevel': []}
nodeDf_l1 = {'id': [], 'posX': [], 'posY': [], 'authorName': [], 'affiliation': [], 'paperCount': [], 'coauthorCount': [], 'memberNodeCount': [], 'clusterLevel': []}
nodeDf_l2 = {'id': [], 'posX': [], 'posY': [], 'authorName': [], 'affiliation': [], 'paperCount': [], 'coauthorCount': [], 'memberNodeCount': [], 'clusterLevel': []}
nodeDf_l3 = {'id': [], 'posX': [], 'posY': [], 'authorName': [], 'affiliation': [], 'paperCount': [], 'coauthorCount': [], 'memberNodeCount': [], 'clusterLevel': []}


for nodeId in nodeDict:
    node = nodeDict[nodeId]
    nodeDf_l0['id'].append(node.nodeId)
    #nodeDf_l0['posX'].append(pos_l0[nodeId][0])
    #nodeDf_l0['posY'].append(pos_l0[nodeId][1])
    nodeDf_l0['posX'].append(0)
    nodeDf_l0['posY'].append(0)
    nodeDf_l0['authorName'].append(node.name)
    nodeDf_l0['affiliation'].append(node.affiliation)
    nodeDf_l0['paperCount'].append(int(len(node.papers)))
    nodeDf_l0['coauthorCount'].append(int(len(node.coauthors)))
    nodeDf_l0['memberNodeCount'].append(int(len(node.memberNodes)))
    nodeDf_l0['clusterLevel'].append(node.clusterLevel)

for nodeId in nodeDict_l1:
    node = nodeDict_l1[nodeId]
    nodeDf_l1['id'].append(node.nodeId)
    #nodeDf_l1['posX'].append(pos_l1[nodeId-numVertices][0])
    #nodeDf_l1['posY'].append(pos_l1[nodeId-numVertices][1])
    nodeDf_l1['posX'].append(0)
    nodeDf_l1['posY'].append(0)
    nodeDf_l1['authorName'].append(node.name)
    nodeDf_l1['affiliation'].append(node.affiliation)
    nodeDf_l1['paperCount'].append(int(len(node.papers)))
    nodeDf_l1['coauthorCount'].append(int(len(node.coauthors)))
    nodeDf_l1['memberNodeCount'].append(int(len(node.memberNodes)))
    nodeDf_l1['clusterLevel'].append(node.clusterLevel)

for nodeId in nodeDict_l2:
    node = nodeDict_l2[nodeId]
    nodeDf_l2['id'].append(node.nodeId)
    #nodeDf_l2['posX'].append(pos_l2[nodeId-(numVertices+numVertices_l1)][0])
    #nodeDf_l2['posY'].append(pos_l2[nodeId-(numVertices+numVertices_l1)][1])
    nodeDf_l2['posX'].append(0)
    nodeDf_l2['posY'].append(0)
    nodeDf_l2['authorName'].append(node.name)
    nodeDf_l2['affiliation'].append(node.affiliation)
    nodeDf_l2['paperCount'].append(int(len(node.papers)))
    nodeDf_l2['coauthorCount'].append(int(len(node.coauthors)))
    nodeDf_l2['memberNodeCount'].append(int(len(node.memberNodes)))
    nodeDf_l2['clusterLevel'].append(node.clusterLevel)

for nodeId in nodeDict_l3:
    node = nodeDict_l3[nodeId]
    nodeDf_l3['id'].append(node.nodeId)
    #nodeDf_l3['posX'].append(pos_l3[nodeId-(numVertices+numVertices_l1+numVertices_l2)][0])
    #nodeDf_l3['posY'].append(pos_l3[nodeId-(numVertices+numVertices_l1+numVertices_l2)][1])
    nodeDf_l3['posX'].append(0)
    nodeDf_l3['posY'].append(0)
    nodeDf_l3['authorName'].append(node.name)
    nodeDf_l3['affiliation'].append(node.affiliation)
    nodeDf_l3['paperCount'].append(int(len(node.papers)))
    nodeDf_l3['coauthorCount'].append(int(len(node.coauthors)))
    nodeDf_l3['memberNodeCount'].append(int(len(node.memberNodes)))
    nodeDf_l3['clusterLevel'].append(node.clusterLevel)

# edge dataframe
edgeDf_l0 = {'edgeId': [], 'x1': [], 'y1': [], 'x2': [], 'y2': [], 'Source': [], 'Target': [], 'paperCount': [], 'clusterLevel': [], 'weight': []}
edgeDf_l1 = {'edgeId': [], 'x1': [], 'y1': [], 'x2': [], 'y2': [], 'Source': [], 'Target': [], 'paperCount': [], 'clusterLevel': [], 'weight': []}
edgeDf_l2 = {'edgeId': [], 'x1': [], 'y1': [], 'x2': [], 'y2': [], 'Source': [], 'Target': [], 'paperCount': [], 'clusterLevel': [], 'weight': []}
edgeDf_l3 = {'edgeId': [], 'x1': [], 'y1': [], 'x2': [], 'y2': [], 'Source': [], 'Target': [], 'paperCount': [], 'clusterLevel': [], 'weight': []}

for edgeId in edgeDict:
    edge = edgeDict[edgeId]
    edgeDf_l0['edgeId'].append(edge.edgeId)
    #edgeDf_l0['x1'].append(pos_l0[edge.author1Id][0])
    #edgeDf_l0['y1'].append(pos_l0[edge.author1Id][1])
    #edgeDf_l0['x2'].append(pos_l0[edge.author2Id][0])
    #edgeDf_l0['y2'].append(pos_l0[edge.author2Id][1])
    edgeDf_l0['x1'].append(0)
    edgeDf_l0['y1'].append(0)
    edgeDf_l0['x2'].append(0)
    edgeDf_l0['y2'].append(0)
    edgeDf_l0['Source'].append(edge.author1Id)
    edgeDf_l0['Target'].append(edge.author2Id)
    edgeDf_l0['paperCount'].append(int(len(edge.papers)))
    edgeDf_l0['clusterLevel'].append(edge.clusterLevel)
    edgeDf_l0['weight'].append(len(edge.papers) / numPapers)

for edgeId in edgeDict_l1:
    edge = edgeDict_l1[edgeId]
    edgeDf_l1['edgeId'].append(edge.edgeId)
    #edgeDf_l1['x1'].append(pos_l1[edge.author1Id-numVertices][0])
    #edgeDf_l1['y1'].append(pos_l1[edge.author1Id-numVertices][1])
    #edgeDf_l1['x2'].append(pos_l1[edge.author2Id-numVertices][0])
    #edgeDf_l1['y2'].append(pos_l1[edge.author2Id-numVertices][1])
    edgeDf_l1['x1'].append(0)
    edgeDf_l1['y1'].append(0)
    edgeDf_l1['x2'].append(0)
    edgeDf_l1['y2'].append(0)
    edgeDf_l1['Source'].append(edge.author1Id)
    edgeDf_l1['Target'].append(edge.author2Id)
    edgeDf_l1['paperCount'].append(int(len(edge.papers)))
    edgeDf_l1['clusterLevel'].append(edge.clusterLevel)
    edgeDf_l1['weight'].append(len(edge.papers) / numPapers)

for edgeId in edgeDict_l2:
    edge = edgeDict_l2[edgeId]
    edgeDf_l2['edgeId'].append(edge.edgeId)
    #edgeDf_l2['x1'].append(pos_l2[edge.author1Id-(numVertices+numVertices_l1)][0])
    #edgeDf_l2['y1'].append(pos_l2[edge.author1Id-(numVertices+numVertices_l1)][1])
    #edgeDf_l2['x2'].append(pos_l2[edge.author2Id-(numVertices+numVertices_l1)][0])
    #edgeDf_l2['y2'].append(pos_l2[edge.author2Id-(numVertices+numVertices_l1)][1])
    edgeDf_l2['x1'].append(0)
    edgeDf_l2['y1'].append(0)
    edgeDf_l2['x2'].append(0)
    edgeDf_l2['y2'].append(0)
    edgeDf_l2['Source'].append(edge.author1Id)
    edgeDf_l2['Target'].append(edge.author2Id)
    edgeDf_l2['paperCount'].append(int(len(edge.papers)))
    edgeDf_l2['clusterLevel'].append(edge.clusterLevel)
    edgeDf_l2['weight'].append(len(edge.papers) / numPapers)

for edgeId in edgeDict_l3:
    edge = edgeDict_l3[edgeId]
    edgeDf_l3['edgeId'].append(edge.edgeId)
    #edgeDf_l3['x1'].append(pos_l3[edge.author1Id-(numVertices+numVertices_l1+numVertices_l2)][0])
    #edgeDf_l3['y1'].append(pos_l3[edge.author1Id-(numVertices+numVertices_l1+numVertices_l2)][1])
    #edgeDf_l3['x2'].append(pos_l3[edge.author2Id-(numVertices+numVertices_l1+numVertices_l2)][0])
    #edgeDf_l3['y2'].append(pos_l3[edge.author2Id-(numVertices+numVertices_l1+numVertices_l2)][1])
    edgeDf_l3['x1'].append(0)
    edgeDf_l3['y1'].append(0)
    edgeDf_l3['x2'].append(0)
    edgeDf_l3['y2'].append(0)
    edgeDf_l3['Source'].append(edge.author1Id)
    edgeDf_l3['Target'].append(edge.author2Id)
    edgeDf_l3['paperCount'].append(int(len(edge.papers)))
    edgeDf_l3['clusterLevel'].append(edge.clusterLevel)
    edgeDf_l3['weight'].append(len(edge.papers) / numPapers)


df = pd.DataFrame(data=nodeDf_l0)
with open('./graphNodesData_l0.csv', 'w') as g:
    df.to_csv(path_or_buf=g, index=False)
    g.close()

df = pd.DataFrame(data=edgeDf_l0)
with open('graphEdgesData_l0.csv', 'w') as g:
    df.to_csv(path_or_buf=g, index=False)
    g.close()
    
df = pd.DataFrame(data=nodeDf_l1)
with open('./graphNodesData_l1.csv', 'w') as g:
    df.to_csv(path_or_buf=g, index=False)
    g.close()

df = pd.DataFrame(data=edgeDf_l1)
with open('graphEdgesData_l1.csv', 'w') as g:
    df.to_csv(path_or_buf=g, index=False)
    g.close()
    
df = pd.DataFrame(data=nodeDf_l2)
with open('./graphNodesData_l2.csv', 'w') as g:
    df.to_csv(path_or_buf=g, index=False)
    g.close()

df = pd.DataFrame(data=edgeDf_l2)
with open('graphEdgesData_l2.csv', 'w') as g:
    df.to_csv(path_or_buf=g, index=False)
    g.close()
    
df = pd.DataFrame(data=nodeDf_l3)
with open('./graphNodesData_l3.csv', 'w') as g:
    df.to_csv(path_or_buf=g, index=False)
    g.close()

df = pd.DataFrame(data=edgeDf_l3)
with open('graphEdgesData_l3.csv', 'w') as g:
    df.to_csv(path_or_buf=g, index=False)
    g.close()

