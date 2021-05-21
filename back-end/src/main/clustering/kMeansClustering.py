from sklearn.cluster import KMeans
import numpy as np
import sys

sys.path.append("..")
from dataStructures import *

class kMeansClustering:
    def __init__(self, randomState, clusterLevels, nodeDict, edgeDict, aggMeasuresNodesFields, aggMeasuresNodesFunctions, aggMeasuresEdgesFields, aggMeasuresEdgesFunctions):
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

        # attributes to aggregate and their corresponding aggregation functions
        self.aggMeasuresNodesFields = aggMeasuresNodesFields
        self.aggMeasuresNodesFunctions = aggMeasuresNodesFunctions
        self.aggMeasuresEdgesFields = aggMeasuresEdgesFields
        self.aggMeasuresEdgesFunctions = aggMeasuresEdgesFunctions

        # get class definitions for node and edge objects
        nodeAttributes = list(nodeDict[0].__dict__.keys()) + self.aggMeasuresNodesFields
        nodeAttributes = filter(lambda x: x[0] != '_', nodeAttributes)

        edgeAttributes = list(list(edgeDict.values())[0].__dict__.keys()) + self.aggMeasuresEdgesFields
        edgeAttributes = filter(lambda x: x[0] != '_', edgeAttributes)

        # based on the attributes to be aggregated as count, convert the attribute values for level 0 elements to a set
        # this is for ease of management down the pipeline
        for attr, func in zip(self.aggMeasuresNodesFields, self.aggMeasuresNodesFunctions):
            if func == 'count':
                # by default, the data is read as a string of ';' separated strings
                for key in self.nodeDicts[0]:
                    node = self.nodeDicts[0][key]
                    strVal = getattr(node, attr, None)
                    strSet = set([str(s) for s in strVal.split(';')])
                    setattr(node, attr, strSet)

        for attr, func in zip(self.aggMeasuresEdgesFields, self.aggMeasuresEdgesFunctions):
            if func == 'count':
                # by default, the data is read as a string of ';' separated strings
                for key in self.edgeDicts[0]:
                    edge = self.edgeDicts[0][key]
                    strVal = getattr(edge, attr, None)
                    strSet = set([str(s) for s in strVal.split(";")])
                    setattr(edge, attr, strSet)

        self.dataStructures = dataStructures(nodeAttributes, edgeAttributes)
        self.Node = self.dataStructures.getNodeClass()
        self.Edge = self.dataStructures.getEdgeClass()

    def run(self):
        nodeCounter = 0
        edgeCounter = 0

        prevNodeCounter = 0

        for level, numMetaNodes in enumerate(self.clusterLevels):
            print("Creating cluster level", level+1)
            prevNodeDict = self.nodeDicts[level]
            prevEdgeDict = self.edgeDicts[level]
            clustering_input = []
            for nodeId in prevNodeDict:
                # gather all the node positions for input to clustering
                pos = []
                pos.append(prevNodeDict[nodeId]._x)
                pos.append(prevNodeDict[nodeId]._y)
                clustering_input.append(pos)

            np_clustering_input = np.asarray(clustering_input)
            kmeans = KMeans(n_clusters=numMetaNodes, random_state=self.randomState, algorithm=self.algorithm).fit(np_clustering_input)
            
            nodeCounter += len(prevNodeDict)
            edgeCounter += len(prevEdgeDict)

            currNodeDict = {}
            currEdgeDict = {}

            for id, label in enumerate(kmeans.labels_):
                nodeId = nodeCounter + label
                if nodeId not in currNodeDict:
                    currNodeDict[nodeId] = self.Node(_id=nodeId, _x=kmeans.cluster_centers_[label][0], _y=kmeans.cluster_centers_[label][1], _level=level+1, _parentNode=-1)
                
                newNode = currNodeDict[nodeId]
                newNode._memberNodes.append(prevNodeCounter + id)
                prevNodeDict[prevNodeCounter + id]._parentNode = nodeId

                # aggregate the required node attributes as per user specification
                for attr, func in zip(self.aggMeasuresNodesFields, self.aggMeasuresNodesFunctions):
                    childNode = prevNodeDict[prevNodeCounter + id]
                    if func == 'count':
                        if not getattr(newNode, attr, None):
                            # assign an empty string for the attr if nothing is assigned to it
                            setattr(newNode, attr, set())
                        
                        aggSet = getattr(newNode, attr, None)
                        assert (getattr(childNode, attr, None) != None)
                        aggSet = aggSet.union(getattr(childNode, attr, None))
                        setattr(newNode, attr, aggSet)

                    if func == 'sum':
                        if not getattr(newNode, attr, None):
                            # assign '0' for the attr if nothing is assigned to it
                            setattr(newNode, attr, 0)

                        sumVar = getattr(newNode, attr, None)
                        assert (getattr(childNode, attr, None) != None)
                        sumVar += float(getattr(childNode, attr, None))
                        setattr(newNode, attr, sumVar)

                    if func == 'sqrsum':
                        if not getattr(newNode, attr, None):
                            # assign '0' for the attr if nothing is assigned to it
                            setattr(newNode, attr, 0)

                        sqrSumVar = getattr(newNode, attr, None)
                        assert (getattr(childNode, attr, None) != None)
                        sqrSumVar += pow(float(getattr(childNode, attr, None)), 2)
                        setattr(newNode, attr, sqrSumVar)

                    if func == 'avg':
                        # TODO: Might be needed to be corrected
                        if not getattr(newNode, attr, None):
                            # assign '0' for the attr if nothing is assigned to it
                            setattr(newNode, attr, 0)

                        avgVar = getattr(newNode, attr, None)
                        assert (getattr(childNode, attr, None) != None)
                        avgVar = (avgVar * (len(newNode._memberNodes) - 1) + float(getattr(childNode, attr, None))) / len(newNode._memberNodes)
                        setattr(newNode, attr, avgVar)

                    if func == 'max':
                        if not getattr(newNode, attr, None):
                            # assign '0' for the attr if nothing is assigned to it
                            setattr(newNode, attr, 0)

                        maxVar = getattr(newNode, attr, None)
                        assert (getattr(childNode, attr, None) != None)
                        maxVar = max(maxVar, float(getattr(childNode, attr, None)))
                        setattr(newNode, attr, maxVar)

                    if func == 'min':
                        if not getattr(newNode, attr, None):
                            # assign '0' for the attr if nothing is assigned to it
                            setattr(newNode, attr, 0)

                        minVar = getattr(newNode, attr, None)
                        assert (getattr(childNode, attr, None) != None)
                        minVar = min(minVar, float(getattr(childNode, attr, None)))
                        setattr(newNode, attr, minVar)

            prevNodeCounter += len(prevNodeDict)

            for edgeIdx in prevEdgeDict:
                edge = prevEdgeDict[edgeIdx]
                srcId = prevNodeDict[edge._srcId]._parentNode
                dstId = prevNodeDict[edge._dstId]._parentNode

                if srcId != dstId:
                    # create meta edge only if the parent nodes are different, otherwise the edge connects
                    # nodes in the same cluster, which should not be visible
                    newEdgeIdx = str(srcId) + '_' + str(level+1) + '_' + str(dstId) if str(srcId) < str(dstId) else str(dstId) + '_' + str(level+1) + '_' + str(srcId)
                    if newEdgeIdx not in currEdgeDict:
                        currEdgeDict[newEdgeIdx] = self.Edge(_id=newEdgeIdx, _srcId=srcId, _dstId=dstId, _level=level+1, \
                                                            _x1=currNodeDict[srcId]._x, _y1=currNodeDict[srcId]._y, \
                                                            _x2=currNodeDict[dstId]._x, _y2=currNodeDict[dstId]._y, _parentEdge='orphan')
                        
                    newEdge = currEdgeDict[newEdgeIdx]
                    newEdge._memberEdges.append(edgeIdx)
                    prevEdgeDict[edgeIdx]._parentEdge = newEdgeIdx
                    newEdge._weight += edge._weight

                    # aggregate the required edge attributes as per user specification
                    for attr, func in zip(self.aggMeasuresEdgesFields, self.aggMeasuresEdgesFunctions):
                        childEdge = edge
                        if func == 'count':
                            if not getattr(newEdge, attr, None):
                                # assign an empty list for the attr if nothing is assigned to it
                                setattr(newEdge, attr, set())
                            
                            aggSet = getattr(newEdge, attr, None)
                            assert (getattr(childEdge, attr, None) != None)
                            aggSet = aggSet.union(getattr(childEdge, attr, None))
                            setattr(newEdge, attr, aggSet)

                        if func == 'sum':
                            if not getattr(newEdge, attr, None):
                                # assign '0' for the attr if nothing is assigned to it
                                setattr(newEdge, attr, 0)

                            sumVar = getattr(newEdge, attr, None)
                            assert (getattr(childEdge, attr, None) != None)
                            sumVar += getattr(childEdge, attr, None)
                            setattr(newEdge, attr, sumVar)

                        if func == 'sqrsum':
                            if not getattr(newEdge, attr, None):
                                # assign '0' for the attr if nothing is assigned to it
                                setattr(newEdge, attr, 0)

                            sqrSumVar = getattr(newEdge, attr, None)
                            assert (getattr(childEdge, attr, None) != None)
                            sqrSumVar += pow(getattr(childEdge, attr, None), 2)
                            setattr(newEdge, attr, sqrSumVar)

                        if func == 'avg':
                            # TODO: Might be needed to be corrected
                            if not getattr(newEdge, attr, None):
                                # assign '0' for the attr if nothing is assigned to it
                                setattr(newEdge, attr, 0)

                            avgVar = getattr(newEdge, attr, None)
                            assert (getattr(childEdge, attr, None) != None)
                            avgVar = (avgVar * (len(newEdge._memberNodes) - 1) + getattr(childEdge, attr, None)) / len(newEdge._memberNodes)
                            setattr(newEdge, attr, avgVar)

                        if func == 'max':
                            if not getattr(newEdge, attr, None):
                                # assign '0' for the attr if nothing is assigned to it
                                setattr(newEdge, attr, 0)

                            maxVar = getattr(newEdge, attr, None)
                            assert (getattr(childEdge, attr, None) != None)
                            maxVar = max(maxVar, getattr(childEdge, attr, None))
                            setattr(newEdge, attr, maxVar)

                        if func == 'min':
                            if not getattr(newEdge, attr, None):
                                # assign '0' for the attr if nothing is assigned to it
                                setattr(newEdge, attr, 0)

                            minVar = getattr(newEdge, attr, None)
                            assert (getattr(childEdge, attr, None) != None)
                            minVar = min(minVar, getattr(childEdge, attr, None))
                            setattr(newEdge, attr, minVar)

            self.nodeDicts[level+1] = currNodeDict
            self.edgeDicts[level+1] = currEdgeDict

        return self.nodeDicts, self.edgeDicts