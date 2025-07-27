from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings
from django.db import models
import datetime

# Create your models here.

class Code(models.Model):
    code_id = models.AutoField(primary_key=True)
    code = models.IntegerField()

class User(AbstractUser):
    USERNAME_FIELD = 'email'
    email = models.EmailField(('email address'), unique=True)
    REQUIRED_FIELDS = ["password"]
    last_seen = models.DateTimeField(auto_now=True)

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_online": self.online()
        }

    def online(self):
        if not timezone.now() > self.last_seen + datetime.timedelta(seconds=settings.USER_TIMEOUT):
                return True
        return False 

class Friend_Request(models.Model):
    request_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recipient")

    def serialize(self):
        return {
            "request_id": self.request_id,
            "user": self.user.username,
            "user_id": self.user.id,
            "recipient": self.recipient.username,
            "recipient_id": self.recipient.id
        }

class Friend(models.Model):
    friendship_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friend")

    def inverse(self):
        return Friend.objects.get(user=self.friend, friend=self.user)

    def serialize(self):
        return {
            "friendship_id": self.friendship_id,
            "user": self.user.username,
            "user_id": self.user.id,
            "friend": self.friend.username,
            "friend_id": self.friend.id
        }

class DM_Message(models.Model):
    message_id = models.AutoField(primary_key=True)
    friendship = models.ForeignKey(Friend, on_delete=models.CASCADE, related_name="dm")
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)

    def serialize(self):
        return {
            "message_id": self.message_id,
            "friendship_id": self.friendship_id,
            "sender": self.friendship_id.user.username,
            "sender_id": self.friendship_id.user.id,
            "recipient": self.friendship_id.user.username,
            "recipient_id": self.friendship_id.user.id,
            "message": self.message,
            "timestamp": self.timestamp
        }

class Group(models.Model):
    group_id = models.AutoField(primary_key=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="creator")
    name = models.TextField(default="")

    def latest_message(self):
        return Group_Message.objects.filter(group_id=self.group_id).order_by("-timestamp")[0].timestamp

    def serialize(self):
        return {
            "group_id": self.group_id,
            "name": self.name if self.name else str(self.creator.username) + "'s group",
            "creator": self.creator.username
        }

class Group_Member(models.Model):
    membership_id = models.AutoField(primary_key=True)
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name="member")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group")

    def serialize(self):
        return {
            "membership_id": self.membership_id,
            "member_id": self.member.id,
            "username": self.member.username,
            "is_online": self.member.online(),
            "group_id": self.group.group_id,
            "group_name": self.group.name if self.group.name else str(self.group.creator.username) + "'s group",
            "group_creator": self.group.creator.username
        }
    
class Group_Message(models.Model):
    message_id = models.AutoField(primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="message_in_group")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_msg_sender")
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)