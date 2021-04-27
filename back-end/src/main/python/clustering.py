from dataStructures import *

#from sklearn.cluster import KMeans
#from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd
import sys


# sample call: python3 clustering.py authorship ../../../../OpenORD/graphNodesData_level_0.csv ../../../../OpenORD/graphEdgesData_level_0.csv openORD kmeans 1000,500,50 memberNodeCount,paperCount 0.9,0.3 authorName 0

if __name__ == "__main__":
    if len(sys.argv) < 11:
        # default 
        print("Not enough arguments")
    else:
        # project name (str)
        project = sys.argv[1]

        # get node and edges file directors
        nodesDir = sys.argv[2] # ../../../../OpenORD/graphNodesData_level_0.csv
        edgesDir = sys.argv[3] # ../../../../OpenORD/graphEdgesData_level_0.csv

        # layout algorithm name (str), one from 'openORD', 'force-directed', TODO: IMPLEMENT MORE LAYOUT ALGORITHMS
        layout = sys.argv[4]

        # cluster algorithm name (str), one from 'kmeans', 'spectral', TODO: IMPLEMENT MORE CLUSTERING ALGORITHMS
        clusterAlgorithm = sys.argv[5] 

        # number of levels, passed in as a string "1000,500,50,..." -> list
        clusterLevels = sys.argv[6].split(',') 

        # attributes to cluster on passed in as a list (header of attribute) [abc, xyz]
        clusterAttributes = sys.argv[7] 

        # clustering parameters, passed in as a string "0.9,0.3,..." -> list | specific to clustering method
        clusterParams = sys.argv[8].split(',') 

        # get id that edges use for source and target labels
        edgeDataID = sys.argv[9] # e.g. authorName

        # boolean for whether graph is directed or not, 1 if directed, 0 if not
        directed = sys.argv[10]

        


    # read in layout of nodes and edges from layout algorithm TODO: MODIFY FOR MORE ALGORITHMS
    layoutNodes = pd.read_csv('../../../../OpenORD/OpenOrd-master/examples/recursive/authorship.coord', names = ['id', 'x', 'y'], sep='\t', header=None)

    # read in user input nodes and edges and infer column types
    inputNodes = pd.read_csv(nodesDir, na_values=[''])
    inputEdges = pd.read_csv(edgesDir, na_values=[''])

    # create unique edge id using ordering of 'source' and 'target' nodes 
    # where the smaller node id comes first and then target id comes next
    def createUniqueEdgeID(x,y):
        if directed == 1: # takes in x,y as source,target so return edge id as such
            return x + '_0_' + y

        small = x if x < y else y
        big = y if y > x else x
        return small + '_0_' + big # if they are both equal, result is y_0_x 


    ### find and remove duplicate edges; may need to aggregate over them? 
    ### this might be an unnecessary step if duplicate edges are intentional

    # set of visited edges to remove any duplicate edges that may appear
    visitedEdges = set()

    def findDuplicate(x, y):
        if directed == 1:
            one = x + '_0_' + y
            two = x + '_0_' + y
        else:
            one = x + "_0_" + y
            two = y + '_0_' + x
        if one in visitedEdges or two in visitedEdges:
            return True
        visitedEdges.add(one)
        return False


    ### re-id the source and target in layout output to ids used in user input, 
    ### important for creating unique edge ids
    edgeDataID_to_id = dict(zip(inputNodes['id'].astype(str), inputNodes[edgeDataID]))


    ### work on creating finalEdges df for finalized lowest level edges

    # create unique edge id for input edges
    inputEdges['source_target'] = [createUniqueEdgeID(x, y) for x, y in zip(inputEdges['source'], inputEdges['target'])]

    # merge edges on unique edge id
    finalEdges = inputEdges

    ### done with finalEdges for now

    ### prepare finalNodes df

    # merge nodes on unique node id (input nodes merge onto layout nodes to keep new coordinate values)
    finalNodes = pd.merge(layoutNodes, inputNodes, on='id')

    # create nodeDict using edgeDataID as index to set x and y coordinates for edges df
    nodeDict = finalNodes.set_index(edgeDataID).T.to_dict('series')

    def getX(ID):
        return nodeDict[ID].x

    def getY(ID):
        return nodeDict[ID].y

    # set x and y coordinates in edges df
    finalEdges['x1'] = [getX(x) for x in finalEdges['source']]
    finalEdges['y1'] = [getY(x) for x in finalEdges['source']]

    finalEdges['x2'] = [getX(x) for x in finalEdges['target']]
    finalEdges['y2'] = [getY(x) for x in finalEdges['target']]

    # create new node id used specifically for clustering
    finalNodes = finalNodes.reset_index()
    finalNodes = finalNodes.rename(columns = {'index' : 'clusterNodeID'})
    finalNodes['clusterNodeID'] = finalNodes.index

    ### done preparing finalNodes df

    #print(finalEdges.head(5))
