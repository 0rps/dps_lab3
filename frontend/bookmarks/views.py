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
backendBookmarks = "http://127.0.0.1:8004"
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
		return func(request, *args, **kwargs)

	return wrapper

def authorizationRequired(func):
	def wrapper(r, *args, **kwargs):
		session = kwargs.get('session')
		if session is None:
			return HttpResponseRedirect(frontendServer + "/login")
		return func(r, *args, **kwargs)
	return wrapper


@sessionWrapper
def index(request, session=None):
	return render(request, "base.html", {'logged': session})


@sessionWrapper
def topSites(request, session=None):
	users = None
	return render(request, "top.html", {'logged': session, 'users': users})

@csrf_exempt
@sessionWrapper
@authorizationRequired
def addBookmark(request, session=None):
	if request.method != 'POST':
		return HttpResponseForbidden()

	post = request.POST
	url = post.get('url')
	description = post.get('description')
	curUrl = post.get('pageurl')

	if url is None or description is None:
		return HttpResponseBadRequest()

	query = "{0}/add?url={1}".format(backendBookmarks, url)
	response = requests.put(query)

	if response.status_code != 200:
		return HttpResponseServerError()

	id = response.json()['id']

	query = "{0}/add".format(backendFavorites)
	response = requests.post(query, data={'bookmarkId': str(id),
										 'userId': session['userId'],
										 'description': description})

	if response.status_code != 200:
		return HttpResponseServerError()

	if curUrl:
		return HttpResponseRedirect(curUrl)

	frontUrl = "{0}/bookmarks?page={1}".format(frontendServer, 1)
	return HttpResponseRedirect(frontUrl)

@csrf_exempt
@sessionWrapper
@authorizationRequired
def changeBookmark(request, session=None):
	if request.method != 'POST':
		return HttpResponseForbidden()

	param = request.POST

	description = param.get('description')
	id = param.get('id')
	curUrl = param.get('pageurl')

	if description is None or id is None:
		return HttpResponseBadRequest()

	query = "{0}/change?id={1}&description={2}".format(backendFavorites, id, description)
	response = requests.put(query)
	if response.status_code != 200:
		return HttpResponseServerError()

	if curUrl:
		return HttpResponseRedirect(curUrl)

	url = "{0}/bookmarks?page={1}".format(frontendServer, 1)
	return HttpResponseRedirect(url)

@csrf_exempt
@sessionWrapper
@authorizationRequired
def deleteBookmark(request, session=None):
	if request.method != 'POST':
		return HttpResponseForbidden()

	param = request.POST

	curUrl = param.get('pageurl')
	id = param.get('id')

	if id is None:
		return HttpResponseBadRequest()

	query = "{0}/remove?id={1}".format(backendFavorites, id)
	response = requests.delete(query)
	if response.status_code != 200:
		return HttpResponseServerError()

	response = response.json()
	count = int(response['count'])
	if count == 0:
		query = "{0}/remove?id={1}".format(backendBookmarks, response['bookmarkId'])
		response = requests.delete(query)
		if response.status_code != 200:
			return HttpResponseServerError()

	url = "{0}/bookmarks?page={1}".format(frontendServer, 1)

	if curUrl:
		return HttpResponseRedirect(curUrl)

	return HttpResponseRedirect(url)


@sessionWrapper
@authorizationRequired
def getBookmarks(request, session=None):

	if request.method != 'GET':
		return HttpResponseForbidden()

	page = request.GET.get('page')

	if page is None:
		return HttpResponseBadRequest()

	query = "{0}/bookmarks?userId={1}&page={2}&perpage={3}".format(backendFavorites, session['userId'], page, 10)
	response = requests.get(query)
	if response.status_code != 200:
		return HttpResponseServerError()

	response = response.json()

	page = int(response['page'])
	total = int(response['total'])

	if page > 1:
		prevPage = {'num': page-1, 'url': "{0}/bookmarks?page={1}".format(frontendServer, page-1)}
	else:
		prevPage = None

	if page < total:
		nextPage = {'num': page+1, 'url': "{0}/bookmarks?page={1}".format(frontendServer, page+1)}
	else:
		nextPage = None

	pageNumber = page

	bookmarks = response['favorites']

	param = reduce(lambda res, x: ','.join([res, x['bookmarkId']]), bookmarks, "")
	if param != "":
		param = param[1:]

		query = "{0}/bookmarks?bookmarks={1}".format(backendBookmarks, param)
		response = requests.get(query)

		if response.status_code != 200:
			return HttpResponseServerError()

		response = response.json()
		urls = response['bookmarks']

		for bookmark in bookmarks:
			bookmark['url'] = urls[bookmark['bookmarkId']]

	curUrl = "{0}/bookmarks?page={1}".format(frontendServer, pageNumber)

	return render(request, "bookmarks.html", {'logged': session,
											  'curPageUrl': curUrl,
											  'bookmarks':bookmarks,
											  'pageNumber':pageNumber,
											  'prevPage':prevPage,
											  'nextPage':nextPage})


@sessionWrapper
@authorizationRequired
def me(request, session=None):

	query = "{0}/me?userId={1}".format(sessionServer, session['userId'])

	response = requests.get(query)
	profile = {}
	if response.status_code == 200:
		profile = response.json()

	return render(request, "profile.html", {'logged': session, 'profile': profile})


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