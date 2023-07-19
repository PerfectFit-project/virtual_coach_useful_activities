use db;

CREATE TABLE users(prolific_id TEXT, name TEXT, time DATETIME);

CREATE TABLE sessiondata(prolific_id TEXT, session_num TEXT, response_type TEXT,
response_value TEXT, time DATETIME);
