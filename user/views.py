from django.shortcuts import render, HttpResponse, redirect
from django.urls import reverse
from .models import *

# User Authentications
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import UserProfileForm, FileUploadForm

# File Upload
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt


UPLOAD_FILE_TYPES = ['pdf', ]

# Create your views here.

#
# 用户系统
#
def register(request):
    form = UserProfileForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.profile.cellphone = form.cleaned_data['cellphone']
        # user.profile.user_uuid = uuid.uuid4()
        user.set_password(password)
        user.save()
        user.profile.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                return render(request, 'file/upload.html', {'user': user})
                # albums = Album.objects.filter(user=request.user)
                # return render(request, 'music/upload.html', {'albums': albums})
    else:
        return render(request, 'user/register.html', {'form': form, })


def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                # albums = Album.objects.filter(user=request.user)
                return render(request, 'user/user_homepage.html', {user: 'user'})
            else:
                return render(request, 'user/login_page.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'user/login_page.html', {'error_message': 'Invalid login'})
    return render(request, 'user/login_page.html')


def password_reset_by_email(request):  # TODO: complete function - password forgot reset
    return render(request, 'check_success.html')

@login_required(login_url='/user/login/')
def logout(request):
    auth_logout(request)
    return render(request, 'user/logout.html')  # TODO: redirect logout to login-page
    # form = UserProfileForm(request.POST or None)
    # context = {
    #     "form": form,
    # }
    # return render(request, 'user/logout.html', context)


# @login_required(login_url='/user/login/')
# def password_reset_by_user(request):
#     form = PasswordResetForm(request.POST or None)
#     if form.is_valid():
#         user = request.user
#         old_password = form.cleaned_data['old_password']
#         new_pass1 = form.cleaned_data['new_password']
#         new_pass2 = form.cleaned_data['confirm_password']
#         if new_pass1 == new_pass2:
#             checkuser = authenticate(username=user.username, password=old_password)
#             if checkuser is not None:
#                 if checkuser.is_active:
#                     user.set_password(new_pass1)
#                     user.save()
#                     return render(request, 'check_success.html')
#             return render(request, 'check_success.html')
#         else:  # new password and confirmation does not match
#             return render(request, 'user/reset_by_user.html', {'form': form, 'error_message': "密码不一致"})
#     return render(request, 'user/reset_by_user.html', {'form': form, })

@login_required(login_url='/user/login/')  # TODO: fix function
def password_reset_by_user(request):
    # if request.method == 'POST':
    #     form = PasswordChangeForm(user=request.user, data=request.POST)
    #     if form.is_valid():
    #         form.save()
    #         update_session_auth_hash(request, form.user)
    #         # return redirect('http://www.baidu.com/')
    #         return redirect(reverse('user:homepage'))
    #     # else:
    #     #     # return redirect(reverse('user:password_reset_by_user'))
    # else:
    #     form = PasswordChangeForm(user=request.user)
    #
    # context = {'form': form, }
    # return render(request, 'user/reset_by_user.html', context)

    form = PasswordChangeForm(user=request.user, data=request.POST or None)
    if form.is_valid():
        form.save()
        update_session_auth_hash(request, form.user)
        return redirect(reverse('user:homepage'))
    return render(request, 'user/reset_by_user.html', {'form': form})


#    ------------------------------------------------------------------------------------------------------------


#
# 用户群组
#
@ensure_csrf_cookie
@csrf_exempt
@login_required(login_url='/user/login/')
def create_group(request):
    c = {}
    correct_members = []
    wrong_input = []

    if request.method == 'POST':
        owner = request.user
        id_input = request.POST.get('members').split('\n')
        name_input = request.POST.get('name')

        if Group.objects.filter(group_name=name_input).exists():   # check if group with same name exists
            c = {'error': 'duplicate', }
            return JsonResponse(c)
        else:
            group = Group(owner=owner, group_name=name_input)
            group.save()

        for p in id_input:
            if User.objects.filter(Q(username=p) | Q(email=p)).exists():
                matched_user = User.objects.filter(Q(username=p) | Q(email=p))[0]
                member_record = GroupMember(share_group=group, shared_user=matched_user)
                member_record.save()
                correct_members.append(p)
            else:
                wrong_input.append(p)

        # if no valid group member is found, delete the generated group
        if len(correct_members) == 0:
            group.delete()

        member_record = GroupMember(share_group=group, shared_user=owner);
        member_record.save()

    c['correct_members'] = correct_members
    c['wrong_input'] = wrong_input
    return JsonResponse(c)


@login_required(login_url='/user/login/')
def group_management(request):
    user = request.user
    groups = Group.objects.filter(owner=user)

    # for group in groups:   # find the members in each group and store username in array (as string?)
    #     members = GroupMember.objects.filter(share_group=group)

    context = {
        'groups': groups,
        'user': user,
    }
    return render(request, 'user/group_management.html', context)


@login_required(login_url='/user/login/')
def shared_group_management(request):
    user = request.user
    records = GroupMember.objects.select_related('share_group').filter(shared_user=user)  # includes groups user owned, handle in html
    context = {
        'records': records,
        'user': user,
    }
    return render(request, 'user/shared_group_management.html', context)


@login_required(login_url='/user/login/')
def edit_group(request, group_id):
    user = request.user
    thegroup = Group.objects.select_related().filter(group_id=group_id)[0]
    members = GroupMember.objects.filter(share_group=thegroup)

    context = {
        'group': thegroup,
        'members': members,
        'user': user,
    }
    return render(request, 'user/edit-group.html', context)

@ensure_csrf_cookie
@csrf_exempt
@login_required(login_url='/user/login/')
def delete_member(request):
    group_id = request.POST.get('group')
    thegroup = Group.objects.select_related().filter(group_id=group_id)[0]
    user = request.user

    c = {}
    correct_members = []
    wrong_input = []
    if request.method == 'POST':
        to_delete = request.POST.getlist('to_delete[]')
        # to_delete = request.POST['to_delete']
        # print(to_delete)
        for p in to_delete:
            if User.objects.filter(username=p).exists(): # if matched_user is valid, do the deletion
                matched_user = User.objects.filter(username=p)[0]
                if matched_user == user:
                    c['message'] = '无法删除群主'
                    return JsonResponse(c)
                else:
                    GroupMember.objects.filter(share_group=thegroup, shared_user=matched_user).delete()
                    correct_members.append(p)
            else:
                wrong_input.append(p)

    c['correct_members'] = correct_members
    c['wrong_input'] = wrong_input
    return JsonResponse(c)

@ensure_csrf_cookie
@csrf_exempt
def add_member(request):
    c = {}
    correct_members = []
    wrong_input = []

    if request.method == 'POST':
        owner = request.user
        group_id = request.POST.get('group')
        group = Group.objects.select_related().filter(group_id=group_id)[0]
        id_input = request.POST.get('members').split('\n')

        for p in id_input:
            if User.objects.filter(Q(username=p) | Q(email=p)).exists():
                matched_user = User.objects.filter(Q(username=p) | Q(email=p))[0]
                member_record = GroupMember(share_group=group, shared_user=matched_user)
                member_record.save()
                correct_members.append(p)
            else:
                wrong_input.append(p)

    c['correct_members'] = correct_members
    c['wrong_input'] = wrong_input
    return JsonResponse(c)

@ensure_csrf_cookie
@csrf_exempt
def delete_group(request):
    c = {}
    if request.method == 'POST':
        if request.POST.get('group') != None:
            user = request.user
            target_group_id = request.POST.get('group')
            target_group = Group.objects.filter(group_id=target_group_id)[0]
            if target_group.owner != user:
                c['message'] = '非群创建者，没有操作权限'
                return JsonResponse(c)
            else:
                # Delete related record from GroupMember table by CASCADE
                Group.objects.filter(group_id=target_group_id).delete()
                c['message'] = '删除成功'
                return JsonResponse(c)
    # else:
    #     return render(request, '')


#  -----------------------------------------------------------------------------------------------------------------


#
# 文件管理系统
#
@login_required(login_url='/user/login/')
def index(request):
    # return redirect('/user/file_upload')
    return redirect(reverse('user:file_upload'))


@login_required(login_url='/user/login/')
def homepage(request):
    return render(request, 'user/user_homepage.html')


@login_required(login_url='/user/login/')
def file_upload(request):
    form = FileUploadForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        file = form.save(commit=False)
        file.owner = request.user
        file.path = request.FILES['path']
        file.filename = request.FILES['path'].name

        if File.objects.filter(filename=file.filename).filter(owner=file.owner):
            context = {
                'file': file,
                'form': form,
                'error_message': '同名文件已存在',
                'show': 1,
            }
            return render(request, 'file/upload.html', context)
        else:
            # 检查文件后缀名
            file_type = file.path.url.split('.')[-1]
            file_type.lower()
            if file_type not in UPLOAD_FILE_TYPES:
                context = {
                    'file': file,
                    'form': form,
                    'show': 2,
                }
                return render(request, 'file/upload.html', context)
            file.save()
            context = {
                'form': form,
                'show': 0,
            }
            return render(request, 'file/upload.html', context)
    context = {
        'form': form,
        # 'show': 2,  # do nothing - no alert
    }
    return render(request, 'file/upload.html', context)

# @csrf_exempt
# def file_upload(request):
#     c = {}
#     if request.method == 'POST':
#         obj = request.FILES.get('file')
#         filename = obj.name
#         owner = request.user
#
#         if File.objects.filter(filename=filename).filter(owner=owner).count():
#             c['message'] = '已存在同名文件'
#             return JsonResponse(c)


@login_required(login_url='/user/login/')
def file_management(request):
    user = request.user
    # order = 'upload_time'   # default order by file upload time
    files = File.objects.filter(owner=user).order_by('-date_uploaded')  # default order by file upload time

    # if order == 'upload_time':
    #     files = File.objects.filter(owner=user).order_by('-date_uploaded')
    # elif order == 'modify_time':
    #     files = File.objects.filter(owner=user).order_by('-last_modified')
    # elif order == 'filename':
    #     files = File.objects.filter(owner=user).order_by('filename')

    if files.exists():
        msg_code = 0
    else:
        msg_code = 1
    context = {
        'user': user,
        'files': files,
        'msg': msg_code,
        'order': 0,   # upload_time
    }
    return render(request, 'file/file_management.html', context)


@login_required(login_url='/user/login/')
def file_management_by_modify_time(request):
    user = request.user
    files = File.objects.filter(owner=user).order_by('-last_modified')  # order by last modify time

    if files.exists():
        msg_code = 0
    else:
        msg_code = 1
    context = {
        'user': user,
        'files': files,
        'msg': msg_code,
        'order': 1,   # last_modified
    }
    return render(request, 'file/file_management.html', context)


@login_required(login_url='/user/login/')
def file_management_by_filename(request):
    user = request.user
    files = File.objects.filter(owner=user).order_by('filename')  # order by filename
    # print(files)

    if files.exists():
        msg_code = 0
    else:
        msg_code = 1
    context = {
        'user': user,
        'files': files,
        'msg': msg_code,
        'order': 2,  # filename
    }
    return render(request, 'file/file_management.html', context)


# @ensure_csrf_cookie
# @csrf_exempt
# def sort_file(request):
#     user = request.user
#     flag = ''
#     # files = None
#     if request.method == 'POST':
#         sort_by = request.POST.get('sort_by')  # upload_time / modify_time / filename
#         if sort_by == 'upload_time':
#             flag = 'upload_time'
#             files = File.objects.filter(owner=user).order_by('-date_uploaded')
#         elif sort_by == 'modify_time':
#             flag = 'modify_time'
#             files = File.objects.filter(owner=user).order_by('-last_modified')
#         elif sort_by == 'filename':
#             flag = 'filename'
#             files = File.objects.filter(owner=user).order_by('filename')
#     print(files)
#     print(flag)
#     context = {
#         'files': files,
#         'flag': flag,
#     }
#     return render(request, 'file/file_management.html', context)


@login_required(login_url='/user/login/')
def shared_file_view(request):
    user = request.user
    shared_files = FileShare.objects.filter(sharer=user)
    if shared_files.exists():
        msg_code = 0
    else:
        msg_code = 1
    context = {
        'user': user,
        'shared_files': shared_files,
        'msg': msg_code,
    }
    return render(request, 'file/shared_with_me.html', context)


@login_required(login_url='/user/login/')
def group_file_view(request):
    user = request.user
    if GroupMember.objects.select_related().filter(shared_user=user).exists():  # check if user belongs to any group
        records = GroupMember.objects.select_related().filter(shared_user=user)
        ret = File.objects.none()  # initialize a empty query for merge and return
        for g in records:
            # print(g)
            group = g.share_group
            # files = GroupFiles.objects.select_related().filter(share_group=group)
            # print(files)
            try:
                ret |= GroupFiles.objects.select_related().filter(share_group=group)
                # print(ret)
            except GroupFiles.DoesNotExist:
                pass
        ret.order_by('-date_uploaded')  # default order by file upload time
        context = {
            'user': user,
            'group_files': ret,
            'msg_code': 0,
        }
        return render(request, 'file/group_share_files.html', context)
    else:
        context = {
            'user': user,
            'msg_code': 1,
        }
    return render(request, 'file/group_share_files.html', context)


@ensure_csrf_cookie
@csrf_exempt
@login_required(login_url='/user/login/')
def delete_file(request):
    c = {}
    if request.method == 'POST':
        if request.POST.get('file_guid') != None:
            user = request.user
            target_file_id = request.POST.get('file_guid')
            target_file = File.objects.filter(gu_id=target_file_id)[0]
            if target_file.owner != user:
                c['message'] = '非文件上传者，无法删除'
                return JsonResponse(c)
            else:
                # delete from File table, other table auto-delete by CASCADE
                File.objects.filter(gu_id=target_file_id).delete()
                c['message'] = '删除成功'
    return JsonResponse(c)


@ensure_csrf_cookie
@csrf_exempt
@login_required(login_url='/user/login/')
def share_file(request):
    c = {}
    correct_co_editors = []
    wrong_input = []
    duplicate = []

    if request.method == 'POST':
        owner = request.user
        file_guid = request.POST.get('file_guid')
        share_input = request.POST.get('co_editors').split('\n')

        shared_file = File.objects.filter(gu_id=file_guid)[0]
        for p in share_input:
            if User.objects.filter(Q(username=p) | Q(email=p)).exists():  # input has a match
                matched_editor = User.objects.filter(Q(username=p) | Q(email=p))[0]
                if FileShare.objects.filter(owner=owner, sharer=matched_editor, shared_file=shared_file).exists():
                    duplicate.append(p)
                else:
                    share = FileShare(owner=owner, sharer=matched_editor, shared_file=shared_file)
                    share.save()
                    correct_co_editors.append(p)
            else:
                wrong_input.append(p)

    c['correct_co_editors'] = correct_co_editors
    c['wrong_input'] = wrong_input
    c['duplicate'] = duplicate
    return JsonResponse(c)


@ensure_csrf_cookie
@csrf_exempt
@login_required(login_url='/user/login/')
def share_file_to_group(request):
    c = {}
    correct_group = []
    wrong_input = []
    duplicate = []

    if request.method == 'POST':
        # owner = request.user
        file_guid = request.POST.get('file_guid')
        share_input = request.POST.get('groupID').split('\n')

        shared_file = File.objects.filter(gu_id=file_guid)[0]
        for p in share_input:
            if Group.objects.filter(group_name=p).exists():   # if matched group exists
                matched_group = Group.objects.select_related().filter(group_name=p)[0]
                if GroupFiles.objects.filter(share_group=matched_group, shared_file=shared_file).exists():
                    duplicate.append(p)
                else:
                    group_record = GroupFiles(share_group=matched_group, shared_file=shared_file)
                    group_record.save()
                    correct_group.append(p)
            else:
                wrong_input.append(p)

    c['correct_group'] = correct_group
    c['wrong_input'] = wrong_input
    c['duplicate'] = duplicate
    return JsonResponse(c)

@ensure_csrf_cookie
@csrf_exempt
@login_required(login_url='/user/login/')
def share_status_management(request, file_guid):
    user = request.user
    thefile = File.objects.select_related().filter(gu_id=file_guid)[0]

    # user_shares = FileShare.objects.filter(shared_file=thefile, owner=user)
    user_shares = FileShare.objects.filter(shared_file=thefile)
    group_shares = GroupFiles.objects.filter(shared_file=thefile)

    context = {
        'user': user,
        'file': thefile,
        'user_shares': user_shares,
        'group_shares': group_shares,
    }

    return render(request, 'file/share_status_management.html', context)


@ensure_csrf_cookie
@csrf_exempt
@login_required(login_url='/user/login/')
def remove_share_record(request):
    file_id = request.POST.get('file')
    thefile = File.objects.filter(gu_id=file_id)[0]

    c = {}
    deleted_group = []
    deleted_user = []
    error = []
    if request.method == 'POST':
        user_to_remove = request.POST.getlist('user_to_remove[]')
        group_to_remove = request.POST.getlist('group_to_remove[]')
        # remove user record
        for u in user_to_remove:
            if User.objects.filter(username=u).exists():   # check if matched user exists
                matched_user = User.objects.filter(username=u)[0]  # TODO: 如何处理取消分享给自己？
                FileShare.objects.filter(shared_file=thefile, sharer=matched_user).delete()
                deleted_user.append(u)
            else:
                error.append(u)
        # remove group record
        for g in group_to_remove:
            if Group.objects.filter(group_name=g).exists():   # check if matched group exists
                matched_group = Group.objects.filter(group_name=g)[0]
                GroupFiles.objects.filter(share_group=matched_group, shared_file=thefile).delete()
                deleted_group.append(g)
            else:
                error.append(g)

    c['deleted_user'] = deleted_user
    c['deleted_group'] = deleted_group
    c['error'] = error
    return JsonResponse(c)


@ensure_csrf_cookie
@csrf_exempt
@login_required(login_url='/user/login/')
def edit_file(request):  # TODO: complete function
    return render(request, 'check_success.html')



