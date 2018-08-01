from django.conf.urls import url
from . import views

app_name = "user"

urlpatterns = [
    # user/
    url(r'^$', views.file_management, name="index"),   # 主页跳转 - TBD

    url(r'^register/$', views.register, name='register'),

    url(r'^login/$', views.login, name='login'),

    url(r'^logout/$', views.logout, name='logout'),

    url(r'^user_homepage/$', views.homepage, name='homepage'),

    url(r'^file_upload/$', views.file_upload, name='file_upload'),

    url(r'^file_management/$', views.file_management, name='file_management'),

    url(r'^delete_file/$', views.delete_file, name='delete_file'),
]