# Title: Hashing
# Project: Shazam
# Author: Sijia Liu
# Date: Dec. 2017

import numpy as np
import falconn
from songClass import Song
import database as db

import wave as wv
from pydub import AudioSegment
import os
import re
import random
import struct


class Hashtable:
	"""
	a class that can build hash table for efficient signal searching and matching"""

	def __init__(self):
		
		self.table = None
		self.query_object = None

	def build_lsh(self, all_signatures):
		"""
		take signatures of songs to build a LSH table, and the query object

		params:
			all_signatures: all signatures from the database
		
		returns:
			a falconn hash table;
			a pointer pointing to the falconn hash table
			None if not successful

		"""
		
		if all_signatures.shape[0] == 0:
			raise ValueError("All signatures must not be empty.")

		params = falconn.get_default_parameters(all_signatures.shape[0], all_signatures.shape[1])

		# center the dataset to improve performance: 
		all_signatures -= np.mean(all_signatures, axis=0)

		# Create the LSH table
		print('Constructing the LSH table...')		
		table = falconn.LSHIndex(params)
		table.setup(all_signatures)

		print('Constructing the queries...')		
		query_object = table.construct_query_object()

		self.table = table
		self.query_object = query_object
		
		if not table or not query_object:
			return None


	def search_nearest(self, snippet_path, K, threshold):
		"""
		search for the K nearest songs for the given snippet

		params:
			snippet_path: the snippet path ending with '.wav'
			K: the number of song(s) that match(es) the snippet
			threshold: the min distance should be no larger than the threshold
		
		returns:
			k_min_songs_info: ids and titles of the K nearest songs matched
			k_min_distances: min distances of the K nearest songs matched
			None if not matched

		"""

		query_object = self.query_object

		snippet = Song('snippet', snippet_path)
		snippet_signature = snippet.analyzer()
		snippet_signature = np.asarray(snippet_signature, dtype=np.float32)

		k_nearest = []
		for line in snippet_signature:
			k_nearest.append(query_object.find_k_nearest_neighbors(line, K))

		distances = []
		matched_songs_id = []

		for i, value in enumerate(k_nearest):
			entry_id = value[0]
			matched_songs_id.append(db.get_song_signature(entry_id)[0])

			signature_string = db.get_song_signature(entry_id)[1]
			matched_signature = (re.sub('[{}]','',signature_string)).split(',')
			matched_signature = [float(x) for x in matched_signature]
			matched_signature = np.asarray(matched_signature, dtype=np.float32)

			distances.append(np.sum(snippet_signature[i] - matched_signature)**2)

		distances = np.asarray(distances)
		k_min_distances_idx = distances.argsort()[:K]
		k_min_distances = distances[k_min_distances_idx]

		if min(k_min_distances) > threshold:
			print("The snippet doesn't match any song in our library!")
			return None

		k_min_songs_info = []

		for i in k_min_distances_idx:
			k_min_songs_info.append(db.get_song_info(matched_songs_id[i]))

		return k_min_songs_info, k_min_distances
