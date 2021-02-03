import pickle
import json
from authorGraphDefs import *

from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd

if __name__ == "__main__":
    nodeDict = pickle.load(open('nodeDict.pkl', 'rb'))
    edgeDict = pickle.load(open('edgeDict.pkl', 'rb'))

    f = open('openORD_l0_weighted.json')
    data = json.load(f)

    print(len(data['nodes']))
    print(len(data['edges']))

    for node in data['nodes']:
        nodeDict[int(node['id'])].x = node['x']
        nodeDict[int(node['id'])].y = node['y']

    for edge in data['edges']:
        edgeIdx = edge['source'] + '_0_' + edge['target'] if edge['source'] < edge['target'] else edge['target'] + '_0_' + edge['source']
        edgeDict[edgeIdx].x1 = nodeDict[int(edge['source'])].x
        edgeDict[edgeIdx].y1 = nodeDict[int(edge['source'])].y
        edgeDict[edgeIdx].x2 = nodeDict[int(edge['target'])].x
        edgeDict[edgeIdx].y2 = nodeDict[int(edge['target'])].y

    clustering_input = []
    for nodeId in nodeDict:
        pos = []
        pos.append(nodeDict[nodeId].x)
        pos.append(nodeDict[nodeId].y)
        clustering_input.append(pos)

    np_clustering_input = np.asarray(clustering_input)
    # scale the positions to lie in the 0-1 range
    scaler = MinMaxScaler(feature_range=(0,1), copy=True)
    scaler.fit(np_clustering_input)
    np_clustering_input = scaler.transform(np_clustering_input)

    for nodeIdx, pos in enumerate(np_clustering_input):
        node = nodeDict[nodeIdx]
        node.x = pos[0]
        node.y = pos[1]

    for edge in data['edges']:
        edgeIdx = edge['source'] + '_0_' + edge['target'] if edge['source'] < edge['target'] else edge['target'] + '_0_' + edge['source']
        edgeDict[edgeIdx].x1 = nodeDict[int(edge['source'])].x
        edgeDict[edgeIdx].y1 = nodeDict[int(edge['source'])].y
        edgeDict[edgeIdx].x2 = nodeDict[int(edge['target'])].x
        edgeDict[edgeIdx].y2 = nodeDict[int(edge['target'])].y

    numNodes_l0 = len(nodeDict)
    numEdges_l0 = len(edgeDict)

    # LEVEL 1
    numClusters = 200
    kmeans = KMeans(n_clusters=numClusters, random_state=0, algorithm='elkan').fit(np_clustering_input)
    #print(kmeans.cluster_centers_)

    # level 1 meta nodes
    nodeDict_l1 = {}
    for nodeId, label in enumerate(kmeans.labels_):
        if label+numNodes_l0 not in nodeDict_l1:
            newNode = Node(label+numNodes_l0, str(nodeId), '')
            newNode.x = kmeans.cluster_centers_[label][0]
            newNode.y = kmeans.cluster_centers_[label][1]
            newNode.clusterLevel = 1
            nodeDict_l1[label+numNodes_l0] = newNode

        newNode = nodeDict_l1[label+numNodes_l0]
        newNode.memberNodes.add(nodeId)
        node = nodeDict[nodeId]
        newNode.coauthors = newNode.coauthors.union(node.coauthors)
        node.parentMetaNode[1] = label+numNodes_l0
        newNode.papers.extend(node.papers)
        newNode.memberNodes = newNode.memberNodes.union(node.memberNodes)

    # correct the representative node for each meta node
    for nodeId in nodeDict_l1:
        node = nodeDict_l1[nodeId]
        repNode = nodeDict[int(node.name)]
        paperCount = len(repNode.papers)
        node.name = repNode.name
        node.afiliation = repNode.affiliation
        for memberNode in node.memberNodes:
            if len(nodeDict[memberNode].papers) > paperCount:
                paperCount = len(nodeDict[memberNode].papers)
                node.name = nodeDict[memberNode].name
                node.affiliation = nodeDict[memberNode].affiliation

    # level 1 meta edges
    edgeCounter = numEdges_l0
    edgeDict_l1 = {}
    for edgeIdx in edgeDict:
        edge = edgeDict[edgeIdx]
        author1Id = nodeDict[edge.author1Id].parentMetaNode[1]
        author2Id = nodeDict[edge.author2Id].parentMetaNode[1]

        if author1Id != author2Id:
            edgeIdx_l1 = str(author1Id) + '_1_' + str(author2Id) if str(author1Id) < str(author2Id) else str(author2Id) + '_1_' + str(author1Id)
            if edgeIdx_l1 not in edgeDict_l1:
                edgeDict_l1[edgeIdx_l1] = Edge(edgeIdx_l1, author1Id, author2Id, 1)
                edgeCounter += 1
            
            metaEdge = edgeDict_l1[edgeIdx_l1]
            metaEdge.papers.extend(edge.papers)
            metaEdge.x1 = nodeDict_l1[author1Id].x
            metaEdge.y1 = nodeDict_l1[author1Id].y
            metaEdge.x2 = nodeDict_l1[author2Id].x
            metaEdge.y2 = nodeDict_l1[author2Id].y

    numNodes_l1 = len(nodeDict_l1)
    numEdges_l1 = len(edgeDict_l1)

    # LEVEL 2
    clustering_input = []
    for nodeId in nodeDict_l1:
        pos = []
        pos.append(nodeDict_l1[nodeId].x)
        pos.append(nodeDict_l1[nodeId].y)
        clustering_input.append(pos)

    np_clustering_input = np.asarray(clustering_input)

    numClusters = 50
    kmeans = KMeans(n_clusters=numClusters, random_state=0, algorithm='elkan').fit(np_clustering_input)
    #print(kmeans.cluster_centers_)

    # level 2 meta nodes
    numNodes = numNodes_l0 + numNodes_l1
    nodeDict_l2 = {}
    for nodeId, label in enumerate(kmeans.labels_):
        if label+numNodes not in nodeDict_l2:
            newNode = Node(label+numNodes, str(nodeId+numNodes_l0), '')
            newNode.x = kmeans.cluster_centers_[label][0]
            newNode.y = kmeans.cluster_centers_[label][1]
            newNode.clusterLevel = 2
            nodeDict_l2[label+numNodes] = newNode

        newNode = nodeDict_l2[label+numNodes]
        newNode.memberNodes.add(nodeId+numNodes_l0)
        node = nodeDict_l1[nodeId+numNodes_l0]
        newNode.coauthors = newNode.coauthors.union(node.coauthors)
        node.parentMetaNode[2] = label+numNodes
        newNode.papers.extend(node.papers)
        newNode.memberNodes = newNode.memberNodes.union(node.memberNodes)

    # correct the representative node for each meta node
    for nodeId in nodeDict_l2:
        node = nodeDict_l2[nodeId]
        repNode = nodeDict_l1[int(node.name)]
        paperCount = len(repNode.papers)
        node.name = repNode.name
        node.afiliation = repNode.affiliation
        for memberNode in node.memberNodes:
            if memberNode in nodeDict_l1:
                if len(nodeDict_l1[memberNode].papers) > paperCount:
                    paperCount = len(nodeDict_l1[memberNode].papers)
                    node.name = nodeDict_l1[memberNode].name
                    node.affiliation = nodeDict_l1[memberNode].affiliation
            else:
                if len(nodeDict[memberNode].papers) > paperCount:
                    paperCount = len(nodeDict[memberNode].papers)
                    node.name = nodeDict[memberNode].name
                    node.affiliation = nodeDict[memberNode].affiliation

    # level 2 meta edges
    edgeCounter = numEdges_l0 + numEdges_l1
    edgeDict_l2 = {}
    for edgeIdx_l1 in edgeDict_l1:
        edge = edgeDict_l1[edgeIdx_l1]
        author1Id = nodeDict_l1[edge.author1Id].parentMetaNode[2]
        author2Id = nodeDict_l1[edge.author2Id].parentMetaNode[2]

        if author1Id != author2Id:
            edgeIdx_l2 = str(author1Id) + '_2_' + str(author2Id) if str(author1Id) < str(author2Id) else str(author2Id) + '_2_' + str(author1Id)
            if edgeIdx_l2 not in edgeDict_l2:
                edgeDict_l2[edgeIdx_l2] = Edge(edgeIdx_l2, author1Id, author2Id, 2)
                edgeCounter += 1
            
            metaEdge = edgeDict_l2[edgeIdx_l2]
            metaEdge.papers.extend(edge.papers)
            metaEdge.x1 = nodeDict_l2[author1Id].x
            metaEdge.y1 = nodeDict_l2[author1Id].y
            metaEdge.x2 = nodeDict_l2[author2Id].x
            metaEdge.y2 = nodeDict_l2[author2Id].y

    numNodes_l2 = len(nodeDict_l2)
    numEdges_l2 = len(edgeDict_l2)

    # Create the dataframes
    # node dataframe
    nodeDf = {'nodeId': [], 'posX': [], 'posY': [], 'authorName': [], 'affiliation': [], 'paperCount': [], 'coauthorCount': [], 'memberNodeCount': [], 'clusterLevel': []}

    for nodeId in nodeDict:
        node = nodeDict[nodeId]
        nodeDf['nodeId'].append(node.nodeId)
        nodeDf['posX'].append(node.x)
        nodeDf['posY'].append(node.y)
        nodeDf['authorName'].append(node.name)
        nodeDf['affiliation'].append(node.affiliation)
        nodeDf['paperCount'].append(int(len(node.papers)))
        # nodeDf['coauthors'].append(str(list(node.coauthors)))
        nodeDf['coauthorCount'].append(int(len(node.coauthors)))
        nodeDf['memberNodeCount'].append(int(len(node.memberNodes)))
        nodeDf['clusterLevel'].append(node.clusterLevel)

    for nodeId in nodeDict_l1:
        node = nodeDict_l1[nodeId]
        nodeDf['nodeId'].append(node.nodeId)
        nodeDf['posX'].append(node.x)
        nodeDf['posY'].append(node.y)
        nodeDf['authorName'].append(node.name)
        nodeDf['affiliation'].append(node.affiliation)
        nodeDf['paperCount'].append(int(len(node.papers)))
        # nodeDf['coauthors'].append(str(list(node.coauthors)))
        nodeDf['coauthorCount'].append(int(len(node.coauthors)))
        nodeDf['memberNodeCount'].append(int(len(node.memberNodes)))
        nodeDf['clusterLevel'].append(node.clusterLevel)

    for nodeId in nodeDict_l2:
        node = nodeDict_l2[nodeId]
        nodeDf['nodeId'].append(node.nodeId)
        nodeDf['posX'].append(node.x)
        nodeDf['posY'].append(node.y)
        nodeDf['authorName'].append(node.name)
        nodeDf['affiliation'].append(node.affiliation)
        nodeDf['paperCount'].append(int(len(node.papers)))
        # nodeDf['coauthors'].append(str(list(node.coauthors)))
        nodeDf['coauthorCount'].append(int(len(node.coauthors)))
        nodeDf['memberNodeCount'].append(int(len(node.memberNodes)))
        nodeDf['clusterLevel'].append(node.clusterLevel)


    # edge dataframe
    edgeDf = {'edgeId': [], 'x1': [], 'y1': [], 'x2': [], 'y2': [], 'author1': [], 'author2': [], 'paperCount': [], 'clusterLevel': []}
    
    for edgeId in edgeDict:
        edge = edgeDict[edgeId]
        edgeDf['edgeId'].append(edge.edgeId)
        edgeDf['x1'].append(edge.x1)
        edgeDf['y1'].append(edge.y1)
        edgeDf['x2'].append(edge.x2)
        edgeDf['y2'].append(edge.y2)
        edgeDf['author1'].append(nodeDict[edge.author1Id].name)
        edgeDf['author2'].append(nodeDict[edge.author2Id].name)
        edgeDf['paperCount'].append(int(len(edge.papers)))
        edgeDf['clusterLevel'].append(edge.clusterLevel)

    for edgeId in edgeDict_l1:
        edge = edgeDict_l1[edgeId]
        edgeDf['edgeId'].append(edge.edgeId)
        edgeDf['x1'].append(edge.x1)
        edgeDf['y1'].append(edge.y1)
        edgeDf['x2'].append(edge.x2)
        edgeDf['y2'].append(edge.y2)
        edgeDf['author1'].append(nodeDict_l1[edge.author1Id].name)
        edgeDf['author2'].append(nodeDict_l1[edge.author2Id].name)
        edgeDf['paperCount'].append(int(len(edge.papers)))
        edgeDf['clusterLevel'].append(edge.clusterLevel)

    for edgeId in edgeDict_l2:
        edge = edgeDict_l2[edgeId]
        edgeDf['edgeId'].append(edge.edgeId)
        edgeDf['x1'].append(edge.x1)
        edgeDf['y1'].append(edge.y1)
        edgeDf['x2'].append(edge.x2)
        edgeDf['y2'].append(edge.y2)
        edgeDf['author1'].append(nodeDict_l2[edge.author1Id].name)
        edgeDf['author2'].append(nodeDict_l2[edge.author2Id].name)
        edgeDf['paperCount'].append(int(len(edge.papers)))
        edgeDf['clusterLevel'].append(edge.clusterLevel)

    df = pd.DataFrame(data=nodeDf)
    with open('graphNodesData.csv', 'w') as g:
        df.to_csv(path_or_buf=g, index=False)
        g.close()

    df = pd.DataFrame(data=edgeDf)
    with open('graphEdgesData.csv', 'w') as g:
        df.to_csv(path_or_buf=g, index=False)
        g.close()