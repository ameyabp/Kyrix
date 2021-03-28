docker cp ../../../OpenORD/Clustering/graphNodesData_level_0.csv kyrix_db_1:/graphNodesData_level_0.csv         # copy the csv file to the db container
docker cp ../../../OpenORD/Clustering/graphNodesData_level_1.csv kyrix_db_1:/graphNodesData_level_1.csv
docker cp ../../../OpenORD/Clustering/graphNodesData_level_2.csv kyrix_db_1:/graphNodesData_level_2.csv
docker cp ../../../OpenORD/Clustering/graphEdgesData_level_0.csv kyrix_db_1:/graphEdgesData_level_0.csv         # copy the csv file to the db container
docker cp ../../../OpenORD/Clustering/graphEdgesData_level_1.csv kyrix_db_1:/graphEdgesData_level_1.csv
docker cp ../../../OpenORD/Clustering/graphEdgesData_level_2.csv kyrix_db_1:/graphEdgesData_level_2.csv

docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/postgres -c "CREATE DATABASE graphVis;"
#docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/postgres -c "USE graphvis;"      # connect to recFut database
docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/graphvis -c "DROP TABLE IF EXISTS authorNodes;"
docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/graphvis -c "CREATE TABLE authorNodes(nodeId TEXT, posX FLOAT8, posY FLOAT8, authorName TEXT, affiliation TEXT, paperCount INT, coauthorCount INT, memberNodeCount INT, clusterLevel INT, PRIMARY KEY(nodeId));"
docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/graphvis -c "COPY authorNodes(nodeId, posX, posY, authorName, affiliation, paperCount, coauthorCount, memberNodeCount, clusterLevel) FROM '/graphNodesData_level_0.csv' DELIMITER ',' CSV HEADER;"
docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/graphvis -c "COPY authorNodes(nodeId, posX, posY, authorName, affiliation, paperCount, coauthorCount, memberNodeCount, clusterLevel) FROM '/graphNodesData_level_1.csv' DELIMITER ',' CSV HEADER;"
docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/graphvis -c "COPY authorNodes(nodeId, posX, posY, authorName, affiliation, paperCount, coauthorCount, memberNodeCount, clusterLevel) FROM '/graphNodesData_level_2.csv' DELIMITER ',' CSV HEADER;"

docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/graphvis -c "DROP TABLE IF EXISTS authorEdges;"
docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/graphvis -c "CREATE TABLE authorEdges(edgeId TEXT, x1 FLOAT8, y1 FLOAT8, x2 FLOAT8, y2 FLOAT8, author1 TEXT, author2 TEXT, paperCount INT, clusterLevel INT, PRIMARY KEY(edgeId));"
docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/graphvis -c "COPY authorEdges(edgeId, x1, y1, x2, y2, author1, author2, paperCount, clusterLevel) FROM '/graphEdgesData_level_0.csv' DELIMITER ',' CSV HEADER;"
docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/graphvis -c "COPY authorEdges(edgeId, x1, y1, x2, y2, author1, author2, paperCount, clusterLevel) FROM '/graphEdgesData_level_1.csv' DELIMITER ',' CSV HEADER;"
docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/graphvis -c "COPY authorEdges(edgeId, x1, y1, x2, y2, author1, author2, paperCount, clusterLevel) FROM '/graphEdgesData_level_2.csv' DELIMITER ',' CSV HEADER;"

docker exec -it kyrix_db_1 su - postgres -c "./install-d3.sh graphvis"