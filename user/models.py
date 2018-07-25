from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import uuid

# 用户信息
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    cellphone = models.CharField(max_length=20, blank=True, default='')
    user_uuid = models.UUIDField(default=uuid.uuid4, null=False, auto_created=True, editable=False)

    def __str__(self):
        return self.user.username

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)
post_save.connect(create_user_profile, sender=User)


# 文件信息
class File(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='file_owner')

    # 正式server只存文件路径 #
    # path = models.CharField(max_length=256)
    path = models.FileField(upload_to='files/')

    # @property
    # def filename(self):
    #     name = self.path.name.split("/")[1].replace('_', ' ').replace('-', ' ')
    #     return name
    filename = models.CharField(max_length=256)

    gu_id = models.UUIDField(default=uuid.uuid4, null=False, auto_created=True, editable=False)
    pages = models.PositiveIntegerField(default=0)
    date_uploaded = models.DateTimeField('date file uploaded', auto_now_add=True)
    last_modified = models.DateTimeField('date last modified', auto_now=True)


    def __str__(self):
        return self.filename + " ; " + self.owner.username + " ; " + self.path.url

# 标注信息
class Label(models.Model):
    labeled_file = models.ForeignKey(File, on_delete=models.CASCADE)
    editor = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=256, default='')   # figure / table / ...
    coordinate = models.CharField(max_length=256, default='')
    status = models.CharField(max_length=256, default='')   # 识别 / 删除 / 添加

# 分享组信息
class Group(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_owner')
    group_id = models.UUIDField(default=uuid.uuid4, null=False, auto_created=True, editable=False)

    def __str__(self):
        return self.owner.username + ' ；' + str(self.group_id)

# 单个文件分享记录
class FileShare(models.Model):
    shared_file = models.ForeignKey(File, on_delete=models.CASCADE, default=None)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shared_file_owner", default=None)
    sharer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shared_file_sharer", default=None)

# 群文件分享记录
class GroupShare(models.Model):
    share_user = models.ForeignKey(User, on_delete=models.CASCADE)
    share_group = models.ForeignKey(File, on_delete=models.CASCADE)
    page_num = models.PositiveIntegerField(default=0, blank=False)
    # share_user_id = models.UUIDField(default=uuid.uuid4, null=False, auto_created=False, editable=False)
    # share_group_id = models.UUIDField(default=uuid.uuid4, null=False, auto_created=False, editable=False)


