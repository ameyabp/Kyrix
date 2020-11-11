import graph_tool as gt
from graph_tool.draw import sfdp_layout
import pandas as pd

if __name__ == '__main__':
    with open('fb-wosn-friends.edges', 'r') as f:
        lines = f.readlines()

    # get number of edges and vertices
    statLine = lines[1]
    stats = statLine.split(' ')
    numVertices = int(stats[2])
    numEdges = int(stats[1])

    #print(numVertices, numEdges)

    g = gt.Graph(directed=False)
    g.add_vertex(n=numVertices)
    etimestamp = g.new_ep("int")

    edge_list = []
    for line in lines[2:]:
        edge = line.split(' ')
        vertex1 = int(edge[0]) - 1
        vertex2 = int(edge[1]) - 1
        timestamp = int(edge[3])
        edge_tuple = (vertex1, vertex2, timestamp)
        edge_list.append(edge_tuple)

    g.add_edge_list(edge_list, eprops=[etimestamp])

    print("Added data to graph")
    #print(etimestamp.fa)
    #print(g.get_edges())

    # generate the graph layout
    pos = sfdp_layout(g)
    print("Computed layout")

    # print(pos[0])
    # print(pos[1])
    # print(pos[2])
    # print(pos[63728])
    # print(pos[63729])
    # print(pos[63730])

    # create the dataframe for the nodes along with their generated positions
    # edges will be listed as a tuple of second vertex nodeId and the timestamp associated with the edge
    d = {'nodeId': [], 'edges': [], 'posX': [], 'posY': []}
    
    vertex_dict = {}
    for i in range(numVertices):
        vertex_dict[i] = []

    edges = g.get_edges(eprops=[etimestamp])
    print(edges.shape)
    for edge in edges:
        vertex1 = edge[0]
        vertex2 = edge[1]
        timestamp = edge[2]

        vertex_dict[vertex1].append(edge[1:])

    for vertex1 in vertex_dict:
        d['nodeId'].append(vertex1)
        d['edges'].append(vertex_dict[vertex1])
        d['posX'].append(pos[vertex1][0])
        d['posY'].append(pos[vertex1][1])

    df = pd.DataFrame(data=d)
    with open('graphNodesData.csv', 'w') as f:
        df.to_csv(path_or_buf=f, index=False)
        f.close()

    # create the dataframe for the edges along with the timestamps and src and dst node positions
    d = {'edgeId': [], 'startTimestamp': [], 'endTimestamp': [], 'x1': [], 'y1': [], 'x2': [], 'y2': []}
    edge_dict = {}

    for edge in edges:
        vertex1 = edge[0]
        vertex2 = edge[1]
        timestamp = edge[2]

        edgeId = str(vertex1)+'_'+str(vertex2)
        if edgeId in edge_dict:
            edge_dict[edgeId]['endTimestamp'] = timestamp
        else:
            edge_dict[edgeId] = {'startTimestamp': timestamp, 'endTimestamp': None, 'x1': pos[vertex1][0], 'y1': pos[vertex1][1], 'x2': pos[vertex2][0], 'y2': pos[vertex2][1]}

    for edge in edge_dict:
        d['edgeId'].append(edge)
        d['startTimestamp'].append(edge_dict[edge]['startTimestamp'])
        d['endTimestamp'].append(edge_dict[edge]['endTimestamp'])
        d['x1'].append(edge_dict[edge]['x1'])
        d['y1'].append(edge_dict[edge]['y1'])
        d['x2'].append(edge_dict[edge]['x2'])
        d['y2'].append(edge_dict[edge]['y2'])

    df = pd.DataFrame(data=d)
    with open('graphLinksData.csv', 'w') as g:
        df.to_csv(path_or_buf=g, index=False)
        g.close()