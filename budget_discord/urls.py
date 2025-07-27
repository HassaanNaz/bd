from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("email_confirm", views.email_confirm, name="email_confirm"),
    path("app", views.app, name="app"),
    path("app/friends", views.friends, name="friends"),
    path("app/dms/<int:friendship_id>", views.dms, name="dms"),
    path("app/group_chat/<int:group_id>", views.group_chat, name="group"),
    path("add_friend", views.add_friend, name="add_friend"),
    path("load_users/<int:group_id>", views.load_users, name="load_users"),
    path("change_group_name/<int:group_id>", views.change_group_name, name="change_group_name"),
    path("get_groups", views.get_group_chats, name="get_group_chats"),
    path("get_dm_messages/<int:friendship_id>", views.get_dm_messages, name="get_dm_messages"),
    path("get_group_messages/<int:group_id>", views.get_group_messages, name="get_group_messages"),
    path("send_group_message", views.send_group_message, name="send_group_message"),
    path("send_message", views.send_message, name="send_message"),
    path("get_friends", views.get_friends, name="get_friends"),
    path("send_request", views.send_request, name="send_request"),
    path("get_requests", views.get_requests, name="get_requests"),
    path("request_response/<int:request_id>", views.request_response, name="request_response"),
    path("get_user/<int:user_id>", views.get_user, name="get_user"),
    path("get_user_info/<int:user_id>", views.get_user_info, name="get_user_info")
]
