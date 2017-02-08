# Joshua Agby - joshagby

import re
import sys
import os
from operator import itemgetter

# original contractions dictionary from stackoverflow user arturomp
# http://stackoverflow.com/questions/19790188/expanding-english-language-contractions-in-python
# dictionary has been slightly modified
contractions = {"ain't": "am not",
				"aren't": "are not",
				"can't": "cannot",
				"'cause": "because",
				"could've": "could have",
				"couldn't": "could not",
				"didn't": "did not",
				"doesn't": "does not",
				"don't": "do not",
				"hadn't": "had not",
				"hasn't": "has not",
				"haven't": "have not",
				"he'd": "he would",
				"he'll": "he will",
				"he's": "he is",
				"how'd": "how did",
				"how'll": "how will",
				"how's": "how is",
				"i'd": "i would",
				"i'll": "i will",
				"i'm": "i am",
				"i've": "i have",
				"isn't": "is not",
				"it'd": "it had",
				"it'll": "it will",
				"it's": "it is",
				"let's": "let us",
				"ma'am": "madam",
				"might've": "might have",
				"mightn't": "might not",
				"must've": "must have",
				"mustn't": "must not",
				"needn't": "need not",
				"o'clock": "of the clock",
				"oughtn't": "ought not",
				"she'd": "she would",
				"she'll": "she will",
				"she's": "she is",
				"should've": "should have",
				"shouldn't": "should not",
				"so've": "so have",
				"so's": "so is",
				"that'd": "that would",
				"that's": "that is",
				"there'd": "there would",
				"there's": "there is",
				"they'd": "they would",
				"they'll": "they will",
				"they're": "they are",
				"they've": "they have",
				"wasn't": "was not",
				"we'd": "we would",
				"we'll": "we will",
				"we're": "we are",
				"we've": "we have",
				"weren't": "were not",
				"what'll": "what will",
				"what're": "what are",
				"what's": "what is",
				"what've": "what have",
				"when's": "when is",
				"when've": "when have",
				"where'd": "where did",
				"where's": "where is",
				"where've": "where have",
				"who'll": "who will",
				"who's": "who is",
				"who've": "who have",
				"why's": "why is",
				"why've": "why have",
				"won't": "will not",
				"would've": "would have",
				"wouldn't": "would not",
				"y'all": "you all",
				"you'd": "you would",
				"you'll": "you will",
				"you're": "you are",
				"you've": "you have"
				}

# dictionary with all months and their corresponding number representation
months = {'january': '1',
		  'jan': '1',
		  'february': '2',
		  'march':'3',
		  'mar':'3',
		  'april':'4',
		  'apr':'4',
		  'may':'5',
		  'june':'6',
		  'jun':'6',
		  'july':'7',
		  'jul':'7',
		  'august':'8',
		  'aug':'8',
		  'september':'9',
		  'sept':'9',
		  'october':'10',
		  'oct':'10',
		  'november':'11',
		  'nov':'11',
		  'december':'12',
		  'dec':'12'
		  }

# stopwords list
stopwords = ['a', 'all', 'an', 'and', 'any', 'are', 'as', 'at', 'be', 'been', 'but', 
			 'by', 'few', 'from', 'for', 'have', 'he', 'her', 'here', 'him', 'his',
			 'how', 'i', 'in', 'is', 'it', 'its', 'many', 'me', 'my', 'none', 'of',
			 'on', 'or', 'our', 'she', 'some', 'the', 'their', 'them', 'there',
			 'they', 'that', 'this', 'to', 'us', 'was', 'what', 'when', 'where', 
			 'which', 'who', 'why', 'will', 'with', 'you', 'your']

# input: string
# output: string
# removes SGML tags from string
def removeSGML(inString):
	removeTags = re.compile('<.*?>')
	cleanString = re.sub(removeTags, '', inString)
	return cleanString

# input: string
# output: list (of tokens)
# tokenizes input text
def tokenizeText(inString):
	# split text by whitespace
	inList = inString.split()
	outList = []
	inStringTwo = ''
	i = 0
	for i in range(0,len(inList)):
		token = inList[i]
		token = token.lower()
		# get rid of all characters other than numbers, letter, and the symbols -> . - , ' 
		token = re.sub("[^0-9a-zA-Z-.,']+", '', token)

		# skip token if it contains no alphanumeric characters (punctuation, symbols, etc)
		testAlphaNumeric = re.sub('[0-9a-zA-Z]+', '', token)
		if testAlphaNumeric == token:
			continue
		
		# -- DATE FORMAT CHECKS --
		# -- All dates are normalized to MONTH/DAY/YEAR or MONTH/YEAR --

		# check for first date format (month, day, year), i.e. -> august 22, 1958
		if token in months and len(inList) > (i + 2):
			month = token
			nextWord = inList[i + 1]
			nextWord = nextWord.replace(',', '')
			try:
				day = int(nextWord)
			except ValueError:
				day = 0
			if day in range(1,31):
				nextWord = inList[i + 2]
				try:
					year = int(nextWord)
				except ValueError:
					year = -1
				if year in range(0,9999):
					date = months[month] + '/' + str(day) + '/' + str(year)
					outList.append(date)
					continue

		# check for second date format (month, year), i.e. -> july, 1959
		if token.replace(',', '') in months and len(inList) > (i + 1):
			month = token.replace(',', '')
			nextWord = inList[i + 1]
			try:
				year = int(nextWord)
			except ValueError:
				year = -1
			if year in range(0,9999):
				date = months[month] + '/' + str(year)
				outList.append(date)
				continue

		# check for third date format (month/day/year), i.e. -> 05/14/1995 OR 05.14.1995
		li = token.split('/')
		if len(li) != 3:
			li = token.split('.')
		if len(li) == 3:
			try:
				month = int(li[0])
			except ValueError:
				month = -1
			if month in range(1,13):
				try:
					day = int(li[1])
				except ValueError:
					day = -1
				if day in range(1,31):
					try:
						year = int(li[2])
					except ValueError:
						year = -1
					if year in range(0,9999):
						date = str(month) + '/' + str(day) + '/' + str(year)
						outList.append(date)
						continue

		# -- NUMBER FORMAT CHECK --
		# -- numbers are normalized to contain only numeric charcaters --
		testNumbersOnly = re.sub('[^a-zA-Z]+', '', token)
		if testNumbersOnly == '' and re.sub('[^0-9]+', '', token) != '':
			# if token contains no letters and at least one number...
			outList.append(re.sub('[^0-9]+', '', token))
			continue

		# Test if token contains a dot '.' -> if yes and it has less than 4 letters (maximum abbr. length), add to outlist. 
		if '.' in token:
			if len(re.sub('[^a-zA-Z]+', '', token)) < 5:
				outList.append(token)
				continue

		# check for contractions
		if token in contractions:
			outList.append(contractions[token])
			continue

		# check for possessive, remove ('s) as needed
		# if not possesive and not contraction, remove all apostrophes
		if len(token) > 2:
			if token[-1] == 's' and token[-2] == "'":
				outList.append(token[0:-2])
				continue

		# test for dashed words, i.e. -> up-to-date OR r-1
		if re.sub('[-a-zA-Z0-9]+', '', token) == '' and re.sub('[^-]+', '', token) != '':
			# if word contains only letters, numbers, and dashes...
			outWord = ''
			for word in token.split('-'):
				if word != '':
					outWord += word + '_'
			outList.append(outWord[0:-1])
			continue

		# if token is alphanumeric ONLY (no special characters), add to outlist
		if re.sub('[a-zA-Z0-9]+', '', token) == '':
			outList.append(token)
			continue

		# if token still exists, replace all commas, apostrophes, and dots with whitespace, 
		# add to new string for second token screening
		token = (((token.replace('.', ' ')).replace(',', ' ')).replace("'", " "))
		inStringTwo += ' ' + token

	# check a second time, after replacing all commas, apostrophes, and dots with withspace
	inList = inStringTwo.split()
	i = 0
	for i in range(0,len(inList)):
		token = inList[i]
		
		# -- DATE FORMAT CHECKS --
		# -- All dates are normalized to MONTH/DAY/YEAR or MONTH/YEAR --

		# check for first date format (month, day, year), i.e. -> august 22, 1958
		if token in months and len(inList) > (i + 2):
			month = token
			nextWord = inList[i + 1]
			nextWord = nextWord.replace(',', '')
			try:
				day = int(nextWord)
			except ValueError:
				day = 0
			if day in range(1,31):
				nextWord = inList[i + 2]
				try:
					year = int(nextWord)
				except ValueError:
					year = -1
				if year in range(0,9999):
					date = months[month] + '/' + str(day) + '/' + str(year)
					outList.append(date)
					continue

		# check for second date format (month, year), i.e. -> july, 1959
		if token.replace(',', '') in months and len(inList) > (i + 1):
			month = token.replace(',', '')
			nextWord = inList[i + 1]
			try:
				year = int(nextWord)
			except ValueError:
				year = -1
			if year in range(0,9999):
				date = months[month] + '/' + str(year)
				outList.append(date)
				continue

		# check for third date format (month/day/year), i.e. -> 05/14/1995 OR 05.14.1995
		li = token.split('/')
		if len(li) != 3:
			li = token.split('.')
		if len(li) == 3:
			try:
				month = int(li[0])
			except ValueError:
				month = -1
			if month in range(1,13):
				try:
					day = int(li[1])
				except ValueError:
					day = -1
				if day in range(1,31):
					try:
						year = int(li[2])
					except ValueError:
						year = -1
					if year in range(0,9999):
						date = str(month) + '/' + str(day) + '/' + str(year)
						outList.append(date)
						continue

		# -- NUMBER FORMAT CHECK --
		# -- numbers are normalized to contain only numeric charcaters --
		testNumbersOnly = re.sub('[^a-zA-Z]+', '', token)
		if testNumbersOnly == '' and re.sub('[^0-9]+', '', token) != '':
			# if token contains no letters and at least one number...
			outList.append(re.sub('[^0-9]+', '', token))
			continue

		# test for dashed words, i.e. -> up-to-date OR r-1
		if re.sub('[-a-zA-Z0-9]+', '', token) == '' and re.sub('[^-]+', '', token) != '':
			# if word contains only letters, numbers, and dashes...
			outWord = ''
			for word in token.split('-'):
				if word != '':
					outWord += word + '_'
			outList.append(outWord[0:-1])
			continue

		# add any remaining token directly to outList
		outList.append(token)

	return outList

# input: list of tokens
# outut: list of tokens
# removes all stopwords from token list
def removeStopwords(inList):
	outList = []
	for token in inList:
		if token not in stopwords:
			outList.append(token)
	return outList

# stemWords function
def stemWords(inList):
	p = PorterStemmer()
	outList = []
	for token in inList:
		outList.append(p.stem(token, 0, len(token)-1))
	return outList

# publicly available porter stemmer algorithm taken from link given in assignment. 
# http://tartarus.org/~martin/PorterStemmer/python.txt
# class definition is pasted here, and utilized in function above (stemWords())
class PorterStemmer:

    def __init__(self):
        """The main part of the stemming algorithm starts here.
        b is a buffer holding a word to be stemmed. The letters are in b[k0],
        b[k0+1] ... ending at b[k]. In fact k0 = 0 in this demo program. k is
        readjusted downwards as the stemming progresses. Zero termination is
        not in fact used in the algorithm.

        Note that only lower case sequences are stemmed. Forcing to lower case
        should be done before stem(...) is called.
        """

        self.b = ""  # buffer for word to be stemmed
        self.k = 0
        self.k0 = 0
        self.j = 0   # j is a general offset into the string

    def cons(self, i):
        """cons(i) is TRUE <=> b[i] is a consonant."""
        if self.b[i] == 'a' or self.b[i] == 'e' or self.b[i] == 'i' or self.b[i] == 'o' or self.b[i] == 'u':
            return 0
        if self.b[i] == 'y':
            if i == self.k0:
                return 1
            else:
                return (not self.cons(i - 1))
        return 1

    def m(self):
        """m() measures the number of consonant sequences between k0 and j.
        if c is a consonant sequence and v a vowel sequence, and <..>
        indicates arbitrary presence,

           <c><v>       gives 0
           <c>vc<v>     gives 1
           <c>vcvc<v>   gives 2
           <c>vcvcvc<v> gives 3
           ....
        """
        n = 0
        i = self.k0
        while 1:
            if i > self.j:
                return n
            if not self.cons(i):
                break
            i = i + 1
        i = i + 1
        while 1:
            while 1:
                if i > self.j:
                    return n
                if self.cons(i):
                    break
                i = i + 1
            i = i + 1
            n = n + 1
            while 1:
                if i > self.j:
                    return n
                if not self.cons(i):
                    break
                i = i + 1
            i = i + 1

    def vowelinstem(self):
        """vowelinstem() is TRUE <=> k0,...j contains a vowel"""
        for i in range(self.k0, self.j + 1):
            if not self.cons(i):
                return 1
        return 0

    def doublec(self, j):
        """doublec(j) is TRUE <=> j,(j-1) contain a double consonant."""
        if j < (self.k0 + 1):
            return 0
        if (self.b[j] != self.b[j-1]):
            return 0
        return self.cons(j)

    def cvc(self, i):
        """cvc(i) is TRUE <=> i-2,i-1,i has the form consonant - vowel - consonant
        and also if the second c is not w,x or y. this is used when trying to
        restore an e at the end of a short  e.g.

           cav(e), lov(e), hop(e), crim(e), but
           snow, box, tray.
        """
        if i < (self.k0 + 2) or not self.cons(i) or self.cons(i-1) or not self.cons(i-2):
            return 0
        ch = self.b[i]
        if ch == 'w' or ch == 'x' or ch == 'y':
            return 0
        return 1

    def ends(self, s):
        """ends(s) is TRUE <=> k0,...k ends with the string s."""
        length = len(s)
        if s[length - 1] != self.b[self.k]: # tiny speed-up
            return 0
        if length > (self.k - self.k0 + 1):
            return 0
        if self.b[self.k-length+1:self.k+1] != s:
            return 0
        self.j = self.k - length
        return 1

    def setto(self, s):
        """setto(s) sets (j+1),...k to the characters in the string s, readjusting k."""
        length = len(s)
        self.b = self.b[:self.j+1] + s + self.b[self.j+length+1:]
        self.k = self.j + length

    def r(self, s):
        """r(s) is used further down."""
        if self.m() > 0:
            self.setto(s)

    def step1ab(self):
        """step1ab() gets rid of plurals and -ed or -ing. e.g.

           caresses  ->  caress
           ponies    ->  poni
           ties      ->  ti
           caress    ->  caress
           cats      ->  cat

           feed      ->  feed
           agreed    ->  agree
           disabled  ->  disable

           matting   ->  mat
           mating    ->  mate
           meeting   ->  meet
           milling   ->  mill
           messing   ->  mess

           meetings  ->  meet
        """
        if self.b[self.k] == 's':
            if self.ends("sses"):
                self.k = self.k - 2
            elif self.ends("ies"):
                self.setto("i")
            elif self.b[self.k - 1] != 's':
                self.k = self.k - 1
        if self.ends("eed"):
            if self.m() > 0:
                self.k = self.k - 1
        elif (self.ends("ed") or self.ends("ing")) and self.vowelinstem():
            self.k = self.j
            if self.ends("at"):   self.setto("ate")
            elif self.ends("bl"): self.setto("ble")
            elif self.ends("iz"): self.setto("ize")
            elif self.doublec(self.k):
                self.k = self.k - 1
                ch = self.b[self.k]
                if ch == 'l' or ch == 's' or ch == 'z':
                    self.k = self.k + 1
            elif (self.m() == 1 and self.cvc(self.k)):
                self.setto("e")

    def step1c(self):
        """step1c() turns terminal y to i when there is another vowel in the stem."""
        if (self.ends("y") and self.vowelinstem()):
            self.b = self.b[:self.k] + 'i' + self.b[self.k+1:]

    def step2(self):
        """step2() maps double suffices to single ones.
        so -ization ( = -ize plus -ation) maps to -ize etc. note that the
        string before the suffix must give m() > 0.
        """
        if self.b[self.k - 1] == 'a':
            if self.ends("ational"):   self.r("ate")
            elif self.ends("tional"):  self.r("tion")
        elif self.b[self.k - 1] == 'c':
            if self.ends("enci"):      self.r("ence")
            elif self.ends("anci"):    self.r("ance")
        elif self.b[self.k - 1] == 'e':
            if self.ends("izer"):      self.r("ize")
        elif self.b[self.k - 1] == 'l':
            if self.ends("bli"):       self.r("ble") # --DEPARTURE--
            # To match the published algorithm, replace this phrase with
            #   if self.ends("abli"):      self.r("able")
            elif self.ends("alli"):    self.r("al")
            elif self.ends("entli"):   self.r("ent")
            elif self.ends("eli"):     self.r("e")
            elif self.ends("ousli"):   self.r("ous")
        elif self.b[self.k - 1] == 'o':
            if self.ends("ization"):   self.r("ize")
            elif self.ends("ation"):   self.r("ate")
            elif self.ends("ator"):    self.r("ate")
        elif self.b[self.k - 1] == 's':
            if self.ends("alism"):     self.r("al")
            elif self.ends("iveness"): self.r("ive")
            elif self.ends("fulness"): self.r("ful")
            elif self.ends("ousness"): self.r("ous")
        elif self.b[self.k - 1] == 't':
            if self.ends("aliti"):     self.r("al")
            elif self.ends("iviti"):   self.r("ive")
            elif self.ends("biliti"):  self.r("ble")
        elif self.b[self.k - 1] == 'g': # --DEPARTURE--
            if self.ends("logi"):      self.r("log")
        # To match the published algorithm, delete this phrase

    def step3(self):
        """step3() dels with -ic-, -full, -ness etc. similar strategy to step2."""
        if self.b[self.k] == 'e':
            if self.ends("icate"):     self.r("ic")
            elif self.ends("ative"):   self.r("")
            elif self.ends("alize"):   self.r("al")
        elif self.b[self.k] == 'i':
            if self.ends("iciti"):     self.r("ic")
        elif self.b[self.k] == 'l':
            if self.ends("ical"):      self.r("ic")
            elif self.ends("ful"):     self.r("")
        elif self.b[self.k] == 's':
            if self.ends("ness"):      self.r("")

    def step4(self):
        """step4() takes off -ant, -ence etc., in context <c>vcvc<v>."""
        if self.b[self.k - 1] == 'a':
            if self.ends("al"): pass
            else: return
        elif self.b[self.k - 1] == 'c':
            if self.ends("ance"): pass
            elif self.ends("ence"): pass
            else: return
        elif self.b[self.k - 1] == 'e':
            if self.ends("er"): pass
            else: return
        elif self.b[self.k - 1] == 'i':
            if self.ends("ic"): pass
            else: return
        elif self.b[self.k - 1] == 'l':
            if self.ends("able"): pass
            elif self.ends("ible"): pass
            else: return
        elif self.b[self.k - 1] == 'n':
            if self.ends("ant"): pass
            elif self.ends("ement"): pass
            elif self.ends("ment"): pass
            elif self.ends("ent"): pass
            else: return
        elif self.b[self.k - 1] == 'o':
            if self.ends("ion") and (self.b[self.j] == 's' or self.b[self.j] == 't'): pass
            elif self.ends("ou"): pass
            # takes care of -ous
            else: return
        elif self.b[self.k - 1] == 's':
            if self.ends("ism"): pass
            else: return
        elif self.b[self.k - 1] == 't':
            if self.ends("ate"): pass
            elif self.ends("iti"): pass
            else: return
        elif self.b[self.k - 1] == 'u':
            if self.ends("ous"): pass
            else: return
        elif self.b[self.k - 1] == 'v':
            if self.ends("ive"): pass
            else: return
        elif self.b[self.k - 1] == 'z':
            if self.ends("ize"): pass
            else: return
        else:
            return
        if self.m() > 1:
            self.k = self.j

    def step5(self):
        """step5() removes a final -e if m() > 1, and changes -ll to -l if
        m() > 1.
        """
        self.j = self.k
        if self.b[self.k] == 'e':
            a = self.m()
            if a > 1 or (a == 1 and not self.cvc(self.k-1)):
                self.k = self.k - 1
        if self.b[self.k] == 'l' and self.doublec(self.k) and self.m() > 1:
            self.k = self.k -1

    def stem(self, p, i, j):
        """In stem(p,i,j), p is a char pointer, and the string to be stemmed
        is from p[i] to p[j] inclusive. Typically i is zero and j is the
        offset to the last character of a string, (p[j+1] == '\0'). The
        stemmer adjusts the characters p[i] ... p[j] and returns the new
        end-point of the string, k. Stemming never increases word length, so
        i <= k <= j. To turn the stemmer into a module, declare 'stem' as
        extern, and delete the remainder of this file.
        """
        # copy the parameters into statics
        self.b = p
        self.k = j
        self.k0 = i
        if self.k <= self.k0 + 1:
            return self.b # --DEPARTURE--

        # With this line, strings of length 1 or 2 don't go through the
        # stemming process, although no mention is made of this in the
        # published algorithm. Remove the line to match the published
        # algorithm.

        self.step1ab()
        self.step1c()
        self.step2()
        self.step3()
        self.step4()
        self.step5()
        return self.b[self.k0:self.k+1]

