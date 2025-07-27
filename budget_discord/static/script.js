document.addEventListener("DOMContentLoaded", function() {

    // show settings menu on click
    document.querySelector("#settings").addEventListener("click", function() {
        document.querySelector("#settings-menu").classList.add("open");
    });
    
    // hide settings menu when close button clicked
    document.querySelector(".settings-close-button").addEventListener("click", function() {
        document.querySelector("#settings-menu").classList.remove("open");
    });

    try {
        // show side bar on click 
        document.querySelector("#side-bar-toggle").addEventListener("click", function() {
            document.querySelector("#side-bar-toggle").classList.toggle("openned");
            document.querySelector(".side-nav-wrapper").classList.toggle("openned");
        });
    } catch {}
    try {
        document.querySelector("#group-chat-side-bar-toggle").addEventListener("click", function() {
            document.querySelector("#group-chat-side-bar-toggle").classList.toggle("openned");
            document.querySelector(".group-chat-side-bar-wrapper").classList.toggle("openned");
        });
    } catch {}
    try {
        // switch to viewing friends
        document.querySelector("#view_friends").addEventListener("click", function() {
            document.querySelector("#friends-view").style.display = "block";
            document.querySelector("#friends-add").style.display = "none";
            document.querySelector("#friend-requests").style.display = "none";
        });

        // switch to viewing adding friends
        document.querySelector("#add_friends").addEventListener("click", function() {
            document.querySelector("#friends-view").style.display = "none";
            document.querySelector("#friends-add").style.display = "block";
            document.querySelector("#friend-requests").style.display = "none";
        });

        // switch to viewing friend requests
        document.querySelector("#requests").addEventListener("click", function() {
            document.querySelector("#friends-view").style.display = "none";
            document.querySelector("#friends-add").style.display = "none";
            document.querySelector("#friend-requests").style.display = "block";
        });
    } catch {}
    try {
        document.querySelector(".group-chat-top-bar-name").addEventListener("input", function(event) {
            document.querySelector(".group-chat-top-bar-name-hidden").textContent = event.target.value;
        });

        document.querySelector(".group-chat-top-bar-name").addEventListener("change", function(event) {
            var csrf = document.getElementsByName("csrfmiddlewaretoken")[0].value;
            fetch("/change_group_name/" + event.target.parentElement.getAttribute("value"), {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrf
                },
                body: JSON.stringify({
                    name: event.target.value
                })
            });
            document.querySelector(".text-bar").placeholder = "Message " + event.target.value;
            var side = document.querySelector("#g" + event.target.parentElement.getAttribute("value"));
            side.textContent = event.target.value;
        });

        document.querySelector(".group-chat-top-bar-add-friends").addEventListener("click", function() {
            document.querySelector(".add-friends-pop-up-container").style.display = "block";
        });

        document.querySelector(".add-friends-submit").addEventListener("click", function() {
            var group_id = document.querySelector(".group-chat-top-bar-name-container");
            group_id = group_id.getAttribute("value");
            var friend = document.querySelector(".add-friends-input").value;
            fetch("/add_friend", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.getElementsByName("csrfmiddlewaretoken")[0].value
                },
                body: JSON.stringify({
                    group_id: group_id,
                    friend: friend
                })
            })
            .then(response => response.json())
            .then(result => {
                var msg = document.querySelector(".add-friends-msg");
                if (result.sucess) {
                    msg.textContent = result.sucess;
                } else {
                    msg.textContent = result.error;
                }
            });
        });
    } catch {}
    try {
        // toggle friends menu
        document.querySelector(".friends-nav-bar-burger").addEventListener("click", function(){
            document.querySelector(".friends-nav-bar-mobile").classList.toggle("open");
        });

        // switch to viewing friends
        document.querySelector("#view-friends-mobile").addEventListener("click", function() {
            document.querySelector("#friends-view").style.display = "block";
            document.querySelector("#friends-add").style.display = "none";
            document.querySelector("#friend-requests").style.display = "none";
            document.querySelector(".friends-nav-bar-mobile").classList.toggle("open");
        });

        // switch to viewing adding friends
        document.querySelector("#add-friends-mobile").addEventListener("click", function() {
            document.querySelector("#friends-view").style.display = "none";
            document.querySelector("#friends-add").style.display = "block";
            document.querySelector("#friend-requests").style.display = "none";
            document.querySelector(".friends-nav-bar-mobile").classList.toggle("open");
        });

        // switch to viewing friend requests
        document.querySelector("#requests-mobile").addEventListener("click", function() {
            document.querySelector("#friends-view").style.display = "none";
            document.querySelector("#friends-add").style.display = "none";
            document.querySelector("#friend-requests").style.display = "block";
            document.querySelector(".friends-nav-bar-mobile").classList.toggle("open");
        });
    } catch {}

    // handle various click events
    document.addEventListener("click", function(event) {
        if (event.target.classList.contains("add") == false) {
            try {
                document.querySelector(".add-friends-pop-up-container").style.display = "none";
            }
            catch {}
        }
        if (event.target.className == "friend" || event.target.className == "friend-name") {
            get_user(event.target.value)
        }
    });

});

// send message
function send_message() {
    var message = document.querySelector(".text-bar").value;
    if (message) {
        var friendship_id = document.querySelector(".dm-top-bar-friend-name").getAttribute("value");
        var csrf = document.getElementsByName("csrfmiddlewaretoken")[0].value;
    
        fetch("/send_message", {
            method: "POST",
            headers: {
                "X-CSRFToken": csrf
            },
            body: JSON.stringify({
                friendship_id: friendship_id,
                message: message
            })
        })
        .then(function() {
            document.querySelector(".text-bar").value = "";
            load_dm_messages();
        });
    }
}

// send group chat message
function send_group_message() {
    var message = document.querySelector(".text-bar").value;
    if (message) {
        var group_id = document.querySelector(".group-chat-top-bar-name-container").getAttribute("value");
        var csrf = document.getElementsByName("csrfmiddlewaretoken")[0].value;
    
        fetch("/send_group_message", {
            method: "POST",
            headers: {
                "X-CSRFToken": csrf
            },
            body: JSON.stringify({ 
                group_id: group_id,
                message: message
            })
        })
        .then(function() {
            document.querySelector(".text-bar").value = "";
            load_group_messages();
        });
    }
}

// load messages
function load_dm_messages() {
    var friendship_id = document.querySelector(".dm-top-bar-friend-name").getAttribute("value");

    fetch("/get_dm_messages/" + friendship_id, {
        method: "GET"
    })
    .then(response => response.text())
    .then(result => {
        var view = document.querySelector(".dm-message-container");
        view.innerHTML = "";
        var parser = new DOMParser
        var doc = parser.parseFromString(result, "text/html");
        doc.querySelectorAll(".message-container").forEach(function(item) {
            view.append(item);
        });
    });
}

// check if user is online
function is_online(user_id) {
    fetch("/get_user_info/" + user_id, {
        method: "GET"
    })
    .then(response => response.json())
    .then(result => {
        if (result.is_online == true) {
            document.querySelector(".dm-top-bar-friend-status").textContent = "Online";
        } else {
            document.querySelector(".dm-top-bar-friend-status").textContent = "Offline";
        }
    });
}

function load_users(group_id) {
    fetch("/load_users/" + group_id, {
        method: "GET"
    })
    .then(response => response.text())
    .then(result => {
        var view = document.querySelector(".group-chat-bar");
        view.innerHTML = "";
        var parser = new DOMParser
        var doc = parser.parseFromString(result, "text/html");
        doc.querySelectorAll(".member-outer-container").forEach(function(item) {
            view.append(item);
        });
    });
}

// fetch user
function get_user(user_id) {
    fetch("/get_user/" + user_id, {
        method: "GET"
    })
    .then(response => response.text())
    .then(result => {
        var parser = new DOMParser
        var doc = parser.parseFromString(result, "text/html");
        var user = doc.querySelector(".user-outer-container");
        document.querySelector("body").prepend(user);
        document.addEventListener("click", function(event) {
            if (event.target.className != "user-outer-container" && event.target.className != "user-inner-container" && event.target.className != "user-username" && event.target.className != "user-message") {
                user.remove()
            }
        });
    });
}

// fetch all friends
function get_friends() {
    fetch("/get_friends", {
        method: "GET"
    })
    .then(response => response.json())
    .then(result => {
        var view = document.querySelector("#friends-view");
        view.textContent = "";
        if (result.error == "lmao no friends") {
            var error = document.createElement("div");
            error.className = "friends-error-msg"
            error.innerHTML = "lmao no friends bad";
            document.querySelector("#friends-view").append(error);
        } else {
            for (var i = 0; i < result.length; i++) {
                var friend = document.createElement("div");
                var friend_name = document.createElement("div");

                friend.className = "friend";
                friend_name.className = "friend-name";

                friend_name.innerHTML = result[i].friend;

                friend.value = result[i].friend_id;
                friend_name.value = result[i].friend_id;
                
                friend.append(friend_name);
                document.querySelector("#friends-view").append(friend);
            }
        }
    });
}

// load group chat messages
function load_group_messages() {
    var group_id = document.querySelector(".group-chat-top-bar-name-container")
    var group_id = group_id.getAttribute("value");

    fetch("/get_group_messages/" + group_id, {
        method: "GET"
    })
    .then(response => response.text())
    .then(result => {
        var view = document.querySelector(".dm-message-container");
        view.innerHTML = "";
        var parser = new DOMParser
        var doc = parser.parseFromString(result, "text/html");
        doc.querySelectorAll(".message-container").forEach(function(item) {
            view.append(item);
        });
    });
}

// get group chats
function get_group_chats() {
    fetch("/get_groups", {
        method: "GET"
    })
    .then(response => response.json())
    .then(result => {
        var view = document.querySelector(".group-chats");
        view.textContent = "";
        for (var i = 0; i < result.length; i++) {           
            var container = document.createElement("div");
            var form = document.createElement("form");
            var chat = document.createElement("button");
            var csrf_token = document.createElement("input");

            container.className = "group-chat-container";
            chat.className = "group-chat";
            chat.id = "g" + result[i].group_id;

            chat.innerHTML = result[i].name;

            form.action = "/app/group_chat/" + result[i].group_id;
            form.method = "POST";

            chat.type = "submit";

            csrf_token.type = "hidden";
            csrf_token.name = "csrfmiddlewaretoken";
            csrf_token.value = document.getElementsByName("csrfmiddlewaretoken")[0].value;

            form.append(chat, csrf_token);
            container.append(form); 
            view.append(container);
        }
    });
}

// fetch all friend requests
function get_requests() {
    fetch("/get_requests", {
        method: "GET"
    })
    .then(response => response.json())
    .then(result => {
        var view = document.querySelector("#friend-requests");
        view.textContent = "";

        if (result.error == "no requests") {
            var error = document.createElement("div");
            error.className = "friends-error-msg"
            error.innerHTML = "No requests";
            document.querySelector("#friend-requests").append(error);
        }
        
        for (var i = 0; i < result.length; i++) {
            var csrf = document.getElementsByName("csrfmiddlewaretoken")[0].value;
            var request = document.createElement("div");
            var user = document.createElement("div");
            var accept_form = document.createElement("form");
            var decline_form = document.createElement("form");
            var accept = document.createElement("button");
            var decline = document.createElement("button");
            var accept_csrf = document.createElement("input");
            var decline_csrf = document.createElement("input")
            
            request.className = "request";
            user.className = "request-user";
            accept.className = "request-accept";
            decline.className = "request-decline";
            
            accept_form.action = "/request_response/" + result[i].request_id;
            accept_form.method = "POST";
            decline_form.action = "/request_response/" + result[i].request_id;
            decline_form.method = "POST";

            accept_csrf.type = "hidden";
            accept_csrf.name = "csrfmiddlewaretoken";
            accept_csrf.value = csrf;
            decline_csrf.type = "hidden";
            decline_csrf.name = "csrfmiddlewaretoken";
            decline_csrf.value = csrf;

            user.innerHTML = result[i].user;
            accept.innerHTML = "Accept";
            decline.innerHTML = "Decline";

            accept.type = "submit";
            accept.name = "action";
            accept.value = "accept";
            decline.type = "submit";
            decline.name = "action";
            decline.value = "decline";

            request.append(user, accept_form, decline_form)
            accept_form.append(accept, accept_csrf);
            decline_form.append(decline, decline_csrf)
            document.querySelector("#friend-requests").append(request);
        }
    });
}