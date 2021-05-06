"""
Co-author network graph
Creating a graph dataset of authors as nodes and co-authorship as edges
Each edge would have as its attribute a list of papers coauthored by the connected author nodes
The edges in such a dataset would be undirected unlike a dataset of papers citing each other.
In the latter, papers are nodes and citations are directed edges.

Nodes table:
NodeID | Author Name | Affiliation | Papers | Co-author IDs

Edges table:
EdgeID | Author1Id | Author2Id | Papers 

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

class Node:
    # author
    def __init__(self, id, name, affiliation):
        self.nodeId = id
        self.name = name
        self.affiliation = affiliation
        self.papers = []
        self.coauthors = set()

class Edge:
    # coauthor relationship
    def __init__(self, id, author1Id, author2Id):
        self.edgeId = id
        self.author1Id = author1Id
        self.author2Id = author2Id
        self.weight = 0
        self.papers = []


if __name__ == '__main__':
    # PARSE THE CSV TO EXTRACT REQUIRED DATA
    df = pd.read_csv('/home/ameya/Documents/Kyrix/compiler/examples/graphvis/vispub.csv', dtype={'Conference': str, 'Year': int, 'Title': str, 'AuthorNames': str, 'AuthorAffiliation': str}, na_values=[''])

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
                authorDict[author] = nodeCounter
                node = Node(id=nodeCounter, name=str(author), affiliation=str(affiliation))
                nodeDict[nodeCounter] = node
                nodeCounter += 1
            
            node = nodeDict[authorDict[author]]
            paper = str(row['Title'])
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
                edge = Edge(id=edgeIdx, author1Id=author1Id, author2Id=author2Id)
                edgeDict[edgeIdx] = edge
                edgeCounter += 1

            paper = str(row['Title'])
            edgeDict[edgeIdx].papers.append(paper)
    
    numVertices = len(nodeDict)
    numEdges = len(edgeDict)
    numPapers = len(df)

    # assign edge weights
    for edgeId in edgeDict:
        edge = edgeDict[edgeId]
        author1Id = edge.author1Id
        author2Id = edge.author2Id
        # affinity score is set by the number of papers coauthored together
        affinity_score = len(edge.papers) / numPapers
        # affinity score is further boosted if the authors belong to the same affiliation
        if (nodeDict[author1Id].affiliation == nodeDict[author2Id].affiliation):
            affinity_score = pow(affinity_score, 0.5)

        edge.weight = affinity_score

    print('Number of nodes', numVertices)
    print('Number of edges', numEdges)
    print('Number of papers', numPapers)

    # Create the dataframes
    # node dataframe
    nodeDf = {'nodeId': [], 'authorName': [], 'affiliation': [], 'papers': [], 'coauthors': []}

    for nodeId in nodeDict:
        node = nodeDict[nodeId]
        nodeDf['nodeId'].append(node.nodeId)
        nodeDf['authorName'].append(node.name)
        nodeDf['affiliation'].append(node.affiliation)
        nodeDf['papers'].append(";".join(node.papers))
        coauthorList = [str(i) for i in list(node.coauthors)]
        nodeDf['coauthors'].append(";".join(coauthorList))

    # edge dataframe
    edgeDf = {'edgeId': [], 'weight': [], 'author1': [], 'author2': [], 'papers': []}
    
    for edgeId in edgeDict:
        edge = edgeDict[edgeId]
        edgeDf['edgeId'].append(edge.edgeId)
        edgeDf['weight'].append(edge.weight)
        edgeDf['author1'].append(edge.author1Id)
        edgeDf['author2'].append(edge.author2Id)
        edgeDf['papers'].append(";".join(edge.papers))
    
    df = pd.DataFrame(data=nodeDf)
    with open('graphNodesData.csv', 'w') as g:
        df.to_csv(path_or_buf=g, index=False)
        g.close()

    df = pd.DataFrame(data=edgeDf)
    with open('graphEdgesData.csv', 'w') as g:
        df.to_csv(path_or_buf=g, index=False)
        g.close()
