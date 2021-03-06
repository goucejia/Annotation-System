from django.conf.urls import url
from . import views

app_name = "user"

# user/
urlpatterns = [
    # user
    url(r'^$', views.file_management, name="index"),  # 主页跳转 - TBD

    url(r'^register/$', views.register, name='register'),

    url(r'^login/$', views.login, name='login'),

    url(r'^logout/$', views.logout, name='logout'),

    url(r'^password_reset_by_user$', views.password_reset_by_user, name='password_reset_by_user'),

    url(r'^password_reset_by_email', views.password_reset_by_email, name='password_reset_by_email'),

    url(r'^user_homepage/$', views.homepage, name='homepage'),


    # group
    url(r'^group_management/$', views.group_management, name='group_management'),

    url(r'^shared_group_management/$', views.shared_group_management, name='shared_group_management'),

    url(r'^create_group/$', views.create_group, name='create_group'),

    url(r'^(?P<group_id>[0-9a-f-]+)$', views.edit_group, name='edit_group'),

    url(r'^delete_member/$', views.delete_member, name='delete_member'),
    # url(r'^(?P<group_id>[0-9a-f-]+)/delete_member/$', views.delete_member, name='delete_member'),

    url(r'^add_member/$', views.add_member, name='add_member'),

    url(r'^delete_group/$', views.delete_group, name='delete_group'),



    # file
    url(r'^file_upload/$', views.file_upload, name='file_upload'),

    url(r'^file_management/$', views.file_management, name='file_management'),
    url(r'^file_management_by_modify_time/$', views.file_management_by_modify_time, name='file_management_by_modify_time'),
    url(r'^file_management_by_filename/$', views.file_management_by_filename, name='file_management_by_filename'),

    url(r'^shared_file_view/$', views.shared_file_view, name='shared_file_view'),

    url(r'^group_files_view/$', views.group_file_view, name='group_files_view'),

    url(r'^delete_file/$', views.delete_file, name='delete_file'),

    url(r'^share_file/$', views.share_file, name='share_file'),

    url(r'^share_file_to_group/$', views.share_file_to_group, name='share_file_to_group'),

    url(r'^edit_file/$', views.edit_file, name='edit_file'),

    url(r'^share_status/(?P<file_guid>[0-9a-f-]+)$', views.share_status_management, name='share_status_management'),

    url(r'^remove_share_record/$', views.remove_share_record, name='remove_share_record'),

    # url(r'^sort_file/$', views.sort_file, name='sort_file'),

]
