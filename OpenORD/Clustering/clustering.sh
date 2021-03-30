#!/bin/bash

LEVELS=""
while [[ $# -gt 0 ]]
do
    key="$1"
    case $key in
        -c|--clusterLevels)
            LEVELS="$2"
            shift
            shift
            ;;
        *)
            echo "Wrong argument name $key"
            exit
            ;;
    esac
done

python3 kMeansClusteringIterative.py $LEVELS
