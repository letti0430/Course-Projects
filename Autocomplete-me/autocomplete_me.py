# Title: Autocomplete-me
# Course: 36-650
# Author: Sijia Liu

import heapq
import sys


class Node:
	'''Node class for creating Trie.

	Attributes:
		word -- word stored in the node, none by default
		weight -- weight of word stored in the node, -1 by default
	    maxWeight -- max weight of words in the node's children, -1 by default
	    children -- dict for all children nodes
	'''
	def __init__(self, word = None, weight = -1):
		self.word = word
		self.isWord = False
		self.weight = weight
		self.maxWeight = -1
		self.children = {}

	def __lt__(self, other):
		'''less-than comparison between two nodes'''
		if self.maxWeight >= other.maxWeight:
			return True
		return False


class Trie:
	'''Trie class consisting of nodes.

	Attributes:
		root -- empty node where Trie begins
	'''
	def __init__(self):
		self.root = Node()

	def insert(self, node):
		# insert a node to the trie'''
		current = self.root
		word = node.word

		for letter in word:
			# store the max weight among all the nodes within this subtree
			if current.maxWeight < node.weight:
				current.maxWeight = node.weight
			
			if letter not in current.children:
				current.children[letter] = Node()
			
			current = current.children[letter]

		# add weights to the node when the loop ends	
		current.word = word
		current.isWord = True
		current.weight = node.weight

	def search(self, string):
		# given a string, find the node containing the string
		current = self.root
		string = str(string)

		for letter in string:
			if letter not in current.children:
				return None
			current = current.children[letter]
		return current


def read_terms(file):
	'''
	given a text file, construct a trie'''
	trie = Trie()

	if len(str(file).strip())==0:
		raise ValueError("Argument must be a valid text file.")

	with open(file, 'r') as txt:
		next(txt)
		for line in txt:
			if line != '\n':
				item = line.strip().split('\t')
				trie.insert(Node(weight=int(item[0]), word=item[1]))

	return trie


def autocomplete(prefix, trie, k):

	'''autocomplete the prefix by searching the trie and return the first kth items with largest weights

	Arguments:
	prefix -- string to be matched
	trie -- trie built based on the given text file
	k -- number of items returned'''

	wordList, q = [], []

	if len(prefix.strip())==0:
		raise ValueError("Prefix must be a valid string.")

	'''reach the node containing prefix, or raise error'''
	current = trie.search(prefix)
	if current is None:
		raise LookupError("Prefix doesn't exist in the trie.")

	if current.isWord:
		heapq.heappush(q, (-current.weight, current, True))
	heapq.heappush(q, (-current.maxWeight, current, False))

	if len(q)==0:
		return wordList

	while len(q)>0 and len(wordList)<int(k):
		# pop the node with the largest node.maxweight
		weight, current, isWord = heapq.heappop(q)

		if isWord:
			wordList.append((-weight, current.word))
		else:
			# traversal its children, and keep len(wordList)<=k
			for child in current.children.values():
				if child.isWord:
					heapq.heappush(q, (-child.weight, child, True))
				heapq.heappush(q, (-child.maxWeight, child, False))

	return wordList
