from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import sys

sys.path.append("..")
from dataStructures import *

class kMeansClustering:
    def __init__(self, randomState, clusterLevels, nodeDict, edgeDict):
        # parameters for kMeans clustering algorithm
        self.algorithm = 'elkan'
        self.randomState = randomState
        self.clusterLevels = clusterLevels
        # dicts to keep track of the node and edge dicts at each level
        self.nodeDicts = {}
        self.edgeDicts = {}
        # dicts to keep track of number of nodes and edges for each cluster level
        self.nodeCounts = {}
        self.edgeCounts = {}
        # we create cluster levels starting from 0
        # so the unclustered data is level 0, first level of clustering is level 1, and so on
        self.nodeDicts[0] = nodeDict
        self.edgeDicts[0] = edgeDict
        self.nodeCounts[0] = len(nodeDict)
        self.edgeCounts[0] = len(edgeDict)

        # get class definitions for node and edge objects
        nodeAttributes = nodeDict[0].__dict__.keys()
        nodeAttributes = filter(lambda x: x[0] != '_', nodeAttributes)
        edgeAttributes = edgeDict[0].__dict__.keys()
        edgeAttributes = filter(lambda x: x[0] != '_', edgeAttributes)

        self.dataStructures = dataStructures(nodeAttributes, edgeAttributes)
        self.Node = self.dataStructures.getNodeClass()
        self.Edge = self.dataStructures.getEdgeClass()


    def run(self):
        nodeCounter = 0
        edgeCounter = 0

        for level, numMetaNodes in enumerate(self.clusterLevels):
            prevNodeDict = self.nodeDicts[level]
            prevEdgeDict = self.edgeDicts[level]
            clustering_input = []
            for nodeId in prevNodeDict:
                pos = []
                pos.append(prevNodeDict[nodeId]._x)
                pos.append(prevNodeDict[nodeId]._y)
                clustering_input.append(pos)

            np_clustering_input = np.asarray(clustering_input)
            kmeans = KMeans(n_clusters=numMetaNodes, random_state=self.randomState, algorithm=self.algorithm).fit(np_clustering_input)
            
            nodeCounter += len(prevNodeDict)
            edgeCounter += len(edgeDict)

            currNodeDict = {}
            currEdgeDict = {}

            for id, label in enumerate(kmeans.labels_):
                nodeId = nodeCounter + id
                if nodeId not in currNodeDict:
                    currNodeDict[nodeId] = self.Node(_id=nodeId, _x=kmeans.cluster_centers_[label][0], _y=kmeans.cluster_labels_[label][1], _level=level+1)
                
                newNode = currNodeDict[nodeId]
                newNode._memberNodes.append(id)
                prevNodeDict[id]._parentNode = nodeId

                # aggregate the required node attributes as per user specification
                # HERE

            for edgeIdx in prevEdgeDict:
                edge = prevEdgeDict[edgeIdx]
                srcId = currNodeDict[edge._srcId]._parentNode
                dstId = currNodeDict[edge._dstId]._parentNode

                if srcId != dstId:
                    # create meta edge only if the parent nodes are different, otherwise the edge connects
                    # nodes in the same cluster, which should not be visible
                    newEdgeIdx = str(srcId) + '_' + str(level+1) + '_' + str(dstId) if str(srcId) < str(dstId) else str(dstId) + '_' + str(level+1) + '_' + str(srcId)
                    if newEdgeIdx not in currEdgeDict:
                        currEdgeDict[newEdgeIdx] = self.Edge(_id=newEdgeIdx, _srcId=srcId, _dstId=dstId, _level=level+1)
                        
                    newEdge = currEdgeDict[newEdgeIdx]
                    newEdge._memberEdges.append(edgeIdx)
                    prevEdgeDict[edgeIdx]._parentEdge = newEdgeIdx

                    newEdge._x1 = currNodeDict[srcId]._x
                    newEdge._y1 = currNodeDict[srcId]._y
                    newEdge._x2 = currNodeDict[dstId]._x
                    newEdge._y2 = currNodeDict[dstId]._y

                    # aggregate the required edge attributes as per user specification
                    # HERE

            self.nodeDicts[level+1] = currNodeDict
            self.edgeDicts[level+1] = currEdgeDict

        return self.nodeDicts, self.edgeDicts