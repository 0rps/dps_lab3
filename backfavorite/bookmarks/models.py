from django.db import models

class Favorite(models.Model):
	userId = models.IntegerField()
	bookmarkId = models.IntegerField()
	description = models.TextField()

	def toJson(self):
		result = {}
		result['bookmarkId'] = str(self.bookmarkId)
		result['id'] = str(self.id)
		result['description'] = self.description
		return result

def equalBookmarkCount(bookmarkId):
	return Favorite.objects.filter(bookmarkId=int(bookmarkId)).count()

def getFavorite(id):
	request = Favorite.objects.filter(id=int(id))
	return request[0] if request.count() > 0 else None
