from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.http import HttpResponseServerError
from django.http import HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

import requests

from bookmarks import forms
from bookmarks.log import loginfo, logerror
# Create your views here.

sessionServer = "http://127.0.0.1:8002"
backendFavorites = "http://127.0.0.1:8003"
backendBookmarks = "http://127.0.0.1:8005"
frontendServer = "http://127.0.0.1:8000"


def sessionWrapper(func):
	def wrapper(request, *args, **kwargs):
		cookie = request.COOKIES
		id = cookie.get('id')
		token = cookie.get('token')
		if id is not None and token is not None:
			response = requests.get(sessionServer + "/check?id=" + id + "&token=" + token)
			if response.status_code == 200:
				session = response.json()
				session['id'] = id
				session['token'] = token
				return func(request, session=session, *args, **kwargs)
		loginfo("session is None")
		return func(request, *args, **kwargs)

	return wrapper

def printRequest(func):
	def wrapper(r, *args, **kwargs):
		loginfo(r.method + " " + r.get_full_path())
		return func(r, *args, **kwargs)
	return wrapper

def authorizationRequired(func):
	def wrapper(r, *args, **kwargs):
		session = kwargs.get('session')
		if session is None:
			logerror("authorization failed")
			return HttpResponseRedirect(frontendServer + "/login")
		return func(r, *args, **kwargs)
	return wrapper

@printRequest
@sessionWrapper
def index(request, session=None):
	return render(request, "base.html", {'logged': session})

@printRequest
@sessionWrapper
def topSites(request, session=None):
	response = requests.get("{0}/usercount".format(sessionServer))
	count = response.json()['count']

	return render(request, "top.html", {'logged': session, 'count': count})


@csrf_exempt
@printRequest
@sessionWrapper
@authorizationRequired
def addBookmark(request, session=None):
	if request.method != 'POST':
		logerror("is not POST method")
		return HttpResponseForbidden()

	post = request.POST
	url = post.get('url')
	description = post.get('description')
	curUrl = post.get('pageurl')

	loginfo("params: url = {0}, description = {1}, currentPageUrl = {2}".format(url,description,curUrl))

	if url is None or description is None:
		logerror("some of parameters is None")
		return HttpResponseBadRequest()

	query = "{0}/add?url={1}".format(backendBookmarks, url)
	response = requests.put(query)

	if response.status_code != 200:
		logerror("error in request to bookmarks backend")
		return HttpResponseServerError()

	id = response.json()['id']
	loginfo('id of bookmark = {0}'.format(id))

	query = "{0}/add".format(backendFavorites)
	response = requests.post(query, data={'bookmarkId': str(id),
										 'userId': session['userId'],
										 'description': description})

	if response.status_code != 200:
		logerror("error in request to favorites backend")
		return HttpResponseServerError()

	if curUrl:
		loginfo("redirect to curPageUrl")
		return HttpResponseRedirect(curUrl)

	frontUrl = "{0}/bookmarks?page={1}".format(frontendServer, 1)
	loginfo("currentPageUrl is None, redirect to 1 page")
	return HttpResponseRedirect(frontUrl)

@csrf_exempt
@printRequest
@sessionWrapper
@authorizationRequired
def changeBookmark(request, session=None):
	if request.method != 'POST':
		logerror("is not POST method")
		return HttpResponseForbidden()

	param = request.POST

	description = param.get('description')
	id = param.get('id')
	curUrl = param.get('pageurl')

	loginfo("params: id = {0}, description = {1}, currentPageUrl = {2}".format(id,description,curUrl))


	if description is None or id is None:
		logerror("some of parameters is None")
		return HttpResponseBadRequest()

	query = "{0}/change?id={1}&description={2}".format(backendFavorites, id, description)
	response = requests.put(query)
	if response.status_code != 200:
		logerror("error in request to favorites backend")
		return HttpResponseServerError()

	if curUrl:
		loginfo('redirect to curPageUrl')
		return HttpResponseRedirect(curUrl)

	loginfo("currentPageUrl is None, redirect to 1 page")
	url = "{0}/bookmarks?page={1}".format(frontendServer, 1)
	return HttpResponseRedirect(url)

@csrf_exempt
@printRequest
@sessionWrapper
@authorizationRequired
def deleteBookmark(request, session=None):
	if request.method != 'POST':
		logerror("is not POST method")
		return HttpResponseForbidden()

	param = request.POST

	curUrl = param.get('pageurl')
	id = param.get('id')

	loginfo("params: id = {0} currentPageUrl = {1}".format(id,curUrl))

	if id is None:
		logerror("some of parameters is None")
		return HttpResponseBadRequest()

	query = "{0}/remove?id={1}".format(backendFavorites, id)
	response = requests.delete(query)
	if response.status_code != 200:
		logerror("request to backend favorites failed")
		return HttpResponseServerError()

	response = response.json()
	count = int(response['count'])
	if count == 0:
		loginfo("last bookmark")
		query = "{0}/remove?id={1}".format(backendBookmarks, response['bookmarkId'])
		response = requests.delete(query)
		if response.status_code != 200:
			logerror("request to backend bookmarks failed")
			return HttpResponseServerError()

	url = "{0}/bookmarks?page={1}".format(frontendServer, 1)

	if curUrl:
		loginfo("redirect to curPageUrl")
		return HttpResponseRedirect(curUrl)

	loginfo('redirect to 1 page')
	return HttpResponseRedirect(url)

@printRequest
@sessionWrapper
@authorizationRequired
def getBookmarks(request, session=None):

	if request.method != 'GET':
		return HttpResponseForbidden()

	page = request.GET.get('page')

	if page is None:
		logerror("page param is None")
		return HttpResponseBadRequest()

	query = "{0}/bookmarks?userId={1}&page={2}&perpage={3}".format(backendFavorites, session['userId'], page, 10)
	response = requests.get(query)
	if response.status_code != 200:
		logerror("request to favorites backend failed")
		return HttpResponseServerError()

	response = response.json()

	page = int(response['page'])
	total = int(response['total'])

	if page > 1:
		loginfo("there is prev page")
		prevPage = {'num': page-1, 'url': "{0}/bookmarks?page={1}".format(frontendServer, page-1)}
	else:
		loginfo("there is no prev page")
		prevPage = None

	if page < total:
		loginfo("there is next page")
		nextPage = {'num': page+1, 'url': "{0}/bookmarks?page={1}".format(frontendServer, page+1)}
	else:
		loginfo("there is no next page")
		nextPage = None

	pageNumber = page

	bookmarks = response['favorites']

	param = reduce(lambda res, x: ','.join([res, x['bookmarkId']]), bookmarks, "")
	if param == "":
		loginfo("bookmarks list is empty")

	if param != "":
		param = param[1:]

		query = "{0}/bookmarks?bookmarks={1}".format(backendBookmarks, param)
		response = requests.get(query)

		if response.status_code != 200:
			logerror("request to bookmarks backend failed")
			return HttpResponseServerError()

		response = response.json()
		urls = response['bookmarks']

		loginfo("merging results")
		for bookmark in bookmarks:
			bookmark['url'] = urls[bookmark['bookmarkId']]

	curUrl = "{0}/bookmarks?page={1}".format(frontendServer, pageNumber)

	return render(request, "bookmarks.html", {'logged': session,
											  'curPageUrl': curUrl,
											  'bookmarks':bookmarks,
											  'pageNumber':pageNumber,
											  'prevPage':prevPage,
											  'nextPage':nextPage})

@printRequest
@sessionWrapper
@authorizationRequired
def me(request, session=None):

	query = "{0}/me?userId={1}".format(sessionServer, session['userId'])

	response = requests.get(query)
	profile = {}
	if response.status_code == 200:
		profile = response.json()
	else:
		logerror("bad request to session")
	return render(request, "profile.html", {'logged': session, 'profile': profile})

@printRequest
@sessionWrapper
def login(request, session=None):
	if session is not None:
		return HttpResponseRedirect(frontendServer + "/index")

	if request.method == 'POST':
		form = forms.SigninForm(request.POST)
		if form.is_valid():
			response = requests.post(sessionServer + '/login', form.json())
			if response.status_code == 200:
				answer = response.json()

				id = answer['id']
				token = answer['token']

				result = HttpResponseRedirect(frontendServer + '/index')
				result.set_cookie('id', id)
				result.set_cookie('token', token)

				return result
	else:
		form = forms.SigninForm()
	return render(request, 'login.html', {'form': form, 'logged': session})

@printRequest
@sessionWrapper
def register(request, session=None):
	if session is not None:
		return HttpResponseRedirect(frontendServer + "/index")

	if request.method == 'POST':
		form = forms.RegisterForm(request.POST)
		if form.is_valid():
			response = requests.put(sessionServer + '/register', params=form.json())
			if response.status_code == 200:
				return HttpResponseRedirect(frontendServer + '/login')
			else:
				return render(request, 'registration.html', {'form': form, 'logged': session, 'tryagain': 1})

	else:
		form = forms.RegisterForm()
	return render(request, 'registration.html', {'form': form, 'logged': session})

@printRequest
@sessionWrapper
@authorizationRequired
def logout(request, session=None):

	response = requests.delete(url=sessionServer+"/logout?id={0}&token={1}".format(session['id'], session['token']))
	if response.status_code == 200:
		result = HttpResponseRedirect("{0}/index".format(frontendServer))
		result.delete_cookie('id')
		result.delete_cookie('token')

		return result

	return HttpResponseRedirect("{0}/login".format(frontendServer))