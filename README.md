# udacity-swiss-tournament

This project implements a Swiss tournament in Python and PostgreSQL. Three of the
extra credit features are implemented:
* Attempt to prevent rematches without matching players too far apart in number of wins.
* Allow an odd number of players by allowing one bye per round to a player near the bottom of the ranks. No player can get more than one bye per tournament.
* Rank players with the same number of wins by Opponent Match Wins (OMW).

The project consists of three files:
* tournament.py implements the tournament
* tournament.sql creates the database tables
* tournament_test.py runs unit tests on tournament.py

## how-to

Python and PostgreSQL are required. Before the first tournament, create the necessary database tables by importing tournament.sql at a PostgreSQL prompt:

		> psql
		=> create database tournament
		=> \c tournament
		=> \i tournament.sql

Then test the tournament by running

		> python tournament_test.py

at a system command prompt. Tests 9 and 10 probe extra credit features.
