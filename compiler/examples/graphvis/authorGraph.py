"""
Co-author network graph
Creating a graph dataset of authors as nodes and co-authored papers as edges.
The edges in such a dataset would be undirected unlike a dataset of papers citing each other.
In the latter, papers are nodes and citations are directed edges.

Nodes table:
NodeID | Author Name | Affiliation | Paper count | Co-author count

Edges table:
EdgeID | Paper name | Author1 | Author2 | Author count | Conference name | Year

The vispub dataset has the data for 3109 papers, with following schema
0 - Conference
1 - Year
2 - Title
3 - AuthorNames
4 - AuthorAffiliation

"""

import pandas as pd
from itertools import combinations
import graph_tool as gt
from graph_tool.draw import sfdp_layout

class Author:
    # node
    def __init__(self, id, name, affiliation):
        self.nodeId = id
        self.name = name
        self.affiliation = affiliation
        self.paperCount = 0
        self.coauthors = set()

class Paper:
    # edge
    def __init__(self, id, title, author1, author2, authorCount, conferenceName, year):
        self.edgeId = id
        self.title = title
        self.author1 = author1
        self.author2 = author2
        self.authorCount = authorCount
        self.conferenceName = conferenceName
        self.year = year

if __name__ == '__main__':
    # PARSE THE CSV TO EXTRACT REQUIRED DATA
    df = pd.read_csv('vispub.csv', dtype={'Conference': str, 'Year': int, 'Title': str, 'AuthorNames': str, 'AuthorAffiliation': str}, na_values=[''])
    df.AuthorAffiliation.astype(str)

    # gather nodes and index by author name
    nodeDict = {}

    for idx, row in df.iterrows():
        authorList = row['AuthorNames'].split(';')
        cleanedAuthorList = ["".join(filter(lambda x: not x.isdigit(), author)) for author in authorList]

        affiliationList = str(row['AuthorAffiliation']).split(';')

        for idx, author in enumerate(cleanedAuthorList):
            affiliation = affiliationList[idx] if idx < len(affiliationList) else ''
            if author not in nodeDict:
                node = Author(id=len(nodeDict), name=author, affiliation=affiliation)
                nodeDict[author] = node
            
            nodeDict[author].paperCount += 1
            for coauthor in cleanedAuthorList:
                if coauthor != author:
                    nodeDict[author].coauthors.add(coauthor)

    # gather edges and index by edgeId
    edgeDict = {}

    edgeCounter = 0
    for idx, row in df.iterrows():
        authorList = row['AuthorNames'].split(';')
        cleanedAuthorList = ["".join(filter(lambda x: not x.isdigit(), author)) for author in authorList]

        pairs = combinations(cleanedAuthorList, 2)

        for pair in pairs:
            edgeDict[edgeCounter] = Paper(id=edgeCounter, title=row['Title'], author1=pair[0], author2=pair[1], authorCount=len(authorList), conferenceName=row['Conference'], year=row['Year'])
            edgeCounter += 1


    numVertices = len(nodeDict)
    numEdges = len(edgeDict)
    print('Number of nodes', numVertices)
    print('Number of edges', numEdges)

    # GENERATE LAYOUT FOR THE GRAPH
    # create graph object
    g = gt.Graph(directed=False)

    # add node and edge attributes to the graph
    nAuthorName = g.new_vertex_property("string")
    nAffiliation = g.new_vertex_property("string")
    nPaperCount = g.new_vertex_property("int")
    nCoauthorConut = g.new_vertex_property("int")

    ePaperName = g.new_edge_property("string")
    eAuthorCount = g.new_edge_property("int")
    eConferenceName = g.new_edge_property("string")
    eYear = g.new_edge_property("int")

    # create edge list for providing to the graph tool sfdp_layout API
    edgeList = []
    for edge in list(edgeDict.values()):
        edgeTuple = (nodeDict[edge.author1].nodeId, nodeDict[edge.author2].nodeId, edge.title, edge.authorCount, edge.conferenceName, edge.year)
        edgeList.append(edgeTuple)

    g.add_vertex(n=numVertices)
    g.add_edge_list(edgeList, eprops=[ePaperName, eAuthorCount, eConferenceName, eYear])

    # generate the graph layout
    pos = sfdp_layout(g)

    # node dataframe
    nodeDf = {'nodeId': [], 'posX': [], 'posY': [], 'authorName': [], 'affiliation': [], 'paperCount': [], 'coauthorCount': []}

    # prepare the node dataframe
    for node in list(nodeDict.values()):
        nodeDf['nodeId'].append(node.nodeId)
        nodeDf['posX'].append(pos[node.nodeId][0])
        nodeDf['posY'].append(pos[node.nodeId][1])
        nodeDf['authorName'].append(node.name)
        nodeDf['affiliation'].append(node.affiliation)
        nodeDf['paperCount'].append(node.paperCount)
        nodeDf['coauthorCount'].append(len(node.coauthors))

    
    # edge dataframe
    edgeDf = {'edgeId': [], 'x1': [], 'y1': [], 'x2': [], 'y2': [], 'paperName': [], 'author1': [], 'author2': [], 'authorCount': [], 'conferenceName': [], 'year': []}
    
    for edge in list(edgeDict.values()):
        edgeDf['edgeId'].append(edge.edgeId)
        edgeDf['x1'].append(pos[nodeDict[edge.author1].nodeId][0])
        edgeDf['x2'].append(pos[nodeDict[edge.author1].nodeId][1])
        edgeDf['y1'].append(pos[nodeDict[edge.author2].nodeId][0])
        edgeDf['y2'].append(pos[nodeDict[edge.author2].nodeId][1])
        edgeDf['paperName'].append(edge.title)
        edgeDf['author1'].append(edge.author1)
        edgeDf['author2'].append(edge.author2)
        edgeDf['authorCount'].append(edge.authorCount)
        edgeDf['conferenceName'].append(edge.conferenceName)
        edgeDf['year'].append(edge.year)

    # IMPLEMENT LEVEL 1 CANVAS OF GRAPH VIZ (ONE LEVEL OF CLUSTERING)
    # SIMPLE GREEDY CLUSTERING BASED ON PAPER COUNT OF AUTHOR
    sortedNodeDict = dict(sorted(nodeDict.items(), key=lambda x: x[1].paperCount, reverse=True))

