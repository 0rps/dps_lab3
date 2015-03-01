from django.conf.urls import patterns, include, url
from django.contrib import admin

from bookmarks import views

urlpatterns = patterns('',
    url(r'^register/?$', views.handleRegisterRequest),
    url(r'^login/?$', views.handleLoginRequest),
    url(r'^logout/?$', views.handleLogoutRequest),
    url(r'^me/?$', views.handleMeRequest),
    url(r'^check/?$', views.handleCheckCookieRequest),
)
