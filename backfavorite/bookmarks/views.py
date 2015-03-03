from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.core.paginator import Paginator, EmptyPage, InvalidPage

from django.views.decorators.csrf import csrf_exempt

import json

from bookmarks import models
from bookmarks.log import logerror, loginfo

def printRequest(func):
	def wrapper(r, *args, **kwargs):
		loginfo(r.method + " " + r.get_full_path())
		return func(r, *args, **kwargs)
	return wrapper

@printRequest
def handleBookmarksRequest(request):
	if request.method != 'GET':
		logerror("this isn't GET request")
		return HttpResponseBadRequest()

	get = request.GET

	page = get.get('page')
	perpage = get.get('perpage')
	userId = get.get('userId')

	if page is None or perpage is None or userId is None:
		logerror("some parameters is None")
		return HttpResponseBadRequest()

	page = int(page)
	perpage = int(perpage)
	userId = int(userId)

	paginator = Paginator(models.Favorite.objects.filter(userId=userId), perpage, allow_empty_first_page=True)
	try:
		favorites = paginator.page(page)
	except EmptyPage:
		logerror("empty page in paginator")
		favorites = paginator.page(paginator.num_pages)
	except Exception as ex:
		template = "An exception of type {0} occured. Arguments:\n{1!r}"
		message = template.format(type(ex).__name__, ex.args)
		logerror("unexpected error: " + message)

		return HttpResponseServerError()

	pageCount = paginator.num_pages

	objs = [x.toJson() for x in favorites]
	result = {}
	result['favorites'] = objs
	result['page'] = page
	result['perpage'] = perpage
	result['total'] = pageCount

	loginfo('selected: {0} bookmarks, page: {2}, total pages: {1}'.format(len(favorites), pageCount, page))

	return HttpResponse(json.dumps(result))


@csrf_exempt
@printRequest
def handleAddRequest(request):
	if request.method != 'POST':
		logerror("this isn't POST request")
		return HttpResponseBadRequest()

	post = request.POST

	userId = post.get('userId')
	description = post.get('description')
	bookmarkId = post.get('bookmarkId')

	loginfo("userId:{0},desc:{1},bmId:{2}".format(userId,description,bookmarkId))

	if userId and description and bookmarkId:
		favorite = models.Favorite()
		favorite.userId = int(userId)
		favorite.bookmarkId = int(bookmarkId)
		favorite.description = description

		favorite.save()
	else:
		logerror('some parameters is null')
		return HttpResponseBadRequest()

	loginfo("request is executed")
	return HttpResponse()


@csrf_exempt
@printRequest
def handleChangeRequest(request):
	if request.method != 'PUT':
		logerror("this isn't PUT request")
		return HttpResponseBadRequest()

	put = request.REQUEST
	id = put.get('id')
	description = put.get('description')

	if id is None or description is None:
		logerror('some parameters is null')
		return HttpResponseBadRequest()

	favorite = models.getFavorite(id)
	if favorite is None:
		logerror('no such record with id = {1}'.format(id))
		return HttpResponseBadRequest()

	favorite.description = description
	favorite.save()

	loginfo("success")

	return HttpResponse()

@csrf_exempt
@printRequest
def handleDeleteRequest(request):
	if request.method != 'DELETE':
		logerror("this isn't DELETE request")
		return HttpResponseBadRequest()

	delete = request.REQUEST
	id = delete.get('id')

	if id is None:
		logerror('some parameters is null')
		return HttpResponseBadRequest()

	favorite = models.getFavorite(id)
	if favorite is None:
		logerror('no such record with id = {1}'.format(id))
		return HttpResponseBadRequest()

	count = models.equalBookmarkCount(favorite.bookmarkId)
	count = count - 1
	bookmarkId = favorite.bookmarkId

	favorite.delete()

	loginfo("favorite deleted, bookmarks count with this urls = {0}".format(count))

	return HttpResponse(json.dumps({'count': str(count), 'bookmarkId':str(bookmarkId)}))