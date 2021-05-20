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
        *)
            echo "Wrong argument name $key"
            exit
            ;;
    esac
done

mkdir -p /kyrix/compiler/examples/$PROJECT_NAME/intermediary/clustering/$CLUSTERING_ALGORITHM/

python3 clusteringWrapper.py $PROJECT_NAME $NODES_CSV $EDGES_CSV $LAYOUT_ALGORITHM $CLUSTERING_ALGORITHM $CLUSTERING_LEVELS $CLUSTERING_PARAMS $AGG_MEASURES_NODES_FIELDS $AGG_MEASURES_NODES_FUNCTIONS $AGG_MEASURES_EDGES_FIELDS $AGG_MEASURES_EDGES_FUNCTIONS $DIRECTED
