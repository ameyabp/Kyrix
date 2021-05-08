import sys, os, re, subprocess
import pandas as pd


# sample call: python3 inputToLayoutSetup.py authorshipTest ../../../../OpenORD/graphNodesData_level_0.csv ../../../../OpenORD/graphEdgesData_level_0.csv 1 authorName openORD 1000,500,50 0

if __name__ == "__main__":
    if len(sys.argv) < 8:
        # default 
        print("Not enough arguments")
    else:
        # project name (str)
        projectName = sys.argv[1]

        # get node and edges input file directories
        nodesDir = sys.argv[2] # ../../../../OpenORD/graphNodesData_level_0.csv
        edgesDir = sys.argv[3] # ../../../../OpenORD/graphEdgesData_level_0.csv

        # compute weight or not -> 0 if weight is already there, 1 if we need to compute weight (equal weight for all edges)
        computeWeight = sys.argv[4]

        # layout algorithm name (str), one from 'openORD', 'force-directed', TODO: IMPLEMENT MORE LAYOUT ALGORITHMS
        layoutAlgorithm = sys.argv[5]

        # layout parameters, passed in as a string "0.9,0.3,..." -> list | specific to layout method
        layoutParams = sys.argv[6].split(',')

        # boolean for whether graph is directed or not, 1 if directed, 0 if not
        directed = sys.argv[7]


        # read in edges csv, this is turned into our sparse adjacency matrix
        inputEdges = pd.read_csv(edgesDir, na_values=[''])
        inputNodes = pd.read_csv(nodesDir, na_values=[''])

        reID = inputNodes.set_index('id').T.to_dict('series')

        if computeWeight == '0':
            edges = inputEdges[['source', 'target', 'weight']]
        else:
            edges = inputEdges[['source', 'target']]
            edges['weight'] = 1/len(edges['source'])
        
        #edges['source'] = [reID[s].id for s in edges['source']]
        #edges['target'] = [reID[t].id for t in edges['target']]

        if layoutAlgorithm == 'openORD':
            # prepare input as a .sim file (sparse adjacency matrix) for the openORD algorithm in the corresponding folder
            with open('/kyrix/back-end/src/main/layout/OpenOrd-master/examples/recursive/' + projectName + '.sim', 'w') as simFile:
                edges.to_csv(path_or_buf=simFile, index=False, header=False, sep='\t')
                simFile.close()
            
            # use new input and run openORD (bash file)
            print("running openORD...")
            #" -p " + projectName + " -m " + maxLevel + " -s " + startLevel + " -l " + lastCut + " -r " + refineCut + " -f " + finalCut;
            openORD = "./openORD.sh"
            openORD = openORD + " -p " + projectName + " -m " + layoutParams[0] + " -s " + layoutParams[1] + " -l " + layoutParams[2] + " -r " + layoutParams[3] + " -f " + layoutParams[4]
            openORD = openORD.split(" ")
            subprocess.run(openORD, cwd="/kyrix/back-end/src/main/layout/OpenOrd-master/examples/recursive")

            # convert openORD outputs to standardized output (layoutNodes.csv, layoutEdges.csv)
            # nodes part
            #with open('/kyrix/compiler/examples/' + projectName + '/intermediary/layout/' + layoutAlgorithm + "/layoutNodes.csv", 'w') as layoutNodes:
            #    layoutNodes.write("id,x,y")
            #    with open('/kyrix/back-end/src/main/layout/OpenOrd-master/examples/recursive/' + projectName + '.coord', 'r') as openORDNodes:
            #        for line in openORDNodes:
            #            layoutNodes.write(re.sub('\t',',',line))

            # edges part
            #with open('/kyrix/compiler/examples/' + projectName + '/intermediary/layout/' + layoutAlgorithm + "/layoutEdges.csv", 'w') as layoutEdges:
            #    layoutEdges.write("source,target,weight")
            #    with open('/kyrix/back-end/src/main/layout/OpenOrd-master/examples/recursive/' + projectName + '.edges', 'r') as openORDEdges:
            #        for line in openORDEdges:
            #            layoutEdges.write(re.sub('\t',',',line))

            # read in output 
            openORDNodes = pd.read_csv('/kyrix/back-end/src/main/layout/OpenOrd-master/examples/recursive/' + projectName + '.coord', sep = '\t', names = ['id', 'x', 'y'], header=None)
            openORDEdges = pd.read_csv('/kyrix/back-end/src/main/layout/OpenOrd-master/examples/recursive/' + projectName + '.edges', sep = '\t', names = ['source', 'target', 'weight'], header=None)
            
            # normalize x and y coordinates to 0-1
            openORDNodes['x'] = (openORDNodes['x'] - openORDNodes['x'].min())/(openORDNodes['x'].max() - openORDNodes['x'].min())
            openORDNodes['y'] = (openORDNodes['y'] - openORDNodes['y'].min())/(openORDNodes['y'].max() - openORDNodes['y'].min())


            
            openORDNodes.to_csv('/kyrix/compiler/examples/' + projectName + '/intermediary/layout/' + layoutAlgorithm + "/layoutNodes.csv", sep=",", header=None)
            openORDEdges.to_csv('/kyrix/compiler/examples/' + projectName + '/intermediary/layout/' + layoutAlgorithm + '/layoutEdges.csv', sep=",", header=None)

        elif algorithm == 'fm3':
            print('todo')
        else:
            print('please specify a layout algorithm \n')
        





