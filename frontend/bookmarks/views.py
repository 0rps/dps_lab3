from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

import requests

from bookmarks import forms
# Create your views here.

sessionServer = "http://127.0.0.1:8002"
backendFavorites = "http://127.0.0.1:6000"
backendBookmarks = "http://127.0.0.1:5000"
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
	return render(request, "base.html", {'title': 'Index page', 'logged': session})


@sessionWrapper
def topSites(request, session=None):
	return render(request, "base.html", {'title': 'Top', 'logged': session})


@sessionWrapper
@authorizationRequired
def addBookmark(request, session=None):
	return render(request, "base.html", {'title': 'Add', 'logged': session})

@sessionWrapper
@authorizationRequired
def changeBookmark(request, session=None):
	return render(request, "base.html", {'title': 'Add', 'logged': session})

@sessionWrapper
@authorizationRequired
def deleteBookmark(request, session=None):
	return render(request, "base.html", {'title': 'Delete', 'logged': session})


@sessionWrapper
@authorizationRequired
def bookmarks(request, session=None):
	return render(request, "base.html", {'logged': session})


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