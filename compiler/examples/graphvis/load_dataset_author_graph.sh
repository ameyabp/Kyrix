docker cp graphNodesData.csv kyrix_db_1:/graphNodesData.csv         # copy the csv file to the db container
docker cp graphEdgesData.csv kyrix_db_1:/graphEdgesData.csv         # copy the csv file to the db container

docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/postgres -c "CREATE DATABASE graphVis;"
#docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/postgres -c "USE recfut;"      # connect to recFut database
docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/graphvis -c "DROP TABLE IF EXISTS authorNodes;"
docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/graphvis -c "CREATE TABLE authorNodes(nodeId SERIAL, posX FLOAT8, posY FLOAT8, authorName TEXT, affiliation TEXT, paperCount INT, coauthorCount INT, memberNodeCount INT, clusterLevel INT, PRIMARY KEY(nodeId));"
docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/graphvis -c "COPY authorNodes(nodeId, posX, posY, authorName, affiliation, paperCount, coauthorCount, memberNodeCount, clusterLevel) FROM '/graphNodesData.csv' DELIMITER ',' CSV HEADER;"

docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/graphvis -c "DROP TABLE IF EXISTS authorEdges;"
docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/graphvis -c "CREATE TABLE authorEdges(edgeId SERIAL, x1 FLOAT8, y1 FLOAT8, x2 FLOAT8, y2 FLOAT8, author1 TEXT, author2 TEXT, paperCount INT, clusterLevel INT, PRIMARY KEY(edgeId));"
docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/graphvis -c "COPY authorEdges(edgeId, x1, y1, x2, y2, author1, author2, paperCount, clusterLevel) FROM '/graphEdgesData.csv' DELIMITER ',' CSV HEADER;"

docker exec -it kyrix_db_1 su - postgres -c "./install-d3.sh graphvis"