#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    db = connect()
    c = db.cursor()
    c.execute("DELETE FROM matches;")
    db.commit()
    db.close()


def deletePlayers():
    """Remove all the player records from the database."""
    db = connect()
    c = db.cursor()
    c.execute("DELETE FROM players;")
    db.commit()
    db.close()


def countPlayers():
    """Returns the number of players currently registered."""
    db = connect()
    c = db.cursor()
    c.execute("SELECT COUNT(*) FROM players;")
    count = c.fetchall()
    db.close()

    return count[0][0]


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    db = connect()
    c = db.cursor()
    c.execute("INSERT INTO players (name, wins, matches, omw) VALUES (%s, 0, 0, 0);", (name, ))
    db.commit()
    db.close()


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
    db = connect()
    c = db.cursor()
    c.execute("SELECT * FROM players ORDER BY wins DESC, omw DESC")
    ranks = c.fetchall()
    db.close()

    return [(row[0], row[1], row[2], row[3]) for row in ranks]


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    db = connect()
    c = db.cursor()
    
    if loser > -1:
        # Report bye opponent with player id = -1.
        # Only the winner needs updating after a bye.
        c.execute("SELECT wins FROM players WHERE id = %s", (loser, ))
        op_wins = c.fetchall()[0][0]

        c.execute("""UPDATE players SET (wins, matches, omw) = (wins + 1, matches + 1, %s) 
            WHERE id = %s;""", (op_wins, winner))
        c.execute("INSERT INTO matches (p1, p2, winner) VALUES (%s, %s, %s);", (winner, loser, winner))
        c.execute("UPDATE players SET matches = matches + 1 WHERE id = %s;", (loser,))
    else:
        # Don't increment matches for a bye
        c.execute("UPDATE players SET (wins) = (wins + 1) WHERE id = %s;", (winner, ))

    db.commit()
    db.close()
 
 
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    standings = playerStandings()
    db = connect()
    c = db.cursor()

    if len(standings) % 2 == 1:
        # Find the player with the fewest wins who has not yet had a bye
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

        c.execute("""SELECT * FROM matches 
            WHERE (p1 = %s AND p2 = %s) OR (p1 = %s AND p2 = %s)""", (p1, p2, p2, p1))
        rematch = c.fetchall()

        # If this would be a rematch, switch p2 with the next player in line.
        # The next player could also be a rematch, but shifting farther 
        # could lead to matching players whose win numbers are not comparable.
        if len(rematch) > 0 and len(standings) > i+2:
            temp = standings[i+1]
            standings[i+1] = standings[i+2]
            standings[i+2] = temp

        pairings.append((standings[i][0], standings[i][1], standings[i+1][0], standings[i+1][1]))

    db.close()

    return pairings

