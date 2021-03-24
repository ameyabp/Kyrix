docker cp graphNodesData.csv kyrix_db_1:/graphNodesData.csv         # copy the csv file to the db container
docker cp graphEdgesData.csv kyrix_db_1:/graphEdgesData.csv         # copy the csv file to the db container

docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/postgres -c "CREATE DATABASE coauthor_graph;"
#docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/postgres -c "USE recfut;"      # connect to recFut database
docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/coauthor_graph -c "DROP TABLE IF EXISTS authorNodes;"
docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/coauthor_graph -c "CREATE TABLE authorNodes(nodeId TEXT, authorName TEXT, affiliation TEXT, paperCount INT, coauthorCount INT, memberNodeCount INT, PRIMARY KEY(nodeId));"
docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/coauthor_graph -c "COPY authorNodes(nodeId, authorName, affiliation, paperCount, coauthorCount, memberNodeCount) FROM '/graphNodesData.csv' DELIMITER ',' CSV HEADER;"

docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/coauthor_graph -c "DROP TABLE IF EXISTS authorEdges;"
docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/coauthor_graph -c "CREATE TABLE authorEdges(edgeId TEXT, author1 TEXT, author2 TEXT, paperCount INT, PRIMARY KEY(edgeId));"
docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/coauthor_graph -c "COPY authorEdges(edgeId, author1, author2, paperCount) FROM '/graphEdgesData.csv' DELIMITER ',' CSV HEADER;"

docker exec -it kyrix_db_1 su - postgres -c "./install-d3.sh coauthor_graph"