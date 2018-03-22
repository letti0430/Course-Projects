# Title: Database
# Project: Shazam
# Author: Sijia Liu
# Date: Dec. 2017

import psycopg2 as psql
import numpy as np
import os
import re
from songClass import Song


class Database:
	"""
	a class that can build a database for songs and querying information"""
	def __init__(self, conn = None, cur = None):

		self.conn = self.connect()
		self.cur = self.conn.cursor()

	def connect(self):
		"""
		connect to the database, and initiate self.conn and self.cur"""
		try:
			conn = psql.connect(dbname="sijial",
								user="sijial",
								password="Cigar077",
								host="sculptor.stat.cmu.edu")
			return conn
		except psql.DatabaseError:
			if conn:
				conn.rollback()
			return None

	def create_table(self):
		"""
		create two tables for a music database

		returns:
			two tables created in the database, one for song_ids and titles,
			the other for entry_id, song_ids and signature

		"""
		drop_tables_query = """
			DROP TABLE IF EXISTS signatures;
			DROP TABLE IF EXISTS songs;
			"""
		create_tables_query = """
			CREATE TABLE IF NOT EXISTS songs (
				id SERIAL PRIMARY KEY,
				title TEXT NOT NULL,
				UNIQUE (id, title)
			);
			CREATE TABLE IF NOT EXISTS signatures (
				entry_id SERIAL PRIMARY KEY,
				song_id INTEGER REFERENCES songs(id),
				signature VARCHAR NOT NULL,
				UNIQUE (entry_id, song_id)
			);
			"""

		self.cur.execute(drop_tables_query)
		self.cur.execute(create_tables_query)
		self.conn.commit()
		self.conn.close()


def build_library(directory):
	"""
	build a music library given a directory path

	params:
		directory: a directory of songs in '.wav' format

	returns:
		True if successful

	"""
	conn = Database().conn
	cur = conn.cursor()

	insert_song_query = """
		INSERT INTO songs (id, title) 
			VALUES (%s, %s) 
		"""
	insert_signature_query = """
		INSERT INTO signatures (entry_id, song_id, signature)
			VALUES (%s, %s, %s)
		"""

	songList = [x for x in os.listdir(directory) if x.endswith(".wav")]
	for i in range(len(songList)):
		cur.execute(insert_song_query, (i, songList[i]))

	entry = 0
	for i in range(len(songList)):
		song = Song(songList[i], directory + songList[i])
		for j in range(len(song.analyzer())):
			signList = song.analyzer()[j].tolist()
			cur.execute(insert_signature_query, (entry, i, signList))
			entry += 1

	conn.commit()
	conn.close()
	return True


def get_song_info(song_id):
	"""
	get all information about the song

	params:
		song_id: the unique id that identifies one song in the database

	returns:
		rst: the information corresponding to the song_id, including song_id, title

	"""
	conn = Database().conn
	cur = conn.cursor()
	cur.execute("SELECT * FROM songs WHERE id = %s;", (song_id,))
	rst = cur.fetchone()
	conn.close()
	return rst


def get_song_signature(entry_id):
	"""
	get a list of signatures for one song in the database

	params:
		entry_id: the entry_id returned by the 'search_nearest' matching process

	returns:
		rst: the song_id and signature corresponding to the entry_id

	"""
	conn = Database().conn
	cur = conn.cursor()

	cur.execute("SELECT song_id, signature FROM signatures WHERE entry_id = %s;", (entry_id,))
	rst = cur.fetchone()
	conn.close()
	return rst


def get_all_signatures():
	"""
	get all signatures in the database, for building a hashtable

	returns:
		all_signatures: an array of all signatures in the database

	"""
	conn = Database().conn
	cur = conn.cursor()
	cur.execute("SELECT signature FROM signatures;")
	signatures_list = cur.fetchall()

	all_signatures = []
	for one in signatures_list:
		one = (re.sub('[{}]','',one[0])).split(',')
		one = [float(x) for x in one]
		all_signatures.append(one)

	# Cast the data for hashing to numpy.float32 to improve performance
	all_signatures = np.asarray(all_signatures, dtype=np.float32)
	
	conn.close()
	return all_signatures


def get_all_songs():
	"""
	get a list of all songs in the database

	returns:
		rst: a list of all songs
	"""
	conn = Database().conn
	cur = conn.cursor()

	cur.execute("SELECT * FROM songs;")
	rst = cur.fetchall()
	conn.close()
	return rst

