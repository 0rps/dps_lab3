from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import  csrf_exempt

import json

from bookmarks import models
from bookmarks.log import loginfo, logerror

@csrf_exempt
def handleAddRequest(request):
	if request.method != 'PUT':
		logerror("this is not PUT request")
		return HttpResponseBadRequest()

	put = request.REQUEST
	url = put.get('url')

	if url is None:
		logerror("wrong params")
		return HttpResponseBadRequest()

	bookmark = models.getBookmarkViaURL(url)
	if bookmark:
		loginfo("bookmark with this url is existing")
		id = bookmark.id
	else:
		loginfo("creating bookmark")
		bookmark = models.Bookmark()
		bookmark.url = url
		bookmark.save()
		id = bookmark.id

	id = str(id)
	loginfo("bookmark id: " + id)
	return HttpResponse(json.dumps({'id': id}))

@csrf_exempt
def handleDeleteRequest(request):
	if request.method != 'DELETE':
		logerror("this is not DELETE request")
		return HttpResponseBadRequest()

	delete = request.REQUEST
	id = delete.get('id')

	if id is None:
		logerror("wrong params")
		return HttpResponseBadRequest()

	id = int(id)
	bookmark = models.getBookmarkViaId(id)

	if bookmark is None:
		logerror("no bookmark with this id = {0}".format(id))
		return HttpResponseBadRequest()

	bookmark.delete()
	loginfo("bookmark is deleted")
	return HttpResponse()

def handleBookmarksRequest(request):
	if request.method != 'GET':
		logerror("this is not GET request")
		return HttpResponseBadRequest()

	get = request.GET

	bookmarks = get.get('bookmarks')
	if bookmarks is None:
		logerror("wrong params")
		return HttpResponseBadRequest()

	idList = bookmarks.split(',')
	bookmarks = {str(x): models.getBookmarkViaId(int(x)).url for x in bookmarks.split(',') if models.getBookmarkViaId(int(x))}

	loginfo("urls is chosen")

	return HttpResponse(json.dumps({'bookmarks':bookmarks}))
