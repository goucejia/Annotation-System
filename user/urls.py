from django.conf.urls import url
from . import views

app_name = "user"

urlpatterns = [
    # user/
    url(r'^$', views.index, name="index"),

    url(r'^register/$', views.register, name='register'),

    url(r'^login/$', views.login, name='login'),

    url(r'^logout/$', views.logout, name='logout'),

    url(r'^user_homepage/$', views.homepage, name='homepage'),

    url(r'^file_upload/$', views.file_upload, name='file_upload')


]