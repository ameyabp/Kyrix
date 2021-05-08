#!/bin/bash

PROJECT_NAME=""
NODES_CSV=""
EDGES_CSV=""
ALGORITHM=""
LAYOUT_PARAMS=""
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
        --algorithm)
            ALGORITHM="$2"
            shift
            shift
            ;;
        --layoutParams)
            LAYOUT_PARAMS="$2"
            shift
            shift
            ;;
        *)
            echo "Wrong argument name $key"
            exit
            ;;
    esac
done

mkdir -p /kyrix/compiler/examples/$PROJECT_NAME/intermediary/layout/$ALGORITHM/

python3 layoutWrapper.py $PROJECT_NAME $NODES_CSV $EDGES_CSV 0 $ALGORITHM $LAYOUT_PARAMS 0
