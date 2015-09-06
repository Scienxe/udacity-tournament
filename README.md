# udacity-tournament

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

Python and PostgreSQL are required. Before a tournament, create a clean database and tables by importing tournament.sql at a PostgreSQL prompt:

		> psql
		=> \i tournament.sql

Then test the tournament by running

		> python tournament_test.py

at a system command prompt. Tests 9 and 10 probe extra credit features.

### update

This resubmission incorporates two changes:
* Remove an unnecessary column from the matches table
* Implement a cursor generator to handle db open/close tasks.

Thanks to the initial reviewer for these suggestions.
