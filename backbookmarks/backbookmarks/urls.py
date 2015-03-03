from django.conf.urls import patterns, include, url

from bookmarks import views

urlpatterns = patterns('',
    url(r'^add/?$', views.handleAddRequest),
    url(r'^remove/?$', views.handleDeleteRequest),
    url(r'^bookmarks/?$', views.handleBookmarksRequest),
)
