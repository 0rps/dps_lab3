from django.conf.urls import patterns, include, url
from django.contrib import admin

from bookmarks import views

urlpatterns = patterns('',
    url(r'^add/?$', views.handleAddRequest),
    url(r'^remove/?$', views.handleDeleteRequest),
    url(r'^bookmarks/?$', views.handleBookmarksRequest),
    url(r'^change/?$', views.handleChangeRequest),

    # Examples:
    # url(r'^$', 'backfavorite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
)
