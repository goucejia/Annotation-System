from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import uuid


# 用户信息
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    cellphone = models.CharField(max_length=20, blank=True, default='')
    user_uuid = models.UUIDField(default=uuid.uuid4, null=False, auto_created=True, editable=False, primary_key=True)

    def __str__(self):
        return self.user.username


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)


post_save.connect(create_user_profile, sender=User)


# 文件信息
class File(models.Model):
    gu_id = models.UUIDField(default=uuid.uuid4, null=False, auto_created=True, editable=False, primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='file_owner')

    # 正式server只存文件路径 #
    # path = models.CharField(max_length=256)
    path = models.FileField(upload_to='user_files/')

    # @property
    # def filename(self):
    #     name = self.path.name.split("/")[1].replace('_', ' ').replace('-', ' ')
    #     return name
    filename = models.CharField(max_length=255)

    total_page = models.PositiveIntegerField(default=0)
    date_uploaded = models.DateTimeField('date file uploaded', auto_now_add=True)
    last_modified = models.DateTimeField('date last modified', auto_now=True)

    def __str__(self):
        return self.filename + " ; " + self.owner.username + " ; " + self.path.url


# 分享组信息 (组长 + 组_ID)
class Group(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_owner')
    group_id = models.UUIDField(default=uuid.uuid4, null=False, auto_created=True, editable=False)
    group_name = models.CharField(max_length=255, default='', unique=True)

    def __str__(self):
        return self.owner.username + ' ；' + str(self.group_name)


# 标注信息
class Label(models.Model):
    label_id = models.UUIDField(default=uuid.uuid4, null=False, auto_created=True, editable=False, primary_key=True)
    labeled_file = models.ForeignKey(File, on_delete=models.CASCADE, default=None)
    editor = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    category = models.CharField(max_length=255, default='')  # figure / table / ...
    coordinate = models.CharField(max_length=255, default='')
    status = models.CharField(max_length=255, default='')  # 识别 / 删除 / 添加


# 文件分享记录
class FileShare(models.Model):
    file_share_id = models.UUIDField(default=uuid.uuid4, null=False, auto_created=True,
                                     editable=False, primary_key=True)
    shared_file = models.ForeignKey(File, on_delete=models.CASCADE, default=None)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shared_file_owner", default=None)
    sharer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shared_file_sharer", default=None)
    # type = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="type", default=None)


# 群成员信息
class GroupMember(models.Model):
    share_group = models.ForeignKey(Group, on_delete=models.CASCADE, default=None)
    shared_user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return str(self.share_group.group_name) + ' ; ' + self.shared_user.username


# 分享的群文件信息
class GroupFiles(models.Model):
    share_group = models.ForeignKey(Group, on_delete=models.CASCADE, default=None,
                                    related_name="file_share_group")
    shared_file = models.ForeignKey(File, on_delete=models.CASCADE, default=None,
                                    related_name='shared_file')

    def __str__(self):
        return str(self.share_group.group_name) + " ; " + str(self.shared_file.filename)
    
    


