from sklearn.cluster import KMeans
import numpy as np
import sys

sys.path.append("..")
from dataStructures import *

class kMeansClustering:
    def __init__(self, randomState, clusterLevels, nodeDict, edgeDict, \
                aggMeasuresNodesFields, aggMeasuresNodesFunctions, aggMeasuresEdgesFields, aggMeasuresEdgesFunctions, \
                rankListNodes_topK, rankListNodes_fields, rankListNodes_orderBy, rankListNodes_order, \
                rankListEdges_topK, rankListEdges_fields, rankListEdges_orderBy, rankListEdges_order):
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
        self.aggMeasuresNodesFields = aggMeasuresNodesFields if aggMeasuresNodesFields[0] != "" else []
        self.aggMeasuresNodesFunctions = aggMeasuresNodesFunctions if aggMeasuresNodesFunctions[0] != "" else []
        self.aggMeasuresEdgesFields = aggMeasuresEdgesFields if aggMeasuresEdgesFields[0] != "" else []
        self.aggMeasuresEdgesFunctions = aggMeasuresEdgesFunctions if aggMeasuresEdgesFunctions != "" else []

        # rankList parameters
        self.rankListNodes_topK = rankListNodes_topK
        self.rankListNodes_fields = rankListNodes_fields
        self.rankListNodes_orderBy = rankListNodes_orderBy
        self.rankListNodes_order = rankListNodes_order

        self.rankListEdges_topK = rankListEdges_topK
        self.rankListEdges_fields = rankListEdges_fields
        self.rankListEdges_orderBy = rankListEdges_orderBy
        self.rankListEdges_order = rankListEdges_order

        # get class definitions for node and edge objects
        nodeAttributes = list(nodeDict[0].__dict__.keys()) + self.aggMeasuresNodesFields
        nodeAttributes = filter(lambda x: x[0] != '_', nodeAttributes)

        edgeAttributes = list(list(edgeDict.values())[0].__dict__.keys()) + self.aggMeasuresEdgesFields
        edgeAttributes = filter(lambda x: x[0] != '_', edgeAttributes)

        # based on the aggregations to be performed on the attributes, 
        # convert the attributes in the original data to the desired form
        # for list and count aggregations - create a set
        # for other numeric aggregations like sum, avg, sqrsum, min, max - init with 0
        # for count aggregation, convert the list back to a number for the aggregated attribute
        # do this for both nodes and edges
        for attr, func in zip(self.aggMeasuresNodesFields, self.aggMeasuresNodesFunctions):
            if func == 'list' or func == 'count':
                # by default, the data is read as a string of ';' separated strings
                for key in self.nodeDicts[0]:
                    node = self.nodeDicts[0][key]
                    strVal = getattr(node, attr, None)
                    strSet = set([str(s) for s in strVal.split(';')])
                    setattr(node, attr, strSet)
            
            elif func == 'sqrsum':
                for key in self.nodeDicts[0]:
                    node = self.nodeDicts[0][key]
                    strNum = getattr(node, attr, None)
                    setattr(node, attr, float(strNum) * float(strNum))

            elif func == 'sum' or func == 'avg' or func == 'min' or func == 'max':
                # func == 'sum' or 'avg' or 'min' or 'max'
                for key in self.nodeDicts[0]:
                    node = self.nodeDicts[0][key]
                    strNum = getattr(node, attr, None)
                    setattr(node, attr, float(strNum))
            
            else:
                pass

        for attr, func in zip(self.aggMeasuresEdgesFields, self.aggMeasuresEdgesFunctions):
            if func == 'list' or func == 'count':
                # by default, the data is read as a string of ';' separated strings
                for key in self.edgeDicts[0]:
                    edge = self.edgeDicts[0][key]
                    strVal = getattr(edge, attr, None)
                    strSet = set([str(s) for s in strVal.split(";")])
                    setattr(edge, attr, strSet)

            elif func == 'sqrsum':
                for key in self.edgeDicts[0]:
                    edge = self.edgeDicts[0][key]
                    strNum = getattr(edge, attr, None)
                    setattr(edge, attr, float(strNum) * float(strNum))

            elif func == 'sum' or func == 'avg' or func == 'min' or func == 'max':
                for key in self.edgeDicts[0]:
                    edge = self.edgeDicts[0][key]
                    strNum = getattr(edge, attr, None)
                    setattr(edge, attr, float(strNum))
            
            else:
                pass

        self.dataStructures = dataStructures(nodeAttributes, edgeAttributes)
        self.Node = self.dataStructures.getNodeClass()
        self.Edge = self.dataStructures.getEdgeClass()

    def run(self):
        self.cluster()
        self.aggregate()

        # for count aggregation, convert the set back to a number for the aggregated attribute
        # for both nodes and edges
        # also, divide by number of child nodes for avg aggregation
        for level in self.nodeDicts:
            nodeDict = self.nodeDicts[level]

            for nodeId in nodeDict:
                node = nodeDict[nodeId]

                for attr,func in zip(self.aggMeasuresNodesFields, self.aggMeasuresNodesFunctions):
                    if func == 'count':
                        valSet = getattr(node, attr)
                        setattr(node, attr, len(valSet))

                    if func == 'avg':
                        val = getattr(node, attr)
                        setattr(node, attr, val / node._memberNodeCount)
        
        for level in self.edgeDicts:
            edgeDict = self.edgeDicts[level]

            for edgeIdx in edgeDict:
                edge = edgeDict[edgeIdx]

                for attr,func in zip(self.aggMeasuresEdgesFields, self.aggMeasuresEdgesFunctions):
                    if func == 'count':
                        valSet = getattr(edge, attr)
                        setattr(edge, attr, len(valSet))

                    if func == 'avg':
                        val = getattr(edge, attr)
                        setattr(edge, attr, val / edge._memberEdgeCount)

        # create rank list with the specified fields and ordered by the specified attribute
        if self.rankListNodes_topK > 0:
            for level in self.nodeDicts:
                nodeDict = self.nodeDicts[level]

                for nodeId in nodeDict:
                    node = nodeDict[nodeId]
                    if getattr(node, 'rankList', None) == None:
                        # create a list to save the rank list for the node
                        # rankList is a list of topk objects - where each object has the specified fields
                        setattr(node, 'rankList', [])

                    rankList = []

                    # while len(rankList) < self.rankList_topK:
                    if level == 0:
                        # for level 0 - the highest zoom level (most detailed level)
                        # there is only going to be one element in the rankList
                        obj = {}
                        for field in self.rankListNodes_fields:
                            obj[field] = getattr(node, field)

                        rankList.append(obj)
                        setattr(node, 'rankList', rankList)

                    else:
                        # iterate over all the children nodes and get the topk objects from them
                        childNodeDict = self.nodeDicts[level-1]
                        for childNodeId in node._memberNodes:
                            childNode = childNodeDict[childNodeId]
                            childRankList = getattr(childNode, 'rankList')
                            rankList.extend(childRankList)

                        # assuming that the rankList_orderBy attribute is also a part of rankListNodes_fields
                        rankList = sorted(rankList, key=lambda x: x[self.rankListNodes_orderBy], reverse=True if self.rankListNodes_order == 'desc' else False)
                        setattr(node, 'rankList', rankList[:self.rankListNodes_topK])

        if self.rankListEdges_topK > 0:
            for level in self.edgeDicts:
                edgeDict = self.edgeDicts[level]

                for edgeIdx in edgeDict:
                    edge = edgeDict[edgeIdx]
                    if getattr(edge, 'rankList', None) == None:
                        # create a list to save the rank list for the node
                        # rankList is a list of topk objects - where each object has the specified fields
                        setattr(edge, 'rankList', [])

                    rankList = []

                    # while len(rankList) < self.rankList_topK:
                    if level == 0:
                        # for level 0 - the highest zoom level (most detailed level)
                        # there is only going to be one element in the rankList
                        obj = {}
                        for field in self.rankListEdges_fields:
                            obj[field] = getattr(edge, field)

                        rankList.append(obj)
                        setattr(edge, 'rankList', rankList)

                    else:
                        # iterate over all the children nodes and get the topk objects from them
                        childEdgeDict = self.edgeDicts[level-1]
                        for childEdgeIdx in edge._memberEdges:
                            childEdge = childEdgeDict[childEdgeIdx]
                            childRankList = getattr(childEdge, 'rankList')
                            rankList.extend(childRankList)

                        # assuming that the rankList_orderBy attribute is also a part of rankListEdges_fields
                        rankList = sorted(rankList, key=lambda x: x[self.rankListEdges_orderBy], reverse=True if self.rankListEdges_order == 'desc' else False)
                        setattr(edge, 'rankList', rankList[:self.rankListEdges_topK])

        # gather aggregated stuff under clusterAgg as JSON string
        for level in self.nodeDicts:
            nodeDict = self.nodeDicts[level]

            for nodeId in nodeDict:
                node = nodeDict[nodeId]

                clusterAgg = {}
                for attr in self.aggMeasuresNodesFields:
                    clusterAgg[attr] = getattr(node, attr)
                    delattr(node, attr)

                if getattr(node, 'rankList', None) != None:
                    clusterAgg['rankList'] = getattr(node, 'rankList')
                    delattr(node, 'rankList')

                setattr(node, 'clusterAgg', clusterAgg)

        for level in self.edgeDicts:
            edgeDict = self.edgeDicts[level]

            for edgeIdx in edgeDict:
                edge = edgeDict[edgeIdx]

                clusterAgg = {}
                for attr in self.aggMeasuresEdgesFields:
                    clusterAgg[attr] = getattr(edge, attr)
                    delattr(edge, attr)

                if getattr(edge, 'rankList', None) != None:
                    clusterAgg['rankList'] = getattr(edge, 'rankList')
                    delattr(edge, 'rankList')

                setattr(edge, 'clusterAgg', clusterAgg)

        return self.nodeDicts, self.edgeDicts

    def cluster(self):
        nodeCounter = 0
        # edgeCounter = 0

        prevNodeCounter = 0

        for level, numMetaNodes in enumerate(self.clusterLevels):
            print("Creating cluster level", level+1)
            prevNodeDict = self.nodeDicts[level]
            
            clustering_input = []
            for nodeId in sorted(prevNodeDict):
                # CAUTION: ensure sorting of node dict keys, because meta nodes created later 
                # are not guaranteed to be created sequentially
                # gather all the node positions for input to clustering
                pos = []
                pos.append(prevNodeDict[nodeId]._x)
                pos.append(prevNodeDict[nodeId]._y)
                clustering_input.append(pos)

            np_clustering_input = np.asarray(clustering_input)
            kmeans = KMeans(n_clusters=numMetaNodes, random_state=self.randomState, algorithm=self.algorithm).fit(np_clustering_input)
            
            nodeCounter += len(prevNodeDict)
            # edgeCounter += len(prevEdgeDict)

            currNodeDict = {}

            # print(len(kmeans.labels_))
            # print(len(kmeans.cluster_centers_))
            # print(np.amax(kmeans.labels_))
            assert (len(kmeans.labels_) == self.nodeCounts[level])
            # assert (kmeans.n_iter_ == 300)
            assert (np.amax(kmeans.labels_) == len(kmeans.cluster_centers_)-1)

            # create the clustered nodes and setup the parent and child relations
            for id,label in enumerate(kmeans.labels_):
                # CAUTION: this order of creation of meta nodes is not sequential
                # meta nodes can be created out of order
                nodeId = nodeCounter + label
                if nodeId not in currNodeDict:
                    currNodeDict[nodeId] = self.Node(_id=nodeId, _x=kmeans.cluster_centers_[label][0], _y=kmeans.cluster_centers_[label][1],\
                                                     _level=level+1, _memberNodes=[], _memberNodeCount=0, _parentNode=-1)
                    
                newNode = currNodeDict[nodeId]
                newNode._memberNodes.append(prevNodeCounter+id)
                prevNodeDict[prevNodeCounter+id]._parentNode = nodeId

            prevNodeCounter += len(prevNodeDict)

            self.nodeDicts[level+1] = currNodeDict
            self.nodeCounts[level+1] = len(currNodeDict)
            assert (len(currNodeDict) == numMetaNodes)

            # create the clustered edges and setup the parent and child relations
            prevEdgeDict = self.edgeDicts[level]
            currEdgeDict = {}

            for edgeIdx in prevEdgeDict:
                edge = prevEdgeDict[edgeIdx]
                srcId = prevNodeDict[edge._srcId]._parentNode
                dstId = prevNodeDict[edge._dstId]._parentNode

                if srcId != dstId:
                    # create meta edge only if the parent nodes are different, otherwise the edge connects
                    # nodes in the same cluster, which should not be visible
                    newEdgeIdx = str(srcId) + '_' + str(level+1) + '_' + str(dstId) if str(srcId) < str(dstId) else str(dstId) + '_' + str(level+1) + '_' + str(srcId)
                    if newEdgeIdx not in currEdgeDict:
                        currEdgeDict[newEdgeIdx] = self.Edge(_id=newEdgeIdx, _srcId=srcId, _dstId=dstId, \
                                                            _x1=currNodeDict[srcId]._x, _y1=currNodeDict[srcId]._y, \
                                                            _x2=currNodeDict[dstId]._x, _y2=currNodeDict[dstId]._y, \
                                                            _level=level+1, _memberEdges=[], _memberEdgeCount=0, _weight=0, _parentEdge='orphan')
                        
                    newEdge = currEdgeDict[newEdgeIdx]
                    newEdge._memberEdges.append(edgeIdx)
                    edge._parentEdge = newEdgeIdx
                    
            self.edgeDicts[level+1] = currEdgeDict
            self.edgeCounts[level+1] = len(currEdgeDict)

    def aggregate(self):
        # at this point, all the nodeDicts and nodeCounts have been populated
        # but only the first edgeDict and edgeCount has been populated
        
        # first aggregate the nodes, starting bottom up from level 1
        # nothing to be aggregated for level 0
        for level in range(1, len(self.clusterLevels)+1):
            nodeDict = self.nodeDicts[level]
            childNodeDict = self.nodeDicts[level-1]

            for nodeId in nodeDict:
                parentNode = nodeDict[nodeId]
                for memberNodeId in parentNode._memberNodes:
                    childNode = childNodeDict[memberNodeId]
                    parentNode._memberNodeCount += childNode._memberNodeCount

                    for attr,func in zip(self.aggMeasuresNodesFields, self.aggMeasuresNodesFunctions):
                        if func == 'list' or func == 'count':
                            if getattr(parentNode, attr, None) == None:
                                # assign an empty set for the attr if nothing is assigned to it
                                setattr(parentNode, attr, set())

                            aggSet = getattr(parentNode, attr)
                            assert (getattr(childNode, attr, None) != None)
                            aggSet = aggSet.union(getattr(childNode, attr))
                            setattr(parentNode, attr, aggSet)

                        elif func == 'min':
                            if getattr(parentNode, attr, None) == None:
                                # assign 0 for attr if nothing is assigned to it
                                setattr(parentNode, attr, 0)

                            val = getattr(parentNode, attr)
                            assert (getattr(childNode, attr, None) != None)
                            val = min(val, getattr(childNode, attr))
                            setattr(parentNode, attr, val)

                        elif func == 'max':
                            if getattr(parentNode, attr, None) == None:
                                # assign 0 for attr if nothing is assigned to it
                                setattr(parentNode, attr, 0)

                            val = getattr(parentNode, attr)
                            assert (getattr(childNode, attr, None) != None)
                            val = max(val, getattr(childNode, attr))
                            setattr(parentNode, attr, val)

                        else:
                            # if func == 'sum' or func == 'avg' or func == 'sqrsum':
                            if getattr(parentNode, attr, None) == None:
                                # assign 0 for attr if nothing is assigned to it
                                setattr(parentNode, attr, 0)

                            val = getattr(parentNode, attr)
                            assert (getattr(childNode, attr, None) != None)
                            val += getattr(childNode, attr)
                            setattr(parentNode, attr, val)

        # now aggregate the edges, starting bottom up from level 1
        # nothing to be aggregated for level 0
        for level in range(1, len(self.clusterLevels)+1):
            edgeDict = self.edgeDicts[level]
            childEdgeDict = self.edgeDicts[level-1]

            for edgeIdx in edgeDict:
                parentEdge = edgeDict[edgeIdx]
                for memberIdx in parentEdge._memberEdges:
                    childEdge = childEdgeDict[memberIdx]
                    parentEdge._memberEdgeCount += childEdge._memberEdgeCount
                    parentEdge._weight += childEdge._weight

                    # aggregate the required edge attributes as per user specification
                    for attr, func in zip(self.aggMeasuresEdgesFields, self.aggMeasuresEdgesFunctions):
                        if func == 'list' or func == 'count':
                            if getattr(parentEdge, attr, None) == None:
                                # assign an empty list for the attr if nothing is assigned to it
                                setattr(parentEdge, attr, set())
                            
                            aggSet = getattr(parentEdge, attr, None)
                            assert (getattr(childEdge, attr, None) != None)
                            aggSet = aggSet.union(getattr(childEdge, attr, None))
                            setattr(parentEdge, attr, aggSet)

                        elif func == 'max':
                            if not getattr(parentEdge, attr, None):
                                # assign '0' for the attr if nothing is assigned to it
                                setattr(parentEdge, attr, 0)

                            val = getattr(parentEdge, attr, None)
                            assert (getattr(childEdge, attr, None) != None)
                            val = max(val, getattr(childEdge, attr, None))
                            setattr(parentEdge, attr, val)

                        elif func == 'min':
                            if not getattr(parentEdge, attr, None):
                                # assign '0' for the attr if nothing is assigned to it
                                setattr(parentEdge, attr, 0)

                            val = getattr(parentEdge, attr, None)
                            assert (getattr(childEdge, attr, None) != None)
                            val = min(val, getattr(childEdge, attr, None))
                            setattr(parentEdge, attr, val)

                        else:
                            # if func == 'sum' or func == 'avg' or func == 'sqrsum':
                            if not getattr(parentEdge, attr, None):
                                # assign '0' for the attr if nothing is assigned to it
                                setattr(parentEdge, attr, 0)

                            val = getattr(parentEdge, attr, None)
                            assert (getattr(childEdge, attr, None) != None)
                            val += getattr(childEdge, attr, None)
                            setattr(parentEdge, attr, val)