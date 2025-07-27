from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from random import randint
import json

from .models import *

# Create your views here.

def get_group_chats(request):
    if request.method == "GET" and request.user.is_authenticated:
        return JsonResponse([Group.objects.get(group_id=group_id).serialize() for group_id in Group_Member.objects.filter(member=request.user).values_list("group", flat=True)], safe=False)

def get_friends(request):
    if request.method == "GET" and request.user.is_authenticated:
        friends = Friend.objects.filter(user=request.user)
        if friends:
            return JsonResponse([friend.serialize() for friend in friends], safe=False)
        else:
            return JsonResponse({"error": "lmao no friends"})

def get_user_info(request, user_id):
    if request.user.is_authenticated and request.method == "GET":
        return JsonResponse(User.objects.get(id=user_id).serialize())

def get_user(request, user_id):
    if request.user.is_authenticated and request.method == "GET":
        friend = User.objects.get(id=user_id)
        if friend:
            friendship = Friend.objects.get(friend=friend)
            return render(request, "user.html", friendship.serialize())
        else:
            return render(request, "user.html", {"error": "deleted_user"})

def send_request(request):
    if request.user.is_authenticated and request.method == "POST":
        recipient = User.objects.filter(id=request.POST["friend_id"]).first()
        if request.user == recipient:
            return render(request, "friends.html", {"msg": "cant friend urself get a life"})
        if Friend.objects.filter(friend=request.user).exists():
            return render(request, "friends.html", {"msg": "cant friend request a friend"})
        try:
            friend_request = Friend_Request.objects.create(user=request.user, recipient=recipient)
            friend_request.save()
            return redirect("app")
        except:
            return render(request, "friends.html", {"msg": "who u tranna friend, ur imaginary one?"})
      
def request_response(request, request_id):
    if request.user.is_authenticated and request.method == "POST":
        action = request.POST["action"]
        if action == "accept":
            friend_request = Friend_Request.objects.get(request_id=request_id)
            friend = Friend.objects.create(user=request.user, friend=friend_request.user)
            friend.save()
            friend = Friend.objects.create(user=friend_request.user, friend=request.user)
            friend.save()
            friend_request.delete()
            return redirect("app")
        else:
            Friend_Request.objects.get(request_id=request_id).delete()
            return redirect("app")

def get_requests(request):
    if request.method == "GET" and request.user.is_authenticated:
        requests = Friend_Request.objects.filter(recipient=request.user)
        if requests:
            return JsonResponse([request.serialize() for request in requests], safe=False)
        else:
            return JsonResponse({"error": "no requests"})

def send_message(request):
    if request.method == "POST" and request.user.is_authenticated:
        data = json.loads(request.body)
        message = data["message"]
        friendship = Friend.objects.get(friendship_id=data["friendship_id"])

        if request.user != friendship.user:
            return JsonResponse({"lmao": "u tried"}, status=403)

        msg_obj = DM_Message.objects.create(message=message, friendship=friendship)
        msg_obj.save()

        return JsonResponse({"message": "Message sent successfully."}, status=201)

def get_dm_messages(request, friendship_id):
    if request.method == "GET" and request.user.is_authenticated:
        messages = DM_Message.objects.filter(friendship_id=friendship_id).order_by("-timestamp") | DM_Message.objects.filter(friendship_id=Friend.objects.get(friendship_id=friendship_id).inverse().friendship_id).order_by("-timestamp")
        return render(request, "messages.html", {"messages": messages})

def add_friend(request):
    if request.method == "POST" and request.user.is_authenticated:
        try:
            group = Group.objects.get(group_id=json.loads(request.body)["group_id"])
            friend = User.objects.get(username=json.loads(request.body)["friend"])

            if Friend.objects.filter(user=request.user, friend=friend).exists():
                membership = Group_Member.objects.create(member=friend, group=group)
                membership.save()
                return JsonResponse({"sucess": "Friend added sucessfully"})  
            else:
                return JsonResponse({"error": "Only can add your friends"})
        except:
            return JsonResponse({"error": "Can't add ur imaginary friend"})

def send_group_message(request):
    if request.method == "POST" and request.user.is_authenticated:
        data = json.loads(request.body)
        message = data["message"]
        group = Group.objects.get(group_id=data["group_id"])

        if not Group_Member.objects.filter(group=group, member=request.user).exists():
            return JsonResponse({"lmao": "u tried"}, status=403)

        msg_obj = Group_Message.objects.create(message=message, group=group, sender=request.user)
        msg_obj.save()

        return JsonResponse({"message": "Message sent sucessfully"}, status=201)


def get_group_messages(request, group_id):
    if request.method == "GET" and request.user.is_authenticated:
        messages = Group_Message.objects.filter(group_id=group_id).order_by("-timestamp")
        return render(request, "messages.html", {"messages": messages})

def load_users(request, group_id):
    if request.method == "GET" and request.user.is_authenticated:
        group = Group.objects.get(group_id=group_id)
        members = Group_Member.objects.filter(group=group)
        return render(request, "online.html", {"members": [member.serialize() for member in members]})

def group_chat(request, group_id):
    if request.user.is_authenticated and request.method == "POST":
        if group_id != 0:
            group = Group.objects.get(group_id=group_id)
            members = Group_Member.objects.filter(group=group).values_list("member", flat=True)
            if members.filter(group=group).exists():
                return render(request, "group.html", group.serialize())
        else:
            group = Group.objects.create(creator=request.user, name="")
            group.save()
            member = Group_Member.objects.create(member=request.user,group=group)
            member.save()
            return render(request, "group.html", group.serialize())

def change_group_name(request, group_id):
    if request.user.is_authenticated and request.method == "POST":
        name = json.loads(request.body)["name"]
        group = Group.objects.get(group_id=group_id)
        group.name = name
        group.save()
        return JsonResponse({"message": "Name changed successfully"}, status=201)


def dms(request, friendship_id):
    if request.user.is_authenticated and request.method == "POST":
        friendship = Friend.objects.get(friendship_id=friendship_id)
        if request.user == friendship.user:
            return render(request, "dm.html", friendship.serialize())

def index(request):
    return render(request, "index.html")

def friends(request):
    if not request.user.is_authenticated:
        return redirect("/")
    return render(request, "friends.html")

def app(request):
    if not request.user.is_authenticated:
        return redirect("/")
    return render(request, "main.html")

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, email=email, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("app"))
        else:
            return render(request, "index.html", {
                "msg": "Invalid email and/or password."
            })
    else:
        return render(request, "index.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "register.html", {
                "msg": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
        except IntegrityError:
            return render(request, "register.html", {
                "msg": "Username/Email already taken."
            })
        except:
            return render(request, "register.html", {
                "msg": "What were you thinking mate you out of your mind"
            })
        user.delete()

        code = randint(100000, 999999)
        code_obj = Code.objects.create(code=code)
        code_obj.save()

        email = EmailMessage(
            "Budget Discord Email Confirmation",
            render_to_string("confirmation_email.html", {"code": code_obj.code}),
            settings.EMAIL_HOST_USER,
            [email]
        )
        email.fail_silently = True
        email.send()

        return render(request, "email_confirm.html", {"code_id": code_obj.code_id, "username": username, "email": request.POST["email"], "password": password})
    else:
        return render(request, "register.html")

def email_confirm(request):
    if request.method == "POST":
        if Code.objects.filter(code_id=request.POST["code_id"], code=request.POST["code"]).exists():
            try:
                user = User.objects.create_user(request.POST["username"], request.POST["email"], request.POST["password"])
                user.save()
                login(request, user)
                return redirect("/app")
            except IntegrityError:
                return redirect("/register", {"msg", "registration failed"})
        else:
            return render(request, "emaill_confirm.html", {"msg": "Incorrect Code"})

