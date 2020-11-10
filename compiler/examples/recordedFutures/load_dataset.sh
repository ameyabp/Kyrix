docker cp maryland_coords.csv kyrix_db_1:/maryland_coords.csv         # copy the csv file to the db container

docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/postgres -c "CREATE DATABASE recFut;"      # create database in the db container
#docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/postgres -c "USE recfut;"      # connect to recFut database
docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/recfut -c "DROP TABLE IF EXISTS Facilities;"    # drop table if previously existed
docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/recfut -c "CREATE TABLE Facilities(sid SERIAL, rfId TEXT, type TEXT, name TEXT, latitude FLOAT8, longitude FLOAT8, PRIMARY KEY(sid));"      # create Facilities table in recFut database
docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/recfut -c "COPY Facilities(sid, rfId, type, name, latitude, longitude) FROM '/maryland_coords.csv' DELIMITER ',' CSV HEADER;"      # load data in Facilities table
docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/recfut -c "CREATE TABLE Mini_Facilities(sid SERIAL, rfId TEXT, type TEXT, name TEXT, latitude FLOAT8, longitude FLOAT8, PRIMARY KEY(sid));"      # create Facilities table in recFut database
docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/recfut -c "INSERT INTO Mini_Facilities SELECT * FROM Facilities LIMIT 1000000;"
docker exec -it kyrix_db_1 su - postgres -c "./install-d3.sh recfut"