#!/bin/bash

# copy OpenORD-master to docker
docker cp ./OpenORD-master kyrix_kyrix_1:/

# make clean and make
docker exec -it kyrix_kyrix_1 sh -c "cd /OpenOrd-master/src/ && make clean && make"
