from dataStructures import *
import argparse

#from sklearn.cluster import KMeans
#from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd
import json
import sys

sys.path.append("../clustering")
from kMeansClustering import *

def writeToCSVNodes(nodeDicts, projectName, layoutAlgorithm, clusterAlgorithm, aggMeasuresNodesFields, aggMeasuresNodesFunctions):
    # get random node for attribute headers for csv file
    
    for level in nodeDicts:
        # create dataframe using headers from the node data structure
        nodeDictList = []

        for id in nodeDicts[level]:
            node = nodeDicts[level][id]
            
            # convert the attributes aggregated as set, from python set to json string
            for attr, func in zip(aggMeasuresNodesFields, aggMeasuresNodesFunctions):
                if func == 'list':
                    strList = list(getattr(node, attr))
                    jsonStr = json.dumps(strList)
                    setattr(node, attr, jsonStr)
            
            # convert the memberNodes list attribute to json string
            node._memberNodes = json.dumps(node._memberNodes)

            # convert the rankList to json string
            node._rankList = json.dumps(node._rankList)

            nodeDictList.append(node.__dict__) # append a dictionary of {node attributes -> node values} to our list
        
        # create dataframe from list of dictionaries (i.e. setting up our csv file)
        df = pd.DataFrame.from_dict(nodeDictList, orient='columns')
        fileName = '../../../../compiler/examples/' + projectName + '/intermediary/clustering/' + clusterAlgorithm + "/" + layoutAlgorithm + "_nodes_level_" + str(level) +  ".csv"
        with open(fileName, 'w') as g:
            df.to_csv(path_or_buf=g, index=False)
            g.close()

def writeToCSVEdges(edgeDicts, projectName, layoutAlgorithm, clusterAlgorithm, aggMeasuresEdgesFields, aggMeasuresEdgesFunctions):
    
    for level in edgeDicts:

        edgeDictList = []

        for id in edgeDicts[level]:
            edge = edgeDicts[level][id]

            # convert the attributes aggregated as set, from python set to json string
            for attr, func in zip(aggMeasuresEdgesFields, aggMeasuresEdgesFunctions):
                if func == 'list':
                    strList = list(getattr(edge, attr))
                    jsonStr = json.dumps(strList)
                    setattr(edge, attr, jsonStr)

            # convert the memberEdges list attribute to json string
            edge._memberEdges = json.dumps(edge._memberEdges)

            # convert the rankList to json string
            edge._rankList = json.dumps(edge._rankList)

            edgeDictList.append(edge.__dict__)
        
        df = pd.DataFrame.from_dict(edgeDictList, orient='columns')
        fileName = '../../../../compiler/examples/' + projectName + '/intermediary/clustering/' + clusterAlgorithm + "/" + layoutAlgorithm + "_edges_level_" + str(level) +  ".csv"
        with open(fileName, 'w') as g:
            df.to_csv(path_or_buf=g, index=False)
            g.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--projectName', nargs='?', const="", type=str)
    parser.add_argument('--nodesDir', nargs='?', const="", type=str)
    parser.add_argument('--edgesDir', nargs='?', const="", type=str)
    parser.add_argument('--layoutAlgorithm', nargs='?', const="", type=str)
    parser.add_argument('--clusterAlgorithm', nargs='?', const="", type=str)
    parser.add_argument('--clusterLevels', nargs='?', const="", type=str)
    parser.add_argument('--clusterParams', nargs='?', const="", type=str)
    parser.add_argument('--aggMeasuresNodesFields', nargs='?', const="", type=str, default="")
    parser.add_argument('--aggMeasuresNodesFunctions', nargs='?', const="", type=str, default="")
    parser.add_argument('--aggMeasuresEdgesFields', nargs='?', const="", type=str, default="")
    parser.add_argument('--aggMeasuresEdgesFunctions', nargs='?', const="", type=str, default="")
    parser.add_argument('--directed', nargs='?', const=0, type=int, default=0)
    parser.add_argument('--rankListNodesTopK', nargs='?', const=5, type=int, default=5)
    parser.add_argument('--rankListNodesFields', nargs='?', const="", type=str, default="")
    parser.add_argument('--rankListNodesOrderBy', nargs='?', const="", type=str, default="")
    parser.add_argument('--rankListNodesOrder', nargs='?', const="", type=str, default="")
    parser.add_argument('--rankListEdgesTopK', nargs='?', const=5, type=int, default=5)
    parser.add_argument('--rankListEdgesFields', nargs='?', const="", type=str, default="")
    parser.add_argument('--rankListEdgesOrderBy', nargs='?', const="", type=str, default="")
    parser.add_argument('--rankListEdgesOrder', nargs='?', const="", type=str, default="")
    args = parser.parse_args()


    # project name (str)
    projectName = args.projectName

    # get node and edges file directors
    # TODO: MAY NOT NEED THESE ANYMORE AS LAYOUT PERFORMS ALL NECESSARY JOINS
    nodesDir = args.nodesDir
    edgesDir = args.edgesDir

    # layout algorithm name (str), one from 'openORD', 'force-directed', TODO: IMPLEMENT MORE LAYOUT ALGORITHMS
    layoutAlgorithm = args.layoutAlgorithm

    # cluster algorithm name (str), one from 'kmeans', 'spectral', TODO: IMPLEMENT MORE CLUSTERING ALGORITHMS
    clusterAlgorithm = args.clusterAlgorithm

    # number of levels, passed in as a string "1000,500,50,..." -> list
    clusterLevels = args.clusterLevels
    clusterLevels = [int(i) for i in clusterLevels.split(',')]

    # clustering parameters, passed in as a string "0.9,0.3,..." -> list | specific to clustering method
    clusterParams = args.clusterParams
    clusterParams = [float(i) for i in clusterParams.split(',')]

    # measure attributes to aggregate and the corresponding aggregation functions
    aggMeasuresNodesFields = [s for s in args.aggMeasuresNodesFields.split(',')]
    aggMeasuresNodesFunctions = [s for s in args.aggMeasuresNodesFunctions.split(',')]
    aggMeasuresEdgesFields = [s for s in args.aggMeasuresEdgesFields.split(',')]
    aggMeasuresEdgesFunctions = [s for s in args.aggMeasuresEdgesFunctions.split(',')]

    # boolean for whether graph is directed or not, 1 if directed, 0 if not
    directed = args.directed

    # ranklist parameters
    rankListNodes_topK = args.rankListNodesTopK
    rankListNodes_fields = [s for s in args.rankListNodesFields.split(',')]
    rankListNodes_orderBy = args.rankListNodesOrderBy
    rankListNodes_order = args.rankListNodesOrder

    rankListEdges_topK = args.rankListEdgesTopK
    rankListEdges_fields = [s for s in args.rankListEdgesFields.split(',')]
    rankListEdges_orderBy = args.rankListEdgesOrderBy
    rankListEdges_order = args.rankListEdgesOrder

    # read in layout of nodes and edges from layout algorithm, files are fully processed.
    finalNodes = pd.read_csv('../../../../compiler/examples/' + projectName + '/intermediary/layout/' + layoutAlgorithm + "/layoutNodes.csv", sep=',')
    finalEdges = pd.read_csv('../../../../compiler/examples/' + projectName + '/intermediary/layout/' + layoutAlgorithm + "/layoutEdges.csv", sep=',')


    ### Prepare input for clustering algorithm
    nodeAttributes = finalNodes.columns
    edgeAttributes = finalEdges.columns

    ds = dataStructures(nodeAttributes, edgeAttributes)

    Node = ds.getNodeClass()
    Edge = ds.getEdgeClass()

    # map node id to node objects
    clusterNodeDict = {}
    for _, row in finalNodes.iterrows():
        argDict = dict((key, val) for key, val in zip(nodeAttributes[3:], row[3:]))
        node = Node(_id = int(row['id']), _x = float(row['x']), _y = float(row['y']), _level=0,\
                    _memberNodes=[], _memberNodeCount=1, _parentNode=-1, **argDict)
        clusterNodeDict[node._id] = node
    
    # map edge id to edge objects
    clusterEdgeDict = {}
    for _, row in finalEdges.iterrows():
        argDict = dict((key, val) for key, val in zip(edgeAttributes[8:], row[8:]))
        edge = Edge(_id = row['edgeId'], _srcId = int(row['source']), _dstId = int(row['target']), \
                    _x1 = float(row['x1']), _y1 = float(row['y1']), _x2 = float(row['x2']), _y2 = float(row['y2']), \
                    _level = 0, _memberEdges=[], _memberEdgeCount=1, _weight = float(row['weight']), \
                    _parentEdge = 'orphan', **argDict)
        clusterEdgeDict[edge._id] = edge

    # for _id in clusterNodeDict:
    #     node = clusterNodeDict[_id]
    #     print("Node:", node._id, node.authorName, node.affiliation)
    # print(len(clusterEdgeDict))

    ###### CALL TO CLUSTERING METHOD ######
    if clusterAlgorithm == 'kmeans':
        kmClustering = kMeansClustering(randomState=0, clusterLevels=clusterLevels, nodeDict=clusterNodeDict, edgeDict=clusterEdgeDict, \
                                        aggMeasuresNodesFields=aggMeasuresNodesFields, aggMeasuresNodesFunctions=aggMeasuresNodesFunctions, \
                                        aggMeasuresEdgesFields=aggMeasuresEdgesFields, aggMeasuresEdgesFunctions=aggMeasuresEdgesFunctions, \
                                        rankListNodes_topK=rankListNodes_topK, rankListNodes_fields=rankListNodes_fields, rankListNodes_orderBy=rankListNodes_orderBy, rankListNodes_order=rankListNodes_order, \
                                        rankListEdges_topK=rankListEdges_topK, rankListEdges_fields=rankListEdges_fields, rankListEdges_orderBy=rankListEdges_orderBy, rankListEdges_order=rankListEdges_order)
        nodeDicts, edgeDicts = kmClustering.run()

        writeToCSVNodes(nodeDicts, projectName, layoutAlgorithm, clusterAlgorithm, aggMeasuresNodesFields, aggMeasuresNodesFunctions)
        writeToCSVEdges(edgeDicts, projectName, layoutAlgorithm, clusterAlgorithm, aggMeasuresEdgesFields, aggMeasuresEdgesFunctions)

        print("done with clustering...")

    elif clusterAlgorithm == 'spectral':
        print("To be implemented...")

    else:
        print("Inavlid clustering algorithm")
