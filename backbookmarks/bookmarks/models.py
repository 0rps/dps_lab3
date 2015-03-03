from django.db import models

def exact(str):
    return r'\b' + str + r'\b'

class Bookmark(models.Model):
	url = models.URLField()

def getBookmarkViaId(id):
	objs = Bookmark.objects.filter(id=int(id))
	return objs[0] if objs.count() > 0 else None

def getBookmarkViaURL(url):
	objs = Bookmark.objects.filter(url__exact=exact(url))
	return objs[0] if objs.count() > 0 else None