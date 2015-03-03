__author__ = 'orps'

import datetime
import sys

#sys.stdout = open("log.txt", "a")

def log(message, level):
	file = open('../session.log', 'a')
	line = "{0}: {1} msg: {2}\n".format(level, datetime.datetime.now(), message)
	file.write(line)
	file.close()
	#logdebug(message)
	#file.write(level + ' ' + str(datetime.datetime.now()) + ': ' + str(message) + '\n')

def loginfo(message):
	log(message, 'INFO')

def logerror(message):
	log(message, 'ERROR')

def logdebug(message):
	print "DEBUG: " + str(datetime.datetime.now()) + ' ' + str(message)