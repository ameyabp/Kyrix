from dataStructures import *
from clustering import *

#from sklearn.cluster import KMeans
#from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd
import sys


# sample call: python3 clustering.py authorship ../../../../OpenORD/graphNodesData_level_0.csv ../../../../OpenORD/graphEdgesData_level_0.csv openORD kmeans 1000,500,50 memberNodeCount,paperCount 0.9,0.3 authorName 0





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
        clusterLevels = sys.argv[6].split(',') 

        # clustering parameters, passed in as a string "0.9,0.3,..." -> list | specific to clustering method
        clusterParams = sys.argv[7].split(',') 

        # boolean for whether graph is directed or not, 1 if directed, 0 if not
        directed = sys.argv[8]

        


        # read in layout of nodes and edges from layout algorithm, files are fully processed.

        finalNodes = pd.read_csv('/kyrix/compiler/examples/' + projectName + '/intermediary/layout/' + layoutAlgorithm + "/layoutNodes.csv", sep=',')
        finalEdges = pd.read_csv('/kyrix/compiler/examples/' + projectName + '/intermediary/layout/' + layoutAlgorithm + "/layoutEdges.csv", sep=',')

        # ## commenting out old file from here

        # # read in user input nodes and edges and infer column types
        # inputNodes = pd.read_csv(nodesDir, na_values=[''])
        # inputEdges = pd.read_csv(edgesDir, na_values=[''])

        # # create unique edge id using ordering of 'source' and 'target' nodes 
        # # where the smaller node id comes first and then target id comes next
        # def createUniqueEdgeID(x,y):
        #     if directed == 1: # takes in x,y as source,target so return edge id as such
        #         return x + '_0_' + y

        #     small = x if x < y else y
        #     big = y if y > x else x
        #     return small + '_0_' + big # if they are both equal, result is y_0_x 


        # ### find and remove duplicate edges; may need to aggregate over them? 
        # ### this might be an unnecessary step if duplicate edges are intentional

        # # set of visited edges to remove any duplicate edges that may appear
        # visitedEdges = set()

        # def findDuplicate(x, y):
        #     if directed == 1:
        #         one = x + '_0_' + y
        #         two = x + '_0_' + y
        #     else:
        #         one = x + "_0_" + y
        #         two = y + '_0_' + x
        #     if one in visitedEdges or two in visitedEdges:
        #         return True
        #     visitedEdges.add(one)
        #     return False


        # ### re-id the source and target in layout output to ids used in user input, 
        # ### important for creating unique edge ids
        # reIdEdges = dict(zip(inputNodes['id'].astype(str), inputNodes[edgeDataID]))


        # ### work on creating finalEdges df for finalized lowest level edges

        # # create unique edge id for input edges
        # inputEdges['source_target'] = [createUniqueEdgeID(x, y) for x, y in zip(inputEdges['source'], inputEdges['target'])]

        # layoutEdges['source'] = [reIdEdges[str(x)] for x in layoutEdges['source']]
        # layoutEdges['target'] = [reIdEdges[str(x)] for x in layoutEdges['target']]
        # layoutEdges['source_target'] = [createUniqueEdgeID(x, y) for x, y in zip(layoutEdges['source'], layoutEdges['target'])]
        # layoutEdges = layoutEdges.drop(columns = ['source', 'target'])



        # # merge edges on unique edge id -> we need to keep edges that result from layout since edges may be dropped (???, need to figure this out)
        # #finalEdges = inputEdges
        # finalEdges = pd.merge(inputEdges, layoutEdges, on='source_target')
        # finalEdges = finalEdges.drop_duplicates()


        # ### done with finalEdges for now

        # ### prepare finalNodes df

        # # merge nodes on unique id used for edge endpoints (input nodes merge onto layout nodes to keep new coordinate values)
        # finalNodes = pd.merge(layoutNodes, inputNodes, on='id')

        # # create nodeDict using edgeDataID as index to set x and y coordinates for edges df
        # nodeDict = finalNodes.set_index(edgeDataID).T.to_dict('series')

        # def getX(ID):
        #     return nodeDict[ID].x

        # def getY(ID):
        #     return nodeDict[ID].y

        # # set x and y coordinates in edges df
        # finalEdges['x1'] = [getX(x) for x in finalEdges['source']]
        # finalEdges['y1'] = [getY(y) for y in finalEdges['source']]

        # finalEdges['x2'] = [getX(x) for x in finalEdges['target']]
        # finalEdges['y2'] = [getY(y) for y in finalEdges['target']]

        # # create new node id used specifically for clustering
        # finalNodes = finalNodes.reset_index()
        # finalNodes = finalNodes.rename(columns = {'index' : 'clusterNodeID'})
        # finalNodes['clusterNodeID'] = finalNodes.index

        # ## end commenting out


        ### done preparing finalNodes df
        print(finalEdges.head(6))

        ### Prepare input for clustering algorithm
        nodeAttributes = finalNodes.columns
        edgeAttributes = finalEdges.columns

        ds = dataStructures(nodeAttributes, edgeAttributes)

        Node = ds.getNodeClass()
        Edge = ds.getEdgeClass()

        # map node id to node objects
        clusterNodeDict = {}
        for _, row in finalNodes.iterrows():
            argDict = dict((key, val) for key, val in zip(nodeAttributes, row))
            node = Node(_id = int(row['id']), _x = row['x'], _y = row['y'], _level=0, **argDict)
            clusterNodeDict[node._id] = node
        
        # map edge id to edge objects
        clusterEdgeDict = {}
        for _, row in finalEdges.iterrows():
            argDict = dict((key, val) for key, val in zip(edgeAttributes, row))
            edge = Edge(_id = row['edgeId'], _srcId = int(row['source']), _dstId = int(row['target']), _level = 0, **argDict)
            clusterEdgeDict[edge._id] = edge

        # for _id in clusterNodeDict:
        #     node = clusterNodeDict[_id]
        #     print("Node:", node._id, node.authorName, node.affiliation)
        # print(len(clusterEdgeDict))

        ###### CALL TO CLUSTERING METHOD ######
        if clusterAlgorithm == 'kmeans':
            nodeDict, edgeDict = kMeansClustering(randomState=0, clusterLevels=[1500, 500, 80], nodeDict=clusterNodeDict, edgeDict=clusterEdgeDict)

            # writeToCSV(nodeDict, edgeDict)
