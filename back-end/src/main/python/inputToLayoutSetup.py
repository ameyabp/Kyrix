import sys, os
import pandas as pd


# sample call: python3 inputToLayoutSetup.py authorshipTest ../../../../OpenORD/graphNodesData_level_0.csv ../../../../OpenORD/graphEdgesData_level_0.csv 1 authorName openORD 1000,500,50 0

if __name__ == "__main__":
    if len(sys.argv) < 9:
        # default 
        print("Not enough arguments")
    else:
        # project name (str)
        project = sys.argv[1]

        # get node and edges file directors
        nodesDir = sys.argv[2] # ../../../../OpenORD/graphNodesData_level_0.csv
        edgesDir = sys.argv[3] # ../../../../OpenORD/graphEdgesData_level_0.csv

        # compute weight or not -> 0 if weight is already there, 1 if we need to compute weight (equal weight for all edges)
        computeWeight = sys.argv[4]

        # get attribute from nodes used for source and target labels, need to create adjacency matrix using node ids specified in nodes
        edgeDataID = sys.argv[5]

        # layout algorithm name (str), one from 'openORD', 'force-directed', TODO: IMPLEMENT MORE LAYOUT ALGORITHMS
        algorithm = sys.argv[6]

        # layout parameters, passed in as a string "0.9,0.3,..." -> list | specific to layout method
        layoutParams = sys.argv[7].split(',')

        # boolean for whether graph is directed or not, 1 if directed, 0 if not
        directed = sys.argv[8]


        # read in edges csv, this is turned into our sparse adjacency matrix
        edges = pd.read_csv(edgesDir, na_values=[''])
        nodes = pd.read_csv(nodesDir, na_values=[''])

        reID = nodes.set_index(edgeDataID).T.to_dict('series')

        if computeWeight == 0:
            edges = edges[['source', 'target', 'weight']]
        else:
            edges = edges[['source', 'target']]
            numRows = len(edges['source'])
            edges['weight'] = 1/numRows
        
        edges['source'] = [reID[s].id for s in edges['source']]
        edges['target'] = [reID[t].id for t in edges['target']]

        print(edges['source'])

        if algorithm == 'openORD':
            with open('../../../../OpenORD/OpenOrd-master/examples/recursive/' + project + '.sim', 'w') as simFile:
                edges.to_csv(path_or_buf=simFile, index=False, header=False, sep='\t')
                simFile.close()
        elif algorithm == 'fm3':
            print('todo')
        else:
            print('please specify a layout algorithm \n')




