docker cp graphNodesData.csv kyrix_db_1:/graphNodesData.csv         # copy the csv file to the db container
docker cp graphLinksData.csv kyrix_db_1:/graphLinksData.csv         # copy the csv file to the db container

docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/postgres -c "CREATE DATABASE graphVis;"      # create database in the db container
#docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/postgres -c "USE recfut;"      # connect to recFut database
docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/graphvis -c "DROP TABLE IF EXISTS fbfriendsNodes;"    # drop table if previously existed
docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/graphvis -c "CREATE TABLE fbfriendsNodes(nodeId SERIAL, edges TEXT, posX FLOAT8, posY FLOAT8, PRIMARY KEY(nodeId));"      # create Facilities table in recFut database
docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/graphvis -c "COPY fbfriendsNodes(nodeId, edges, posX, posY) FROM '/graphNodesData.csv' DELIMITER ',' CSV HEADER;"      # load data in Facilities table

docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/graphvis -c "DROP TABLE IF EXISTS fbfriendsEdges;"    # drop table if previously existed
docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/graphvis -c "CREATE TABLE fbfriendsEdges(edgeId TEXT, startTimestamp FLOAT8, endTimestamp FLOAT8, x1 FLOAT8, y1 FLOAT8, x2 FLOAT8, y2 FLOAT8, PRIMARY KEY(edgeId));"      # create Facilities table in recFut database
docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/graphvis -c "COPY fbfriendsEdges(edgeId, startTimestamp, endTimestamp, x1, y1, x2, y2) FROM '/graphLinksData.csv' DELIMITER ',' CSV HEADER;"      # load data in Facilities table

docker exec -it kyrix_db_1 su - postgres -c "./install-d3.sh graphvis"