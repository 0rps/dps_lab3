from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest

import json

from bookmarks import models

def handleAddRequest(request):
	if request.method != 'PUT':
		return HttpResponseBadRequest()

	put = request.REQUEST
	url = put.get('url')

	if url is None:
		return HttpResponseBadRequest()

	bookmark = models.getBookmarkViaURL(url)
	if bookmark:
		id = bookmark.id
	else:
		bookmark = models.Bookmark()
		bookmark.url = url
		bookmark.save()
		id = bookmark.id

	return HttpResponse(json.dumps({'id': id}))

def handleDeleteRequest(request):
	if request.method != 'DELETE':
		return HttpResponseBadRequest()

	delete = request.REQUEST
	id = delete.get('id')

	if id is None:
		return HttpResponseBadRequest()

	id = int(id)
	bookmark = models.getBookmarkViaId(id)

	if bookmark is None:
		return HttpResponseBadRequest()

	bookmark.delete()
	return HttpResponse()

def handleBookmarksRequest(request):
	if request.method != 'GET':
		return HttpResponseBadRequest()

	get = request.GET

	bookmarks = get.get('bookmarks')
	if bookmarks is None:
		return HttpResponseBadRequest()

	bookmarks = { x: models.getBookmarkViaId(int(x)) for x in bookmarks.split(',') if models.getBookmarkViaId(int(x))}

	return HttpResponse(json.dumps({'bookmarks':bookmarks}))
