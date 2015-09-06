#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
from contextlib import contextmanager


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


@contextmanager
def get_cursor():
    """Generate a cursor on the database defined in connect(). 

    Yields a cursor or raises an exeption, then handles closing of the cursor
    and connection.

    Thanks to the initial Udacity reviewer for the suggestion on using a
    generator and decorator to handle db connection and closing tasks.
    """
    db = connect()
    c = db.cursor()

    try:
        yield c
    except:
        raise
    else:
        db.commit()
    finally:
        c.close()
        db.close()


def deleteMatches():
    """Remove all the match records from the database."""
    with get_cursor() as c:
        c.execute("DELETE FROM matches;")


def deletePlayers():
    """Remove all the player records from the database."""
    with get_cursor() as c:
        c.execute("DELETE FROM players;")


def countPlayers():
    """Returns the number of players currently registered."""
    with get_cursor() as c:
        c.execute("SELECT COUNT(*) FROM players;")
        count = c.fetchall()

    return count[0][0]


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    with get_cursor() as c:
        c.execute("INSERT INTO players (name, wins, matches, omw) VALUES (%s, 0, 0, 0);", (name, ))


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    with get_cursor() as c:
        c.execute("SELECT * FROM players ORDER BY wins DESC, omw DESC")
        ranks = c.fetchall()

    return [(row[0], row[1], row[2], row[3]) for row in ranks]


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    with get_cursor() as c:
        if loser > -1:
            # Report bye opponent with player id = -1.
            # Only the winner needs updating after a bye.
            c.execute("SELECT wins FROM players WHERE id = %s", (loser, ))
            op_wins = c.fetchall()[0][0]

            c.execute("""UPDATE players SET (wins, matches, omw) = (wins + 1, matches + 1, %s) 
                WHERE id = %s;""", (op_wins, winner))
            c.execute("INSERT INTO matches (winner, loser) VALUES (%s, %s);", (winner, loser))
            c.execute("UPDATE players SET matches = matches + 1 WHERE id = %s;", (loser,))
        else:
            # Don't increment matches for a bye
            c.execute("UPDATE players SET (wins) = (wins + 1) WHERE id = %s;", (winner, ))
 
 
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    If there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    If there are an odd number of players, a player is chosen with the
    least number of wins who has not had a bye yet. That player is assigned
    a bye round, and the remaining players are matched as above.

    If two players would be assigned a rematch, the lower-ranked player is
    swapped with the next player below. If this swap also results in a rematch,
    it is allowed to stand so that both players in the match still have a
    comparable number of wins.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    standings = playerStandings()
    if len(standings) % 2 == 1:
        # Find the player with the fewest wins who has not yet had a bye
        with get_cursor() as c:
            c.execute("""SELECT id, name FROM players 
                WHERE matches = (SELECT MAX(matches) FROM players)
                ORDER BY wins LIMIT 1""")
            (bye_id, bye_name) = c.fetchall()[0]

        # Pull the bye player out of the standings list so they don't get paired
        standings = [x for x in standings if x[0] != bye_id]

        pairings = [(bye_id, bye_name, -1, 'bye')]
    else:
        pairings = []

    # Pair players in standings order; ensures pairing similar number of wins
    for i in range(0, len(standings) - 1, 2):
        p1 = standings[i][0]
        p2 = standings[i+1][0]

        with get_cursor() as c:
            c.execute("""SELECT * FROM matches 
                WHERE (winner = %s AND loser = %s) OR (winner = %s AND loser = %s)""", (p1, p2, p2, p1))
            rematch = c.fetchall()

        # If this would be a rematch, switch p2 with the next player in line.
        # The next player could also be a rematch, but shifting farther 
        # could lead to matching players whose win numbers are not comparable.
        if len(rematch) > 0 and len(standings) > i+2:
            temp = standings[i+1]
            standings[i+1] = standings[i+2]
            standings[i+2] = temp

        pairings.append((standings[i][0], standings[i][1], standings[i+1][0], standings[i+1][1]))

    return pairings

