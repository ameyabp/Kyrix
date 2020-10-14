docker cp ../../../back-end/maryland_coords.csv kyrix_db_1:/maryland_coords.csv         # copy the csv file to the db container
docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/postgres -c "CREATE DATABASE recFut;"      # create database in the db container
#docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/postgres -c "USE recfut;"      # connect to recFut database
docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/recfut -c "DROP TABLE IF EXISTS Facilities;"    # drop table if previously existed
docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/recfut -c "CREATE TABLE Facilities(sid SERIAL, rfId TEXT, type TEXT, name TEXT, lat FLOAT8, lng FLOAT8, PRIMARY KEY(sid));"      # create Facilities table in recFut database
docker exec -it kyrix_db_1 psql postgresql://postgres:kyrixftw@localhost/recfut -c "COPY Facilities(sid, rfId, type, name, lat, lng) FROM '/maryland_coords.csv' DELIMITER ',' CSV HEADER;"      # load data in Facilities table
