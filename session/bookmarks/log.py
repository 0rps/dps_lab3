__author__ = 'orps'

import datetime

file = open('../../session.log', 'w+')

def log(message, level):
	logdebug(message)
	file.write(level + ' ' + str(datetime.datetime.now()) + ': ' + str(message) + '\n')

def loginfo(message):
	log(message, 'INFO')

def logerror(message):
	log(message, 'ERROR')

def logdebug(message):
	print "DEBUG: " + str(datetime.datetime.now()) + ' ' + str(message)