# read in json from gephi

import json
import pandas as pd

l0 = open('./gephi_graphs/openORD_l0_weighted.json')
l1 = open('./gephi_graphs/openORD_l1.json')
l2 = open('./gephi_graphs/openORD_l2.json')
l3 = open('./gephi_graphs/openORD_l3.json')

data_l0 = json.load(l0)
data_l1 = json.load(l1)
data_l2 = json.load(l2)
data_l3 = json.load(l3)

# Create the dataframes
# node dataframe
nodeDf = {'nodeId': [], 'posX': [], 'posY': [], 'authorName': [], 'affiliation': [], 'paperCount': [], 'coauthorCount': [], 'memberNodeCount': [], 'clusterLevel': []}
id_to_coord = {}

for node in data_l0['nodes']:
    #node = nodeDict[nodeId]
    nodeDf['nodeId'].append(node['id'])
    nodeDf['posX'].append(node['x'])
    nodeDf['posY'].append(node['y'])
    nodeDf['authorName'].append(node['attributes']['authorname'])
    try:
        nodeDf['affiliation'].append(node['attributes']['affiliation'])
    except:
        nodeDf['affiliation'].append('N/A')
    nodeDf['paperCount'].append(int(node['attributes']['papercount']))
    nodeDf['coauthorCount'].append(int(node['attributes']['coauthorcount']))
    nodeDf['memberNodeCount'].append(int(node['attributes']['membernodecount']))
    nodeDf['clusterLevel'].append(node['attributes']['clusterlevel'])
    id_to_coord[node['id']] = [node['x'], node['y']]
    
for node in data_l1['nodes']:
    #node = nodeDict[nodeId]
    nodeDf['nodeId'].append(node['id'])
    nodeDf['posX'].append(node['x'])
    nodeDf['posY'].append(node['y'])
    nodeDf['authorName'].append(node['attributes']['authorname'])
    try:
        nodeDf['affiliation'].append(node['attributes']['affiliation'])
    except:
        nodeDf['affiliation'].append('N/A')
    nodeDf['paperCount'].append(int(node['attributes']['papercount']))
    nodeDf['coauthorCount'].append(int(node['attributes']['coauthorcount']))
    nodeDf['memberNodeCount'].append(int(node['attributes']['membernodecount']))
    nodeDf['clusterLevel'].append(node['attributes']['clusterlevel'])
    id_to_coord[node['id']] = [node['x'], node['y']]
    
for node in data_l2['nodes']:
    #node = nodeDict[nodeId]
    nodeDf['nodeId'].append(node['id'])
    nodeDf['posX'].append(node['x'])
    nodeDf['posY'].append(node['y'])
    nodeDf['authorName'].append(node['attributes']['authorname'])
    try:
        nodeDf['affiliation'].append(node['attributes']['affiliation'])
    except:
        nodeDf['affiliation'].append('N/A')
    nodeDf['paperCount'].append(int(node['attributes']['papercount']))
    nodeDf['coauthorCount'].append(int(node['attributes']['coauthorcount']))
    nodeDf['memberNodeCount'].append(int(node['attributes']['membernodecount']))
    nodeDf['clusterLevel'].append(node['attributes']['clusterlevel'])
    id_to_coord[node['id']] = [node['x'], node['y']]
    
for node in data_l3['nodes']:
    #node = nodeDict[nodeId]
    nodeDf['nodeId'].append(node['id'])
    nodeDf['posX'].append(node['x'])
    nodeDf['posY'].append(node['y'])
    nodeDf['authorName'].append(node['attributes']['authorname'])
    try:
        nodeDf['affiliation'].append(node['attributes']['affiliation'])
    except:
        nodeDf['affiliation'].append('N/A')
    nodeDf['paperCount'].append(int(node['attributes']['papercount']))
    nodeDf['coauthorCount'].append(int(node['attributes']['coauthorcount']))
    nodeDf['memberNodeCount'].append(int(node['attributes']['membernodecount']))
    nodeDf['clusterLevel'].append(node['attributes']['clusterlevel'])
    id_to_coord[node['id']] = [node['x'], node['y']]

# edge dataframe
edgeDf = {'edgeId': [], 'x1': [], 'y1': [], 'x2': [], 'y2': [], 'author1': [], 'author2': [], 'paperCount': [], 'clusterLevel': []}

for edge in data_l0['edges']:
    edgeDf['edgeId'].append(edge['attributes']['edgeid'])
    edgeDf['x1'].append(id_to_coord[edge['source']][0])
    edgeDf['y1'].append(id_to_coord[edge['source']][1])
    edgeDf['x2'].append(id_to_coord[edge['target']][0])
    edgeDf['y2'].append(id_to_coord[edge['target']][1])
    edgeDf['author1'].append(edge['source'])
    edgeDf['author2'].append(edge['target'])
    edgeDf['paperCount'].append(int(edge['attributes']['papercount']))
    edgeDf['clusterLevel'].append(edge['attributes']['clusterlevel'])

for edge in data_l1['edges']:
    edgeDf['edgeId'].append(edge['attributes']['edgeid'])
    edgeDf['x1'].append(id_to_coord[edge['source']][0])
    edgeDf['y1'].append(id_to_coord[edge['source']][1])
    edgeDf['x2'].append(id_to_coord[edge['target']][0])
    edgeDf['y2'].append(id_to_coord[edge['target']][1])
    edgeDf['author1'].append(edge['source'])
    edgeDf['author2'].append(edge['target'])
    edgeDf['paperCount'].append(int(edge['attributes']['papercount']))
    edgeDf['clusterLevel'].append(edge['attributes']['clusterlevel'])
    
for edge in data_l2['edges']:
    edgeDf['edgeId'].append(edge['attributes']['edgeid'])
    edgeDf['x1'].append(id_to_coord[edge['source']][0])
    edgeDf['y1'].append(id_to_coord[edge['source']][1])
    edgeDf['x2'].append(id_to_coord[edge['target']][0])
    edgeDf['y2'].append(id_to_coord[edge['target']][1])
    edgeDf['author1'].append(edge['source'])
    edgeDf['author2'].append(edge['target'])
    edgeDf['paperCount'].append(int(edge['attributes']['papercount']))
    edgeDf['clusterLevel'].append(edge['attributes']['clusterlevel'])
    
for edge in data_l3['edges']:
    edgeDf['edgeId'].append(edge['attributes']['edgeid'])
    edgeDf['x1'].append(id_to_coord[edge['source']][0])
    edgeDf['y1'].append(id_to_coord[edge['source']][1])
    edgeDf['x2'].append(id_to_coord[edge['target']][0])
    edgeDf['y2'].append(id_to_coord[edge['target']][1])
    edgeDf['author1'].append(edge['source'])
    edgeDf['author2'].append(edge['target'])
    edgeDf['paperCount'].append(int(edge['attributes']['papercount']))
    edgeDf['clusterLevel'].append(edge['attributes']['clusterlevel'])


df = pd.DataFrame(data=nodeDf)
with open('kyrixGraphNodesData_f.csv', 'w') as g:
    df.to_csv(path_or_buf=g, index=False)
    g.close()

df = pd.DataFrame(data=edgeDf)
with open('kyrixGraphEdgesData_f.csv', 'w') as g:
    df.to_csv(path_or_buf=g, index=False)
    g.close()
