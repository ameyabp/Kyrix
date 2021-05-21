from dataStructures import *

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
            
            # convert the attributes aggregated as count, from python set to json string
            for attr, func in zip(aggMeasuresNodesFields, aggMeasuresNodesFunctions):
                if func == 'count':
                    strList = list(getattr(node, attr))
                    jsonStr = json.dumps(strList)
                    setattr(node, attr, jsonStr)
            
            node._memberNodes = json.dumps(node._memberNodes)

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

            # convert the attributes aggregated as count, from python set to json string
            for attr, func in zip(aggMeasuresEdgesFields, aggMeasuresEdgesFunctions):
                if func == 'count':
                    strList = list(getattr(edge, attr))
                    jsonStr = json.dumps(strList)
                    setattr(edge, attr, jsonStr)

            edge._memberEdges = json.dumps(edge._memberEdges)

            edgeDictList.append(edge.__dict__)
        
        df = pd.DataFrame.from_dict(edgeDictList, orient='columns')
        fileName = '../../../../compiler/examples/' + projectName + '/intermediary/clustering/' + clusterAlgorithm + "/" + layoutAlgorithm + "_edges_level_" + str(level) +  ".csv"
        with open(fileName, 'w') as g:
            df.to_csv(path_or_buf=g, index=False)
            g.close()


if __name__ == "__main__":
    if len(sys.argv) < 9:
        # default 
        print("Not enough arguments")
    else:
        # project name (str)
        projectName = sys.argv[1]

        # get node and edges file directors
        # TODO: MAY NOT NEED THESE ANYMORE AS LAYOUT PERFORMS ALL NECESSARY JOINS
        nodesDir = sys.argv[2] # ../../../../OpenORD/graphNodesData_level_0.csv
        edgesDir = sys.argv[3] # ../../../../OpenORD/graphEdgesData_level_0.csv

        # layout algorithm name (str), one from 'openORD', 'force-directed', TODO: IMPLEMENT MORE LAYOUT ALGORITHMS
        layoutAlgorithm = sys.argv[4]

        # cluster algorithm name (str), one from 'kmeans', 'spectral', TODO: IMPLEMENT MORE CLUSTERING ALGORITHMS
        clusterAlgorithm = sys.argv[5] 

        # number of levels, passed in as a string "1000,500,50,..." -> list
        clusterLevels = [int(i) for i in sys.argv[6].split(',')]

        # clustering parameters, passed in as a string "0.9,0.3,..." -> list | specific to clustering method
        clusterParams = [float(i) for i in sys.argv[7].split(',')]

        # measure attributes to aggregate and the corresponding aggregation functions
        aggMeasuresNodesFields = [s for s in sys.argv[8].split(',')]
        aggMeasuresNodesFunctions = [s for s in sys.argv[9].split(',')]
        aggMeasuresEdgesFields = [s for s in sys.argv[10].split(',')]
        aggMeasuresEdgesFunctions = [s for s in sys.argv[11].split(',')]

        # boolean for whether graph is directed or not, 1 if directed, 0 if not
        directed = sys.argv[12]

        


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
            node = Node(_id = int(row['id']), _x = float(row['x']), _y = float(row['y']), _level=0, **argDict)
            clusterNodeDict[node._id] = node
        
        # map edge id to edge objects
        clusterEdgeDict = {}
        for _, row in finalEdges.iterrows():
            argDict = dict((key, val) for key, val in zip(edgeAttributes[8:], row[8:]))
            edge = Edge(_id = row['edgeId'], _srcId = int(row['source']), _dstId = int(row['target']), _x1 = float(row['x1']), _y1 = float(row['y1']), _x2 = float(row['x2']), _y2 = float(row['y2']), _weight = float(row['weight']), _level = 0, **argDict)
            clusterEdgeDict[edge._id] = edge

        # for _id in clusterNodeDict:
        #     node = clusterNodeDict[_id]
        #     print("Node:", node._id, node.authorName, node.affiliation)
        # print(len(clusterEdgeDict))

        ###### CALL TO CLUSTERING METHOD ######
        if clusterAlgorithm == 'kmeans':
            kmClustering = kMeansClustering(randomState=0, clusterLevels=clusterLevels, nodeDict=clusterNodeDict, edgeDict=clusterEdgeDict, aggMeasuresNodesFields=aggMeasuresNodesFields, aggMeasuresNodesFunctions=aggMeasuresNodesFunctions, aggMeasuresEdgesFields=aggMeasuresEdgesFields, aggMeasuresEdgesFunctions=aggMeasuresEdgesFunctions)
            nodeDicts, edgeDicts = kmClustering.run()

            writeToCSVNodes(nodeDicts, projectName, layoutAlgorithm, clusterAlgorithm, aggMeasuresNodesFields, aggMeasuresNodesFunctions)
            writeToCSVEdges(edgeDicts, projectName, layoutAlgorithm, clusterAlgorithm, aggMeasuresEdgesFields, aggMeasuresEdgesFunctions)

            print("done with clustering...")

        elif clusterAlgorithm == 'spectral':
            print("To be implemented...")

        else:
            print("Inavlid clustering algorithm")
