"""
Co-author network graph
Creating a graph dataset of authors as nodes and co-authorship as edges
Each edge would have as its attribute a list of papers coauthored by the connected author nodes
The edges in such a dataset would be undirected unlike a dataset of papers citing each other.
In the latter, papers are nodes and citations are directed edges.

Nodes table:
NodeID | Author Name | Affiliation | Paper count | Co-author count | Member Node Count | Cluster Level

Edges table:
EdgeID | Paper name | Author1 | Author2 | Paper count | Is Meta Edge

The vispub dataset has the data for 3109 papers, with following schema
0 - Conference
1 - Year
2 - Title
3 - AuthorNames
4 - AuthorAffiliation

"""

import pandas as pd
from itertools import combinations
import random
import pickle

from authorGraphDefs import *

# class Node:
#     # author
#     def __init__(self, id, name, affiliation):
#         self.nodeId = id
#         self.name = name
#         self.affiliation = affiliation
#         self.papers = []
#         self.coauthors = set()
#         self.parentMetaNode = {}    # a dict to record the parent meta node for each visualized cluster level {1: nodeId, 2: nodeID2, 3:}
#         self.clusterLevel = 0
#         self.memberNodes = set()
#         # index everything using the node and edge IDs
#         # node position
#         self.x = 0
#         self.y = 0

# class Edge:
#     # coauthor relationship
#     def __init__(self, id, author1, author2, clusterLevel=0):
#         self.edgeId = id
#         self.author1Id = author1
#         self.author2Id = author2
#         self.papers = []
#         self.clusterLevel = clusterLevel
#         # edge position
#         self.x1 = 0
#         self.y1 = 0
#         self.x2 = 0
#         self.y2 = 0

# class Paper:
#     # attribute of edge
#     def __init__(self, title, authors, conferenceName, year):
#         self.paperTitle = title
#         self.authors = authors
#         self.conferenceName = conferenceName
#         self.year = year

if __name__ == '__main__':
    # PARSE THE CSV TO EXTRACT REQUIRED DATA
    df = pd.read_csv('/home/ameya/Documents/Kyrix/compiler/examples/graphvis/vispub.csv', dtype={'Conference': str, 'Year': int, 'Title': str, 'AuthorNames': str, 'AuthorAffiliation': str}, na_values=[''])
    df.AuthorAffiliation.astype(str)

    # gather nodes and index by node id
    nodeDict = {}
    # maintain a separate dict to map authors to node ids
    authorDict = {}

    nodeCounter = 0
    for ridx, row in df.iterrows():
        authorList = row['AuthorNames'].split(';')
        cleanedAuthorList = ["".join(filter(lambda x: not x.isdigit(), author)) for author in authorList]

        affiliationList = str(row['AuthorAffiliation']).split(';')

        for idx, author in enumerate(cleanedAuthorList):
            affiliation = affiliationList[idx] if idx < len(affiliationList) else ''
            if author not in authorDict:
                node = Node(id=nodeCounter, name=author, affiliation=affiliation)
                node.memberNodes.add(nodeCounter)   # add its own node ID as a member node ID
                # for a node, its level 0 parent does not mean anything, no node on level 0 is a parent
                nodeDict[nodeCounter] = node
                authorDict[author] = nodeCounter
                nodeCounter += 1
            
            node = nodeDict[authorDict[author]]
            paper = Paper(title=row['Title'], authors=cleanedAuthorList, conferenceName=row['Conference'], year=row['Year'])
            node.papers.append(paper)

    # add coauthors as node IDs for all authors
    for ridx, row in df.iterrows():
        authorList = row['AuthorNames'].split(';')
        cleanedAuthorList = ["".join(filter(lambda x: not x.isdigit(), author)) for author in authorList]

        for idx, author in enumerate(cleanedAuthorList):   
            node = nodeDict[authorDict[author]]     
            for coauthor in cleanedAuthorList:
                if coauthor != author:
                    node.coauthors.add(authorDict[coauthor])

    # gather edges and index by author names
    # author1 + '_' + author2
    edgeDict = {}

    edgeCounter = 0
    for ridx, row in df.iterrows():
        authorList = row['AuthorNames'].split(';')
        cleanedAuthorList = ["".join(filter(lambda x: not x.isdigit(), author)) for author in authorList]

        pairs = combinations(cleanedAuthorList, 2)

        for pair in pairs:
            author1Id = authorDict[pair[0]]
            author2Id = authorDict[pair[1]]
            # these are level 0 edges
            edgeIdx = str(author1Id) + '_0_' + str(author2Id) if str(author1Id) < str(author2Id) else str(author2Id) + '_0_' + str(author1Id)

            if edgeIdx not in edgeDict:
                edge = Edge(id=edgeIdx, author1=author1Id, author2=author2Id)
                edgeDict[edgeIdx] = edge
                edgeCounter += 1

            paper = Paper(title=row['Title'], authors=cleanedAuthorList, conferenceName=row['Conference'], year=row['Year'])
            edgeDict[edgeIdx].papers.append(paper)

    numVertices = len(nodeDict)
    numEdges = len(edgeDict)
    numPapers = len(df)
    print('Number of nodes', numVertices)
    print('Number of edges', numEdges)
    print('Number of papers', numPapers)

    # Create the dataframes
    # node dataframe
    nodeDf = {'nodeId': [], 'authorName': [], 'affiliation': [], 'paperCount': [], 'coauthorCount': [], 'memberNodeCount': []}

    for nodeId in nodeDict:
        node = nodeDict[nodeId]
        nodeDf['nodeId'].append(node.nodeId)
        nodeDf['authorName'].append(node.name)
        nodeDf['affiliation'].append(node.affiliation)
        nodeDf['paperCount'].append(int(len(node.papers)))
        nodeDf['coauthorCount'].append(int(len(node.coauthors)))
        nodeDf['memberNodeCount'].append(int(len(node.memberNodes)))

    # edge dataframe
    edgeDf = {'edgeId': [], 'author1': [], 'author2': [], 'paperCount': []}
    
    for edgeId in edgeDict:
        edge = edgeDict[edgeId]
        edgeDf['edgeId'].append(edge.edgeId)
        edgeDf['author1'].append(nodeDict[edge.author1Id].name)
        edgeDf['author2'].append(nodeDict[edge.author2Id].name)
        edgeDf['paperCount'].append(int(len(edge.papers)))
    
    df = pd.DataFrame(data=nodeDf)
    with open('graphNodesData.csv', 'w') as g:
        df.to_csv(path_or_buf=g, index=False)
        g.close()

    df = pd.DataFrame(data=edgeDf)
    with open('graphEdgesData.csv', 'w') as g:
        df.to_csv(path_or_buf=g, index=False)
        g.close()
