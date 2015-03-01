from django.conf.urls import patterns, include, url
from bookmarks import views

urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^index$', views.index),
    url(r'^top$', views.topSites),
    url(r'^bookmarks$', views.bookmarks),
    url(r'^me$', views.me),
    url(r'^login$', views.login),
    url(r'^logout$', views.logout),
    url(r'^register/?$', views.register),
)
