import sys, subprocess
import pandas as pd
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--projectName', nargs='?', const="", type=str)
    parser.add_argument('--nodesDir', nargs='?', const="", type=str)
    parser.add_argument('--edgesDir', nargs='?', const="", type=str)
    parser.add_argument('--layoutAlgorithm', nargs='?', const="", type=str)
    parser.add_argument('--computeWeight', nargs='?', const=0, type=int, default=0)
    parser.add_argument('--layoutParams', nargs='?', const="", type=str, default="")
    parser.add_argument('--directed', nargs='?', const=0, type=int, default=0)
    args = parser.parse_args()
    
    # project name (str)
    projectName = args.projectName

    # get node and edges input file directories
    nodesDir = args.nodesDir
    edgesDir = args.edgesDir

    # compute weight or not -> 0 if weight is already there, 1 if we need to compute weight (equal weight for all edges)
    computeWeight = args.computeWeight

    # layout algorithm name (str), one from 'openORD', 'force-directed', TODO: IMPLEMENT MORE LAYOUT ALGORITHMS
    layoutAlgorithm = args.layoutAlgorithm

    # layout parameters, passed in as a string "0.9,0.3,..." -> list | specific to layout method
    layoutParams = args.layoutParams

    # boolean for whether graph is directed or not, 1 if directed, 0 if not
    directed = args.directed


    # read in edges csv, this is turned into our sparse adjacency matrix
    inputEdges = pd.read_csv(edgesDir, na_values=[''])
    inputNodes = pd.read_csv(nodesDir, na_values=[''])
    inputNodes = inputNodes.drop(columns = ['x', 'y'], errors='ignore')

    if not 'weight' in inputEdges.columns:
        inputEdges['weight'] = 1/len(inputEdges['source'])

    edges = inputEdges[['source', 'target', 'weight']]
    

    # enter if-else ladder for layout algorithm
    if layoutAlgorithm == 'openORD':
        # prepare input as a .sim file (sparse adjacency matrix) for the openORD algorithm in the corresponding folder
        with open('../layout/OpenOrd-master/examples/recursive/' + projectName + '.sim', 'w') as simFile:
            edges.to_csv(path_or_buf=simFile, index=False, header=False, sep='\t')
            simFile.close()
        
        # use new input and run openORD (bash file)
        print("running openORD...")
        #" -p " + projectName + " -m " + maxLevel + " -s " + startLevel + " -l " + lastCut + " -r " + refineCut + " -f " + finalCut;
        openORD = "./openORD.sh"
        openORD = openORD + " -p " + projectName + " -m " + layoutParams[0] + " -s " + layoutParams[1] + " -l " + layoutParams[2] + " -r " + layoutParams[3] + " -f " + layoutParams[4]
        openORD = openORD.split(" ")
        subprocess.run(openORD, cwd="../layout/OpenOrd-master/examples/recursive")

        # read in output 
        layoutNodes = pd.read_csv('../layout/OpenOrd-master/examples/recursive/' + projectName + '.coord', sep = '\t', names = ['id', 'x', 'y'])
        layoutEdges = pd.read_csv('../layout/OpenOrd-master/examples/recursive/' + projectName + '.edges', sep = '\t', names = ['source', 'target', 'weight'])
        layoutEdges = layoutEdges.drop(columns = ['weight'])

        # normalize x and y coordinates to 0-1
        layoutNodes['x'] = (layoutNodes['x'] - layoutNodes['x'].min())/(layoutNodes['x'].max() - layoutNodes['x'].min())
        layoutNodes['y'] = (layoutNodes['y'] - layoutNodes['y'].min())/(layoutNodes['y'].max() - layoutNodes['y'].min())
        
        # done with layout part, next steps are after if-else ladder
        

    elif layoutAlgorithm == 'fm3':
        print('todo')
    else:
        print('please specify a layout algorithm \n')
    

    # perform join for nodes on 'id' to add node attributes to layout output for finalNodes

    finalNodes = pd.merge(layoutNodes, inputNodes, on='id')

    # create new node ids in case nodes are dropped
    finalNodes = finalNodes.sort_values(['id']) # keeps ids the same if no nodes are dropped
    finalNodes = finalNodes.reset_index(drop=True)
    finalNodes = finalNodes.reset_index()
    finalNodes = finalNodes.rename(columns = {'id' : 'originalID'})
    finalNodes = finalNodes.rename(columns = {'index' : 'id'})
    #finalNodes['clusterNodeID'] = finalNodes.index

    # create finalEdges table

    # create unique edge id using ordering of 'source' and 'target' nodes 
    # where the smaller node id comes first and then target id comes next
    def createUniqueEdgeID(x,y):
        if directed == 1: # takes in x,y as source,target so return edge id as such
            return x + '_0_' + y
        small = x if x < y else y
        big = y if y > x else x
        return str(small) + '_0_' + str(big) # if they are both equal, result is y_0_x 

    # create unique edge ids to perform join on edges for a final edges table (in case edges are dropped)
    inputEdges['source_target'] = [createUniqueEdgeID(x, y) for x, y in zip(inputEdges['source'], inputEdges['target'])]
    layoutEdges['source_target'] = [createUniqueEdgeID(x, y) for x, y in zip(layoutEdges['source'], layoutEdges['target'])]
    layoutEdges = layoutEdges.drop(columns = ['source', 'target'])

    # merge edges on unique edge id -> we need to keep edges that result from layout since edges may be dropped (???, need to figure this out)
    finalEdges = pd.merge(inputEdges, layoutEdges, on='source_target')
    finalEdges = finalEdges.drop_duplicates()
    finalEdges = finalEdges.drop(columns = ['source_target'])

    # create mapping of originalID -> new id + other values
    nodeDict = finalNodes.set_index('originalID').T.to_dict('series')

    # create getters
    def getX(ID):
        return nodeDict[ID].x

    def getY(ID):
        return nodeDict[ID].y

    # set x and y coordinates in edges df
    finalEdges['x1'] = [getX(x) for x in finalEdges['source']]
    finalEdges['y1'] = [getY(y) for y in finalEdges['source']]

    finalEdges['x2'] = [getX(x) for x in finalEdges['target']]
    finalEdges['y2'] = [getY(y) for y in finalEdges['target']]

    # reset ids for source and target to new node ids
    finalEdges['source'] = [nodeDict[source].id for source in finalEdges['source']]
    finalEdges['target'] = [nodeDict[target].id for target in finalEdges['target']]

    # reset source_target in finalEdges
    finalEdges['edgeId'] = [createUniqueEdgeID(x, y) for x, y in zip(finalEdges['source'], finalEdges['target'])]
    # finalEdges['originalID'] = finalEdges['edgeId']
    
    
    # finalEdges['originalID'] = finalEdges.originalID.astype(str)
    # finalNodes['originalID'] = finalNodes.originalID.astype(str)

    # drop unneeded columns
    finalNodes = finalNodes.drop(columns = ['originalID'])

    # reorder columns so necessary columns come first
    nodesNeeded = ['id', 'x', 'y']
    newNodesColumns = nodesNeeded + (finalNodes.columns.drop(nodesNeeded).tolist())
    finalNodes = finalNodes[newNodesColumns]

    edgesNeeded = ['edgeId', 'source', 'target', 'x1', 'y1', 'x2', 'y2', 'weight']
    newEdgesColumns = edgesNeeded + (finalEdges.columns.drop(edgesNeeded).tolist())
    finalEdges = finalEdges[newEdgesColumns]

    # write layout nodes to corresponding folder, unique to project name and layout algorithm 
    # output file name is standard
    finalNodes.to_csv('../../../../compiler/examples/' + projectName + '/intermediary/layout/' + layoutAlgorithm + "/layoutNodes.csv", sep=",", index=False)
    finalEdges.to_csv('../../../../compiler/examples/' + projectName + '/intermediary/layout/' + layoutAlgorithm + '/layoutEdges.csv', sep=",", index=False)
    

