from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.paginator import Paginator, EmptyPage

import json

from bookmarks import models

def handleBookmarksRequest(request):
	if request.method != 'GET':
		return HttpResponseBadRequest()

	get = request.GET

	page = get.get('page')
	perpage = get.get('perpage')
	userId = get.get('userId')

	if page is None or perpage is None:
		return HttpResponseBadRequest()

	page = int(page)
	perpage = int(perpage)
	userId = int(userId)

	paginator = Paginator(models.Favorite.objects.filter(userId=userId), perpage)
	try:
		favorites = paginator.page(page)
	except EmptyPage:
		favorites = paginator.page(paginator.num_pages)

	pageCount = paginator.num_pages

	objs = [x.toJson() for x in favorites]
	result = {}
	result['favorites'] = objs
	result['page'] = page
	result['perpage'] = perpage
	result['total'] = pageCount

	return HttpResponse(json.dumps(result))


def handleAddRequest(request):
	if request.method != 'POST':
		return HttpResponseBadRequest()

	post = request.POST

	userId = post.get('userId')
	description = post.get('description')
	bookmarkId = post.get('bookmarkId')

	if userId and description and bookmarkId:
		favorite = models.Favorite()
		favorite.userId = int(userId)
		favorite.bookmarkId = int(bookmarkId)
		favorite.description = description

		favorite.save()

	return HttpResponse()


def handleChangeRequest(request):
	if request.method != 'PUT':
		return HttpResponseBadRequest()

	put = request.REQUEST
	id = put.get('id')
	description = put.get('description')

	if id is None or description is None:
		return HttpResponseBadRequest()

	favorite = models.getFavorite(id)
	if favorite is None:
		return HttpResponseBadRequest()

	favorite.description = description
	favorite.save()

	return HttpResponse()


def handleDeleteRequest(request):
	if request.method != 'DELETE':
		return HttpResponseBadRequest()

	delete = request.REQUEST
	id = delete.get('id')

	if id is None:
		return HttpResponseBadRequest()

	favorite = models.getFavorite(id)
	if favorite is None:
		return HttpResponseBadRequest()

	count = models.equalBookmarkCount(favorite.bookmarkId)
	count = count - 1
	bookmarkId = favorite.bookmarkId

	favorite.delete()

	return HttpResponse(json.dumps({'count': count, 'bookmarkId':bookmarkId}))