# Title: Testing
# Project: Shazam
# Author: Sijia Liu
# Date: Dec. 2017

import unittest
import os
import re
import random
import struct
import wave as wv
import numpy as np
import scipy.signal as signal
import psycopg2 as psql
import falconn
from pydub import AudioSegment
from songClass import Song
import database as db
from hashing import Hashtable
from shazam import Shazam


class test_shazam(unittest.TestCase):
	"""Unittest cases and randomized tests for shazam"""

	def test_song(self):
		"""test the song class with two random noise waves"""

		writeWav('noise1.wav', 60)
		writeWav('noise2.wav', 50)
		song1 = Song('noise1.wav','noise1.wav')
		song2 = Song('noise2.wav','noise2.wav')
		width = 10

		self.assertEqual(song1.title, 'noise1.wav')
		self.assertEqual(song1.nchannels, 2)
		self.assertEqual(song1.sampWidth, 2)
		self.assertEqual(song1.sampRate, 44100)
		self.assertEqual(song1.sampWidth, 2)
		self.assertEqual(song1.length, 60)

		self.assertEqual(song2.title, 'noise2.wav')
		self.assertEqual(song2.nchannels, 2)
		self.assertEqual(song2.sampWidth, 2)
		self.assertEqual(song2.sampRate, 44100)
		self.assertEqual(song2.sampWidth, 2)
		self.assertEqual(song2.length, 50)

		self.assertEqual(len(song1.analyzer()), song1.length-width+1)  # number of windows in song1
		self.assertEqual(len(song2.analyzer()), song2.length-width+1)
		self.assertEqual(len(song1.analyzer()[0]), 5000)  # number of peaks in each window
		self.assertEqual(len(song2.analyzer()[1]), 5000)


	def test_database(self):
		"""test the database class with two random noise waves"""

		# test create_table
		database = db.Database()
		database.create_table()

		conn = psql.connect(dbname="sijial",
							user="sijial",
							password="Cigar077",
							host="sculptor.stat.cmu.edu")
		cur = conn.cursor()
		cur.execute("SELECT * FROM songs")
		i = cur.fetchone()
		self.assertIsNone(i)

		cur.execute("SELECT * FROM signatures")
		i = cur.fetchone()
		self.assertIsNone(i)

		# test build_library
		self.assertTrue(db.build_library("./"))
		cur.execute("SELECT id, title from songs")
		i = cur.fetchone()
		self.assertEqual(i[0], 0)	# first song_id
		self.assertEqual(i[1], 'noise1.wav')	# first song title

		cur.execute("SELECT * from signatures")
		i = cur.fetchone()
		self.assertEqual(i[0], 0)	# first entry_id
		self.assertEqual(i[1], 0)	# first song_id
		self.assertTrue(len(i[2]) > 0)	# length of first song's all signatures

		# test get_song_info
		rst = db.get_song_info(0)
		self.assertEqual(rst[0], 0)	# first song_id
		self.assertEqual(rst[1], 'noise1.wav')	# first song's title

		# test get_song_signature
		rst = db.get_song_signature(0)
		self.assertEqual(rst[0], 0)	# first song_id

		cur.execute("SELECT * from signatures")
		i = cur.fetchone()
		self.assertEqual(len(rst[1]), len(i[2])) # length of first song's all signatures

		# test get_all_signatures
		all_signatures = db.get_all_signatures()
		self.assertEqual(len(all_signatures[0]), 5000) # length of first signature window


	def test_hashing(self):
		"""test the LSH class with random snippets"""

		Hst = Hashtable()
		self.assertIsNone(Hst.table)
		self.assertIsNone(Hst.query_object)

		# test build_lsh
		database = db.Database()
		database.create_table()
		db.build_library("./")

		all_signatures = db.get_all_signatures()
		Hst.build_lsh(all_signatures)
		self.assertIsNotNone(Hst.table)
		self.assertIsNotNone(Hst.query_object)

		getSnippet('noise1.wav', 'noise1_snippet.wav', 15)
		getSnippet('noise2.wav', 'noise2_snippet.wav', 12)

		self.assertEqual(Hst.search_nearest('noise1_snippet.wav', 1, 0.0001)[0][0], (0, 'noise1.wav'))	# id and title of noise1.wav
		self.assertEqual(Hst.search_nearest('noise1_snippet.wav', 1, 0.0001)[1], [0.])	# distances between noise1.wav and the snippet < 0.0001

		self.assertEqual(Hst.search_nearest('noise2_snippet.wav', 1, 0.0001)[0][0], (1, 'noise2.wav'))	# id of noise2.wav
		self.assertEqual(Hst.search_nearest('noise2_snippet.wav', 1, 0.0001)[1], [0.])	# distances between noise2.wav and the snippet < 0.0001


	def test_shazam(self):
		"""test the shazam with 10 random signatures and one snippet"""

		Shz = Shazam()
		self.assertEqual(Shz.width, 10)
		self.assertEqual(Shz.shift, 1)
		self.assertEqual(Shz.window_type, 'hann')
		self.assertTrue(Shz.verbose)
	
		# test shazam.insert_songs()
		directory = './'

		for f in os.listdir(directory):
			if re.search('snippet.wav', f) or re.search('3.wav', f):
				os.remove(os.path.join(directory, f))

		self.assertTrue(Shz.insert_songs(directory))

		# test shazam.identify() with in-sample snippets
		getSnippet('noise1.wav', 'noise1_snippet.wav', 15)
		getSnippet('noise2.wav', 'noise2_snippet.wav', 12)

		self.assertEqual(Shz.identify('noise1_snippet.wav', 1, 0.0001)[0][0], (0, 'noise1.wav'))	# id and title of noise1.wav
		self.assertEqual(Shz.identify('noise1_snippet.wav', 1, 0.0001)[1], [0.])	# distances from noise1.wav

		self.assertEqual(Shz.identify('noise2_snippet.wav', 1, 0.0001)[0][0], (1, 'noise2.wav'))	# id and title of noise1.wav
		self.assertEqual(Shz.identify('noise2_snippet.wav', 1, 0.0001)[1], [0.])	# distances from noise2.wav

		# test shazam.identify() with out-of-sample snippets
		writeWav('noise3.wav', 55)
		getSnippet('noise3.wav', 'noise3_snippet.wav', 16)
		self.assertIsNone(Shz.identify('noise3_snippet.wav', 1, 0.0001))	# noise3_snippet doesn't match any song in the library

		# test shazam.list()
		self.assertTrue((0, 'noise1.wav') in Shz.list())
		self.assertTrue((1, 'noise2.wav') in Shz.list())
		self.assertFalse((2, 'noise3.wav') in Shz.list())


def writeWav(filename, wave_length):
	"""
	generate random wave files

	params:
		filename: a user-defined file name ending with '.wav'
		wave_length: the length of wave in seconds
	"""
	if not filename.endswith('.wav'):
		raise TypeError("The song must be a .wav file")

	if wave_length == 0:
		raise ValueError("The wave length should not be zero (preferably 30 seconds or more)")

	noise_output = wv.open(filename, 'w')
	noise_output.setparams((2, 2, 44100, 0, 'NONE', 'not compressed'))

	values = []
	SAMPLE_LEN = 44100 * wave_length

	for i in range(0, SAMPLE_LEN):
		value = random.randint(-32767, 32767)
		packed_value = struct.pack('h', value)
		noise_output.writeframes(packed_value)
		noise_output.writeframes(packed_value)

	noise_output.close()


def getSnippet(filename, new_filename, snippet_length):
	"""
	generate snippets from a given .wav file

	params:
		filename: a user-defined file name ending with '.wav'
		wave_length: the length of wave in seconds
	"""
	if not any(x.endswith('.wav') for x in [filename, new_filename]):
		raise TypeError("The original song and the snippet must be a .wav file")

	seg = snippet_length * 1000
	newAudio = AudioSegment.from_wav(filename)
	newAudio = newAudio[:seg]
	newAudio.export(new_filename, format = "wav")


if __name__ == '__main__':
	unittest.main()
