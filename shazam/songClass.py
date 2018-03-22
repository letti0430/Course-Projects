# Title: Song Class
# Project: Shazam
# Author: Sijia Liu
# Date: Dec. 2017

import os
import wave as wv
import numpy as np
import pylab as pl
import scipy.signal as signal

class Song(object):
	"""
	a class that can efficient analyze a '.wav' file, for building a music database"""

	def __init__(self, title = None, path = None, verbose = False):
		"""
		initiate the attributes of a song object

		params:
			title: the song's name ending with '.wav'
			path: the song's path(name) ending with '.wav'
			verbose: False by default
			
			nchannels: 1 = mono, 2 = stereo
			sampWidth: number of frames in each sample
			sampRate: number of frames in each second
			totalFrames: number of frames in this song
			rawWave: a string of all frames in this song
			length: length of this song in seconds
			
		"""

		self.title  = title
		self.path = path
		self.wavData = wv.open(self.path, 'r')

		self.nchannels = self.wavData.getnchannels()
		self.sampWidth = self.wavData.getsampwidth()
		self.sampRate = self.wavData.getframerate()
		self.totalFrames = self.wavData.getnframes()
		self.rawWave = self.wavData.readframes(self.totalFrames)
		self.length = int(self.totalFrames // self.sampRate 
			+ (self.totalFrames % self.sampRate) / self.sampRate)

	def analyzer(self, width = 10, shift = 1, window_type = 'hann'):
		"""
		analyze the signature of a song with windowing and spectral analysis

		params:
			width: the width of windows
			shift: the shift between two windows
			window_type: the function type for windowing

		returns:
			signature: a numpy array of 5000 peaks per window, 
					   serving as the signature of one song

		"""

		totalFrames = self.totalFrames
		channels = self.nchannels
		sampRate = self.sampRate
		rawWave = self.rawWave
		songLength = self.length

		song = np.fromstring(rawWave, dtype = np.short)
		song.shape = -1, 2
		if channels == 2:
			song = np.mean(song.T, axis = 0)

		window = signal.get_window(window_type, sampRate * width)
		window_num = int((totalFrames - sampRate * width) / sampRate)
		window_list = []
		for i in range(0, window_num + 1):
			window_list.append(window * song[i*sampRate: (i+width)*sampRate])

		N = 5000
		signature = []

		for i, window in enumerate(window_list):
			freq_index = signal.argrelextrema(window, np.greater)
			freq_index = freq_index[0].argsort()[-N:][::-1]
			freq_raw = window[freq_index]
			mins = np.min(freq_raw, axis = 0)
			maxs = np.max(freq_raw, axis = 0)
			freq_norm = (freq_raw - mins) / (maxs - mins)
			signature.append(freq_norm)

		return signature


	def metaData(self):
		"""
		get the meta information about a song """

		_metaData = \
		"""
		Title: {}
		Sample Width: {}
		Sample Rate: {}
		N Channels: {}
		N Frames: {}
		""".format(self.title,
					self.sampWidth,
					self.sampRate,
					self.nchannels,
					self.totalFrames)

		return _metaData
    	