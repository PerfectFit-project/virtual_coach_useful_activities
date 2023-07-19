use db;

CREATE TABLE users(idx INT NOT NULL AUTO_INCREMENT, prolific_id TEXT, name TEXT, time DATETIME, CONSTRAINT users_pk PRIMARY KEY (idx)));

CREATE TABLE sessiondata(idx INT NOT NULL AUTO_INCREMENT, prolific_id TEXT, session_num TEXT, response_type TEXT,
response_value TEXT, time DATETIME, CONSTRAINT sessiondata_pk PRIMARY KEY (idx));

SET global general_log = 1;
SET global general_log_file='/var/log/mysql/mysql.log';
SET global log_output = 'file'; 
