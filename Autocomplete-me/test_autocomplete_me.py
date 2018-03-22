# Title: Test suite for autocomplete-me
# Course: 36-650
# Author: Sijia Liu

import unittest
import random
import autocomplete_me
from autocomplete_me import Trie, Node


class test_autocomplete_me(unittest.TestCase):
	'''Unittest cases and randomized tests for autocomplete_me'''

	def test_auto(self):
		# test autocomplete function
		self.assertEqual(autocomplete_me.autocomplete("t", wikTrie, 5),([(5627187200, 'the'), (2595609600, 'to'), (1107331800, 'that'), (401542500, 'this'), (334039800, 'they')]))
		self.assertEqual(autocomplete_me.autocomplete("th", wikTrie, 5),([(5627187200, 'the'), (1107331800, 'that'), (401542500, 'this'), (334039800, 'they'), (282026500, 'their')]))
		self.assertRaises(LookupError, autocomplete_me.autocomplete, "xxx", wikTrie, 5)
		self.assertRaises(ValueError, autocomplete_me.autocomplete, "  ", wikTrie, 5)

		self.assertEqual(autocomplete_me.autocomplete("S", pokTrie, 5), ([(2194440, 'Scizor'), (1211390, 'Starmie'), (993018, 'Skarmory'), (981131, 'Salamence'), (232622, 'Sableye')]))
		self.assertEqual(autocomplete_me.autocomplete("Sh", pokTrie, 5), ([(81075, 'Sharpedo'), (55024, 'Shedinja'), (43597, 'Shaymin'), (42367, 'Shuckle'), (31091, 'Shiftry')]))
		self.assertRaises(LookupError, autocomplete_me.autocomplete, "xxx", pokTrie, 5)
		self.assertRaises(ValueError, autocomplete_me.autocomplete, "  ", pokTrie, 5)
		
		self.assertEqual(autocomplete_me.autocomplete("L", babTrie, 5), ([(16709, 'Liam'), (13066, 'Logan'), (10623, 'Lucas'), (9319, 'Landon'), (8930, 'Luke')]))
		self.assertEqual(autocomplete_me.autocomplete("Li", babTrie, 5), ([(16709, 'Liam'), (7899, 'Lily'), (7105, 'Lillian'), (2915, 'Lincoln'), (2759, 'Lilly')]))
		self.assertRaises(LookupError, autocomplete_me.autocomplete, "xxx", babTrie, 5)
		self.assertRaises(ValueError, autocomplete_me.autocomplete, "  ", babTrie, 5)
		
		self.assertEqual(autocomplete_me.autocomplete("T", movTrie, 5), ([(658672302, 'Titanic (1997)'), (623357910, 'The Avengers (2012)'), (534858444, 'The Dark Knight (2008)'), (448139099, 'The Dark Knight Rises (2012)'), (422783777, 'The Lion King (1994)')]))
		self.assertEqual(autocomplete_me.autocomplete("The", movTrie, 5), ([(623357910, 'The Avengers (2012)'), (534858444, 'The Dark Knight (2008)'), (448139099, 'The Dark Knight Rises (2012)'), (422783777, 'The Lion King (1994)'), (408010692, 'The Hunger Games (2012)')]))
		self.assertEqual(autocomplete_me.autocomplete("Star Wars", movTrie, 5), ([(460935665, 'Star Wars (1977)'), (380262555, 'Star Wars: Episode III - Revenge of the Sith (2005)'), (310675583, 'Star Wars: Episode II - Attack of the Clones (2002)'), (309125409, 'Star Wars: Episode VI - Return of the Jedi (1983)'), (290475067, 'Star Wars: Episode V - The Empire Strikes Back (1980)')]))
		self.assertRaises(LookupError, autocomplete_me.autocomplete, "xxx", movTrie, 5)
		self.assertRaises(ValueError, autocomplete_me.autocomplete, "  ", movTrie, 5)


	def test_random(self):
		# test autocomplete with randomized texts
		self.assertEqual(autocomplete_me.autocomplete("a", randTrie, 5), slow_autocomplete("a", randFile, 5))
		self.assertEqual(autocomplete_me.autocomplete("ac", randTrie, 5), slow_autocomplete("ac", randFile, 5))
		self.assertEqual(autocomplete_me.autocomplete("act", randTrie, 5), slow_autocomplete("act", randFile, 5))


	def test_read(self):
		# test read_terms function
		self.assertEqual(autocomplete_me.read_terms("wiktionary.txt").root.weight, -1)
		self.assertEqual(autocomplete_me.read_terms("wiktionary.txt").root.word, None)
		self.assertEqual(autocomplete_me.read_terms("wiktionary.txt").root.maxWeight, 5627187200)
		self.assertRaises(ValueError, autocomplete_me.read_terms, "  ")

	def test_insert(self):
		# test insert function
		trie = autocomplete_me.Trie()
		trie.insert(Node(weight=500, word="a"))
		trie.insert(Node(weight=123, word="apple"))
		trie.insert(Node(weight=234, word="apples"))

		self.assertEqual(trie.root.weight, -1)
		self.assertEqual(trie.root.word, None)
		self.assertEqual(trie.root.maxWeight, 500)
		self.assertTrue('a', trie.root.children)

		trie.insert(Node(weight=677, word="c"))
		trie.insert(Node(weight=2900, word="cat"))

		self.assertEqual(trie.root.weight, -1)
		self.assertEqual(trie.root.word, None)
		self.assertEqual(trie.root.maxWeight, 2900)
		self.assertTrue('a', trie.root.children)
		self.assertTrue('c', trie.root.children)


	def test_search(self):
		# test search function
		self.assertEqual(wikTrie.search("t").word, "t")
		self.assertEqual(wikTrie.search("t").weight, 442165)
		self.assertEqual(wikTrie.search("t").maxWeight, 5627187200)
		self.assertEqual(wikTrie.search("th").word, None)
		self.assertEqual(wikTrie.search("th").weight, -1)
		self.assertEqual(wikTrie.search("th").maxWeight, 5627187200)
		self.assertEqual(wikTrie.search("the").word, "the")
		self.assertEqual(wikTrie.search("the").weight, 5627187200)
		self.assertEqual(wikTrie.search("the").maxWeight, 334039800)


	def test_weight(self):
		# test when children.weight > node.weight
		trie = autocomplete_me.Trie()
		trie.insert(Node(weight=123, word="apple"))
		trie.insert(Node(weight=234, word="apples"))

		self.assertEqual(trie.search("apple").weight, 123)
		self.assertEqual(trie.search("apple").maxWeight, 234)


	def test_wordList(self):
		# test if len(wordList)=len(children) when len(children)<k
		trie = autocomplete_me.Trie()
		trie.insert(Node(weight=123, word="apple"))
		trie.insert(Node(weight=234, word="apples"))
		trie.insert(Node(weight=67, word="applet"))
		trie.insert(Node(weight=88, word="appletree"))

		self.assertEqual(len(autocomplete_me.autocomplete("apple", trie, 6)), 4)


def create_random_terms(file, n):
	'''create a text file with randomly generated strings and weights

	Arguments:
	file -- file name to be created
	n -- number of items to be created'''
	randList = []

	words = ["".join([random.choice(["a","c","t","h","e","o","k","i"]) for _ in range(random.randint(4, 10))]) for _ in range(n)]
	weights = ["".join([random.choice(["1","2","3","4","5","6","7","8","9","0"]) for _ in range(random.randint(4, 8))]).lstrip("0") for _ in range(n)]
	for i in range(0,len(words)-1):
		randList.append((weights[i], words[i]))

	with open(file, 'w') as random_text:
		random_text.write(str(len(randList)+1)+"\n")
		for i in range(0, len(randList)):
			random_text.write(str(randList[i][0]+"\t"+randList[i][1]+"\n"))
		random_text.close()

	return file


def slow_autocomplete(prefix, file, k):
	'''
	traverse all the words and sort by their weights, return the first kth ones

	Arguments:
	prefix -- string to be matched
	file -- text file containing all words
	k -- number of items returned'''

	words, wordList = [], []

	with open(file, 'r') as txt:
		next(txt)
		for line in txt:
			if line != '\n':
				item = line.strip().split('\t')
				words.append((int(item[0]), item[1]))

	words = sorted(words, reverse=True)

	for item in words:
		if prefix == item[1][0:len(prefix)] and len(wordList)<k:
			wordList.append(item)

	return wordList


# four tries
wikTrie = autocomplete_me.read_terms('wiktionary.txt')
pokTrie = autocomplete_me.read_terms('pokemon.txt')
babTrie = autocomplete_me.read_terms('baby-names.txt')
movTrie = autocomplete_me.read_terms('movies.txt')

# random tries
randFile = create_random_terms('random.txt', 2000)
randTrie = autocomplete_me.read_terms(randFile)


if __name__ == '__main__':
	unittest.main()
	