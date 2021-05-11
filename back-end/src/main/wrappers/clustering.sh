#!/bin/bash

PROJECT_NAME=""
NODES_CSV=""
EDGES_CSV=""
LAYOUT_ALGORITHM=""
CLUSTERING_ALGORITHM=""
CLUSTERING_PARAMS=""
CLUSTERING_LEVELS=""
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

python3 clusteringWrapper.py $PROJECT_NAME $NODES_CSV $EDGES_CSV $LAYOUT_ALGORITHM $CLUSTERING_ALGORITHM $CLUSTERING_LEVELS $CLUSTERING_PARAMS $DIRECTED
