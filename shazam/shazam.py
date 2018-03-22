# Title: Shazam
# Project: Shazam
# Author: Sijia Liu
# Date: Dec. 2017

from songClass import Song
import database as db
from hashing import Hashtable
import os


class Shazam(object):
	"""
	a system that can identify the song given a snippet"""

	def __init__(self, width = 10, shift = 1, window_type = 'hann', verbose = True):
		"""
		initiate a shazam object with user-defined window functions and parameters

		params:
			width: integer, the width of windows for signals
			shift: integer, the distance between two windows
			window_type: string, the type of window will be used for spectral analysis

		"""

		self.width= width
		self.shift = shift
		self.window_type = window_type
		self.verbose = verbose

		# create a database for songs, and an empty hashing table for matching
		self.database = db.Database().create_table()
		self.lsh = Hashtable()


	def insert_songs(self, directory):
		"""
		analyze a new song and add it to the database

		params:
			title: string, the title of the song
			artist: string, the artist of the song
			song_path: string, the path of the song ending with '.wav'

		returns:
			True if successful
			False if not successful

		"""
		if len(directory) == 0:
			raise ValueError("The directory path must not be empty.")

		db.build_library(directory)
		all_signatures = db.get_all_signatures()

		self.lsh.build_lsh(all_signatures)

		if not self.lsh.table or not self.lsh.query_object:
			return False

		return True


	def identify(self, snippet_path, K, threshold):
		"""
		identify the K nearest song(s) that match(es) the snippet

		params:
			snippet_path: string, the path of the snippet ending with '.wav'
			K: the K nearest neighbors of the snippet

		returns:
			ids and titles of the K nearest songs matched;
			min distances of the K nearest songs matched

		"""
		if len(snippet_path) == 0:
			raise ValueError("The snippet_path must not be empty.")
		elif K <= 0:
			raise ValueError("K must be a positive integer.")

		return self.lsh.search_nearest(snippet_path, int(K), threshold)


	def list(self):
		"""
		get a list of all songs in the database"""

		return db.get_all_songs()

