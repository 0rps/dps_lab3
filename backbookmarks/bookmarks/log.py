__author__ = 'orps'

import datetime

def log(message, level):
	file = open('../backend_bookmarks.log', 'a')
	line = "{0}: {1} msg: {2}\n".format(level, datetime.datetime.now(), message)
	file.write(line)
	file.close()

def loginfo(message):
	log(message, 'INFO')

def logerror(message):
	log(message, 'ERROR')

def logdebug(message):
	print "DEBUG: " + str(datetime.datetime.now()) + ' ' + str(message)