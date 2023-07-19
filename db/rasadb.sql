use db;

CREATE TABLE users(idx INT NOT NULL AUTO_INCREMENT, prolific_id TEXT, name TEXT, time DATETIME);

CREATE TABLE sessiondata(idx INT NOT NULL AUTO_INCREMENT, prolific_id TEXT, session_num TEXT, response_type TEXT,
response_value TEXT, time DATETIME);
