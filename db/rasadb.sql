use db;

CREATE TABLE users(prolific_id TEXT, name TEXT, time DATETIME);

CREATE TABLE sessiondata(prolific_id TEXT, session_num TEXT, response_type TEXT,
response_value TEXT, time DATETIME);

SET global general_log = 1;
SET global general_log_file='/var/lib/mysql/mysql.log';
SET global log_output = 'file'; 