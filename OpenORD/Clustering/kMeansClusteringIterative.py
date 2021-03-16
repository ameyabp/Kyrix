import pickle
import json
from authorGraphDefs import *

from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd
import sys

if __name__ == "__main__":
    nodes = pd.read_csv('/OpenOrd-master/examples/recursive/authorship.coord', names = ['id', 'x', 'y'], sep='\t', header=None)
    edges = pd.read_csv('/OpenOrd-master/examples/recursive/authorship.edges', names = ['source', 'target', 'weight'], dtype={'source': str, 'target': str, 'weight': float}, sep='\t', header=None)


    def link(x,y):
        small = x if x < y else y
        big = y if y > x else x
        return small + '_0_' + big

    edges['source_target'] = [link(x, y) for x, y in zip(edges['source'], edges['target'])]

    star = set()

    def f(x,y):
        one = x + "_0_" + y
        two = y + '_0_' + x
        if one in star or two in star:
            return True
        star.add(one)
        return False
        
        
    edges['duplicate'] = [f(x, y) for x, y in zip(edges['source'], edges['target'])]

    edges = edges[edges['duplicate'] == False]

    edges = edges.drop(columns=['duplicate'])

    fullEdges = pd.read_csv('./graphEdgesDataWeighted_l0.csv', dtype={'edgeId': int, 'x1': int, 'y1': int, 'x2': int, 'y2': int, 'Source': str, 'Target': str, 'paperCount': int, 'clusterLevel': int, 'weights': int}, na_values=[''])


    fullEdges['source_target'] = [link(x, y) for x, y in zip(fullEdges['Source'], fullEdges['Target'])]

    finalEdges = pd.merge(edges, fullEdges, on="source_target")

    finalEdges = finalEdges.drop(columns=['Source', 'Target', 'weight_y', 'weight_x', 'weight_y'])


    cols = ['edgeId', 'source', 'target', 'x1', 'y1', 'x2', 'y2', 'paperCount', 'clusterLevel', 'source_target']

    finalEdges = finalEdges[cols]

    fullNodes = pd.read_csv('./graphNodesData_l0.csv', dtype={'id': int, 'posx': float, 'posy': float, 'authorName': str, 'affiliation': str, 'paperCount': int, 'coauthorCount': int, 'memberNodeCount': int, 'clusterLevel': int}, na_values=[''])

    finalNodes = pd.merge(nodes, fullNodes, on='id')

    finalNodes = finalNodes.drop(columns=['posX', 'posY'])

    finalNodes['parentMetaNode'] = [{0:0} for x in finalNodes['id']]
    finalNodes['papers'] = [np.ones(x) for x in finalNodes['paperCount']]
    finalNodes['memberNodes'] = [{x} for x in finalNodes['id']]
    finalNodes['nodeId'] = finalNodes['id']


    nodeDict = finalNodes.set_index('id').T.to_dict('series')

    finalNodes.drop(columns=['parentMetaNode'])
    finalNodes.drop(columns=['papers'])
    finalNodes.drop(columns=['memberNodes'])

    def getX(ID):
        return nodeDict[int(ID)].x

    def getY(ID):
        return nodeDict[int(ID)].y

    finalEdges['x1'] = [getX(x) for x in edges['source']]
    finalEdges['y1'] = [getY(x) for x in edges['source']]
    finalEdges['x2'] = [getX(x) for x in edges['target']]
    finalEdges['y2'] = [getY(x) for x in edges['target']]


    finalEdges = finalEdges.rename(columns={"source": "author1Id", "target": "author2Id"})

    finalEdges['papers'] = [np.ones(x) for x in finalEdges['paperCount']]

    edgeDict = finalEdges.set_index('source_target').T.to_dict('series')


    clustering_input = []
    count = 0
    reID = {}
    for nodeId in nodeDict:
        reID[count] = nodeId
        count += 1
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
        nodeDict[reID[nodeIdx]].x = pos[0]
        nodeDict[reID[nodeIdx]].y = pos[1]

    finalEdges['x1'] = [getX(x) for x in edges['source']]
    finalEdges['y1'] = [getY(x) for x in edges['source']]
    finalEdges['x2'] = [getX(x) for x in edges['target']]
    finalEdges['y2'] = [getY(x) for x in edges['target']]

    edgeDict = finalEdges.set_index('source_target').T.to_dict('series')



    ##### iterative clustering #####
    if len(sys.argv) < 2:
        clusterLevels = 1
    else:
        clusterLevels = int(sys.argv[1])

    numNodes = np.zeros(clusterLevels + 1)
    numEdges = np.zeros(clusterLevels + 1)

    # keep track of TOTAL number of nodes/edges at the index level (0 for base, 1 for first level, etc.)
    numNodes[0] = len(nodeDict)+1000
    numEdges[0] = len(edgeDict)+1000

    numClusters = [0, 200, 50]

    levelNodeDict = {}
    levelEdgeDict = {}

    levelNodeDict[0] = nodeDict
    levelEdgeDict[0] = edgeDict

    for i in range(1, clusterLevels + 1):
        kmeans = KMeans(n_clusters=numClusters[i], random_state=0, algorithm='elkan').fit(np_clustering_input)

        levelNodeDict[i] = {}
        levelEdgeDict[i] = {}

        numNodesPrev = numNodes[i-1]
        numEdgesPrev = numEdges[i-1]

        for nodeId, label in enumerate(kmeans.labels_):
            
            if i == 1: 
                nodeId = reID[nodeId]
            else:
                nodeId = nodeId
                
            if label+numNodesPrev not in levelNodeDict[i]:
                if i == 1:
                    newNode = Node(label+numNodesPrev, str(nodeId + numNodesPrev), '')
                else:
                    newNode = Node(label+numNodesPrev, str(nodeId + numNodesPrev), '')
                newNode.x = kmeans.cluster_centers_[label][0]
                newNode.y = kmeans.cluster_centers_[label][1]
                newNode.clusterLevel = 1
                levelNodeDict[i][label+numNodesPrev] = newNode

            newNode = levelNodeDict[i][int(float(label+numNodesPrev))]
            newNode.memberNodes.add(nodeId)
            if i == 1:
                node = levelNodeDict[i-1][nodeId]
            else:
                node = levelNodeDict[i-1][nodeId + numNodes[i-2]]
            #newNode.coauthors = newNode.coauthors.union(set(node['coauthors']))
            node.parentMetaNode[i] = label+numNodesPrev
            newNode.papers.extend(node.papers)
            newNode.memberNodes = newNode.memberNodes.union(set(node.memberNodes))

        # correct the representative node for each meta node
        for nodeId in levelNodeDict[i]:
            node = levelNodeDict[i][nodeId]
            if int(float(node.name)) - numNodesPrev < len(reID): 
                tempId = reID[int(float(node.name)) - numNodesPrev]
            else:
                tempId = int(float(node.name)) - numNodesPrev
            repNode = levelNodeDict[0][tempId]
            paperCount = len(repNode.papers)
            node.name = repNode.name
            node.afiliation = repNode.affiliation
            for memberNode in node.memberNodes:
                if memberNode < len(reID): memberNode = reID[memberNode]
                if len(levelNodeDict[0][memberNode].papers) > paperCount:
                    paperCount = len(levelNodeDict[0][memberNode].papers)
                    node.name = levelNodeDict[0][memberNode].name
                    node.affiliation = levelNodeDict[0][memberNode].affiliation

        # level i meta edges
        edgeCounter = numEdgesPrev

        for edgeIdx in levelEdgeDict[i-1]:
            
            edge = levelEdgeDict[i-1][edgeIdx]
            if i == 1:
                author1Id = levelNodeDict[i-1][int(edge.author1Id)].parentMetaNode[i]
                author2Id = levelNodeDict[i-1][int(edge.author2Id)].parentMetaNode[i]
            else:
                author1Id = levelNodeDict[i-1][int(edge.author1Id)].parentMetaNode[i]
                author2Id = levelNodeDict[i-1][int(edge.author2Id)].parentMetaNode[i]

            if author1Id != author2Id:
                edgeIdx = str(author1Id) + '_'+str(i)+'_' + str(author2Id) if str(author1Id) < str(author2Id) else str(author2Id) + '_1_' + str(author1Id)
                if edgeIdx not in levelEdgeDict[i]:
                    levelEdgeDict[i][edgeIdx] = Edge(edgeIdx, author1Id, author2Id, i)
                    edgeCounter += 1

                metaEdge = levelEdgeDict[i][edgeIdx]
                metaEdge.papers.extend(edge.papers)
                metaEdge.x1 = levelNodeDict[i][author1Id].x
                metaEdge.y1 = levelNodeDict[i][author1Id].y
                metaEdge.x2 = levelNodeDict[i][author2Id].x
                metaEdge.y2 = levelNodeDict[i][author2Id].y

        numNodes[i] = len(levelNodeDict[i]) + numNodesPrev
        numEdges[i] = len(levelEdgeDict[i]) + numEdgesPrev

        # no need to compute clustering input for last iteration of for loop
        if i != clusterLevels:
            clustering_input = []
            for nodeId in levelNodeDict[i]:
                pos = []
                pos.append(levelNodeDict[i][nodeId].x)
                pos.append(levelNodeDict[i][nodeId].y)
                clustering_input.append(pos)

            np_clustering_input = np.asarray(clustering_input)
            


    # Create the dataframes
    # node dataframe


    for nodeDict in levelNodeDict:
        nodeDf = {'nodeId': [], 'posX': [], 'posY': [], 'authorName': [], 'affiliation': [], 'paperCount': [], 'coauthorCount': [], 'memberNodeCount': [], 'clusterLevel': []}
        for i in levelNodeDict[nodeDict]:
            node = levelNodeDict[nodeDict][i]
            nodeDf['nodeId'].append(i)
            nodeDf['posX'].append(node.x)
            nodeDf['posY'].append(node.y)
            nodeDf['authorName'].append(node.name)
            nodeDf['affiliation'].append(node.affiliation)
            nodeDf['paperCount'].append(int(len(node.papers)))
            if nodeDict == 0:
                nodeDf['coauthorCount'].append(int(node.coauthorCount))
            else:
                nodeDf['coauthorCount'].append(int(len(node.coauthors)))
            nodeDf['memberNodeCount'].append(int(len(node.memberNodes)))
            nodeDf['clusterLevel'].append(nodeDict)
        
        df = pd.DataFrame(data=nodeDf)
        fileName = './graphNodesData_level_' + str(nodeDict) + '.csv'
        with open(fileName, 'w') as g:
            df.to_csv(path_or_buf=g, index=False)
            g.close()


    # edge dataframe



    for edgeDict in levelEdgeDict:
        edgeDf = {'edgeId': [], 'x1': [], 'y1': [], 'x2': [], 'y2': [], 'author1': [], 'author2': [], 'paperCount': [], 'clusterLevel': []}
        for edgeId in levelEdgeDict[edgeDict]:
            edge = levelEdgeDict[edgeDict][edgeId]
            edgeDf['edgeId'].append(edge.edgeId)
            edgeDf['x1'].append(edge.x1)
            edgeDf['y1'].append(edge.y1)
            edgeDf['x2'].append(edge.x2)
            edgeDf['y2'].append(edge.y2)
            if edgeDict == 0:
                edgeDf['author1'].append(levelNodeDict[0][int(edge.author1Id)].authorName)
                edgeDf['author2'].append(levelNodeDict[0][int(edge.author2Id)].authorName)
            else:
                a1 = levelNodeDict[edgeDict][int(edge.author1Id)].name
                a2 = levelNodeDict[edgeDict][int(edge.author2Id)].name
                edgeDf['author1'].append(levelNodeDict[0][a1].authorName)
                edgeDf['author2'].append(levelNodeDict[0][a2].authorName)
            edgeDf['paperCount'].append(int(len(edge.papers)))
            edgeDf['clusterLevel'].append(edgeDict)
        
        df = pd.DataFrame(data=edgeDf)
        fileName = './graphEdgesData_level_' + str(edgeDict) + '.csv'
        with open(fileName, 'w') as g:
            df.to_csv(path_or_buf=g, index=False)
            g.close()