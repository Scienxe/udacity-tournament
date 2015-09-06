-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament;

CREATE TABLE players (
	id serial primary key,
	name text,
	wins smallint, 
	matches smallint,
	omw smallint
);

-- Recording matches allows checking for rematches
CREATE TABLE matches (
	winner smallint references players(id),
	loser smallint references players(id)
);

