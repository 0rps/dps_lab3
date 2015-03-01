from django.shortcuts import render

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

import json

from bookmarks import models
from log import logerror, loginfo

@csrf_exempt
def handleRegisterRequest(request):
	loginfo(request.get_full_path())

	put = request.REQUEST

	user = models.User()
	user.name = put.get('name')
	user.email = put.get('email')
	user.password = put.get('password')
	user.phone = put.get('phone')

	loginfo("register: " + "email " + user.email)

	if models.getUserViaEmail(user.email):
		logerror("user with this email is existing")
		return HttpResponseBadRequest()
	user.save()
	loginfo("user registered")
	return HttpResponse()


def handleCheckCookieRequest(request):
	loginfo(request.get_full_path())
	get = request.GET
	token = get.get('token')
	sessionId = get.get('id')

	cookie = models.getCookie(sessionId, token)
	if cookie:
		loginfo('valid cookie')

		return HttpResponse(json.dumps({'userId': cookie.userId}))
	else:
		loginfo('invalid cookie')
		return HttpResponseBadRequest()


@csrf_exempt
def handleLoginRequest(request):
	loginfo(request.get_full_path())
	post = request.POST

	email = post.get('email')
	password = post.get('password')

	loginfo("login request")
	loginfo("email: " + email)

	user = models.getUserViaEmail(email)
	if user is None:
		loginfo("user is none")

	result = {}
	if user and user.password == password:
		cookie = models.generateCookie(user.id)
		loginfo(str(cookie.id))
		result['id'] = cookie.id
		result['token'] = cookie.token
		result['userId'] = cookie.userId
		loginfo('login successful: ')
		loginfo('id: ' + str(cookie.userId))
		loginfo('token: ' + cookie.token)
		return HttpResponse(json.dumps(result))
	else:
		logerror('login failed')
		return HttpResponseBadRequest()

@csrf_exempt
def handleLogoutRequest(request):
	loginfo(request.get_full_path())
	delete = request.REQUEST

	token = delete.get('token')
	sessionId = delete.get('id')

	loginfo("clear cookie: ")
	loginfo("token: " + token)
	loginfo('id: ' + sessionId)

	cookie = models.getCookie(sessionId, token)
	if cookie:
		cookie.delete()
		loginfo('cookie deleted')

	return HttpResponse()


def handleMeRequest(request):
	loginfo(request.get_full_path())
	get = request.GET

	userId = get.get('userId')
	user = models.getUserViaId(userId)

	loginfo('user email' + str(user.email))

	return HttpResponse(user.json())