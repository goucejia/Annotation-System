from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.template import loader
from .models import *

# User Authentications
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm, FileUploadForm

# File Upload
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt


UPLOAD_FILE_TYPES = ['pdf', 'docx', 'txt',]

# Create your views here.

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
                return render(request, 'user/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'user/login.html', {'error_message': 'Invalid login'})
    return render(request, 'user/login.html')

@login_required(login_url='/user/login/')
def logout(request):
    auth_logout(request)
    return render(request, 'user/logout.html')
    # form = UserProfileForm(request.POST or None)
    # context = {
    #     "form": form,
    # }
    # return render(request, 'user/logout.html', context)

@login_required(login_url='/user/login/')
def index(request):
    return redirect('/user/file_upload')   # TODO: correctly link urls
    # return render(request, 'user/upload.html')

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
        # file.filename = file.path.name.split("/")[1].replace('_', ' ').replace('-', ' ')
        # 检查文件后缀名
        # file_type = file.path.url.split(',')[-1]
        # file_type.lower()
        # if file_type not in UPLOAD_FILE_TYPES:
        #     context = {
        #         'file': file,
        #         'form': form,
        #         'error_message': '文件格式不正确',
        #     }
        #     return render(request, 'user/upload.html', context)
        file.save()

        # return render(request, 'check_success.html')    # TODO: file display page
    context = {
        "form": form,
    }
    return render(request, 'file/upload.html', context)

@login_required(login_url='/user/login/')
def file_management(request):
    user = request.user
    files = File.objects.filter(owner=user)
    shared_files = FileShare.objects.filter(sharer=user)
    context = {
        'user': user,
        'files': files,
        'shared_files': shared_files,
    }
    return render(request, 'file/file_management.html', context)


# @login_required(login_url='/user/login/')
# def delete_file(request, file_id):
#     user = request.user
#     file = get_object_or_404(File, file_id)
#     file.delete()
#     files = File.objects.filter(owner=user)
#     return render(request, 'file/file_management.html',  context={'user': user, 'files': files, })

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
                # delete from File table
                File.objects.filter(gu_id=target_file_id).delete()
                c['message'] = '删除成功'
    return JsonResponse(c)









