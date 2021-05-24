#!/bin/bash

PROJECT_NAME=""
NODES_CSV=""
EDGES_CSV=""
LAYOUT_ALGORITHM=""
CLUSTERING_ALGORITHM=""
CLUSTERING_PARAMS=""
CLUSTERING_LEVELS=""
AGG_MEASURES_NODES_FIELDS=""
AGG_MEASURES_NODES_FUNCTIONS=""
AGG_MEASURES_EDGES_FIELDS=""
AGG_MEASURES_EDGES_FUNCTIONS=""
RANKLIST_NODES_TOPK=""
RANKLIST_NODES_FIELDS=""
RANKLIST_NODES_ORDERBY=""
RANKLIST_NODES_ORDER=""
RANKLIST_EDGES_TOPK=""
RANKLIST_EDGES_FIELDS=""
RANKLIST_EDGES_ORDERBY=""
RANKLIST_EDGES_ORDER=""
DIRECTED="0"
while [[ $# -gt 0 ]]
do
    key="$1"
    case $key in
        --projectName)
            PROJECT_NAME="$2"
            shift
            shift
            ;;
        --nodes)
            NODES_CSV="$2"
            shift
            shift
            ;;
        --edges)
            EDGES_CSV="$2"
            shift
            shift
            ;;
        --layoutAlgorithm)
            LAYOUT_ALGORITHM="$2"
            shift
            shift
            ;;
        --clusteringAlgorithm)
            CLUSTERING_ALGORITHM="$2"
            shift
            shift
            ;;
        --clusteringLevels)
            CLUSTERING_LEVELS="$2"
            shift
            shift
            ;;
        --clusteringParams)
            CLUSTERING_PARAMS="$2"
            shift
            shift
            ;;
        --aggMeasuresNodesFields)
            AGG_MEASURES_NODES_FIELDS="$2"
            shift
            shift
            ;;
        --aggMeasuresNodesFunctions)
            AGG_MEASURES_NODES_FUNCTIONS="$2"
            shift
            shift
            ;;
        --aggMeasuresEdgesFields)
            AGG_MEASURES_EDGES_FIELDS="$2"
            shift
            shift
            ;;
        --aggMeasuresEdgesFunctions)
            AGG_MEASURES_EDGES_FUNCTIONS="$2"
            shift
            shift
            ;;
        --directed)
            DIRECTED="$2"
            shift
            shift
            ;;
        --rankList_nodes_topk)
            RANKLIST_NODES_TOPK="$2"
            shift
            shift
            ;;
        --rankList_nodes_fields)
            RANKLIST_NODES_FIELDS="$2"
            shift
            shift
            ;;
        --rankList_nodes_orderBy)
            RANKLIST_NODES_ORDERBY="$2"
            shift
            shift
            ;;
        --rankList_nodes_order)
            RANKLIST_NODES_ORDER="$2"
            shift
            shift
            ;;
        --rankList_edges_topk)
            RANKLIST_EDGES_TOPK="$2"
            shift
            shift
            ;;
        --rankList_edges_fields)
            RANKLIST_EDGES_FIELDS="$2"
            shift
            shift
            ;;
        --rankList_edges_orderBy)
            RANKLIST_EDGES_ORDERBY="$2"
            shift
            shift
            ;;
        --rankList_edges_order)
            RANKLIST_EDGES_ORDER="$2"
            shift
            shift
            ;;

        *)
            echo "Wrong argument name $key"
            exit
            ;;
    esac
done

mkdir -p /kyrix/compiler/examples/$PROJECT_NAME/intermediary/clustering/$CLUSTERING_ALGORITHM/

python3 clusteringWrapper.py --projectName $PROJECT_NAME --nodesDir $NODES_CSV --edgesDir $EDGES_CSV --layoutAlgorithm $LAYOUT_ALGORITHM --clusterAlgorithm $CLUSTERING_ALGORITHM --clusterLevels $CLUSTERING_LEVELS --clusterParams $CLUSTERING_PARAMS --aggMeasuresNodesFields $AGG_MEASURES_NODES_FIELDS --aggMeasuresNodesFunctions $AGG_MEASURES_NODES_FUNCTIONS --aggMeasuresEdgesFields $AGG_MEASURES_EDGES_FIELDS --aggMeasuresEdgesFunctions $AGG_MEASURES_EDGES_FUNCTIONS --directed $DIRECTED --rankListNodesTopK $RANKLIST_NODES_TOPK --rankListNodesFields $RANKLIST_NODES_FIELDS --rankListNodesOrderBy $RANKLIST_NODES_ORDERBY --rankListNodesOrder $RANKLIST_NODES_ORDER --rankListEdgesTopK $RANKLIST_EDGES_TOPK --rankListEdgesFields $RANKLIST_EDGES_FIELDS --rankListEdgesOrderBy $RANKLIST_EDGES_ORDERBY --rankListEdgesOrder $RANKLIST_EDGES_ORDER
