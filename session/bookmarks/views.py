from django.shortcuts import render

from django.http import HttpResponse, HttpResponseBadRequest

import json

from bookmarks import models

def handleRegisterRequest(request):
	put = request.PUT

	user = models.User
	user.name = put.get['name']
	user.email = put.get['email']
	user.password = put.get['password']
	user.phone = put.get['phone']

	if models.getUserViaEmail(user.email):
		return HttpResponseBadRequest()

	user.save()
	return HttpResponse()


def handleCheckCookieRequest(request):
	get = request.GET

	token = get.get('token')
	userId = get.get('userID')

	result = {}
	cookie = models.getCookie(userId, token)
	if cookie:
		result["valid"] = 1
	else:
		result["error"] = 1

	return HttpResponse(json.dumps(result))


def handleLoginRequest(request):
	post = request.POST

	email = post.get('email')
	password = post.get('password')

	user = models.getUserViaEmail('email')
	result = {}
	if user and user.password == password:
		cookie = models.generateCookie(user.id)
		result['id'] = cookie.userId
		result['token'] = cookie.token
		return HttpResponse(json.dumps(result))
	else:
		return HttpResponseBadRequest()


def handleLogoutRequest(request):
	delete = request.DELETE

	token = delete.get('token')
	userId = delete.get('userID')

	cookie = models.getCookie(userId, token)
	if cookie: cookie.delete()

	return HttpResponse()


def handleMeRequest(request):
	get = request.GET

	userId = get.get('id')
	user = models.getUserViaId(userId)

	return HttpResponse(user.json())