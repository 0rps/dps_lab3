__author__ = 'orps'

import datetime

def log(message, level):
	print "{0} {1}, msg: {2}".format(level, datetime.datetime.now(), message)

def loginfo(message):
	log(message, 'INFO')

def logerror(message):
	log(message, 'ERROR')

def logdebug(message):
	print "DEBUG: " + str(datetime.datetime.now()) + ' ' + str(message)