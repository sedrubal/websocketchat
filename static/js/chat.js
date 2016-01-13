var ws;
var sendtxt = document.getElementById('sendtxt');
var terminal = document.getElementById('terminal');
var nickbox = document.getElementById('nickbox');
var notdiv = $('#notifications');
sendtxt.value = "";
terminal.value = "";

var nick = "Anonymous";
var url = "ws://localhost:8888/websocket";

document.onload = connect(url);
window.onbeforeunload = function() {
	ws = undefined; // don't reconnect while reloading page
};


function connect(url) {
	if (ws == undefined || ws.readyState == ws.CLOSED)	 {
		ws = new WebSocket(url);
		ws.onopen = onopen;
		ws.onmessage = onmessage;
		ws.onclose = onclose;
	}
}

function onopen() {
	notify('Connected to ' + url, 'success', 1000);
	nick = "Anonymous";
	setNick();
};

function onmessage(evt) {
	message = JSON.parse(evt.data);
	if (message.action == "message") {
		var sender = message.data.sender;
		if (sender == nick) {
			sender = "Me";
		} else {
			notify('<strong>' + message.data.sender + '</strong>: ' + message.data.text, 'info', 2000);
		}
		terminal.innerHTML += "<p>" + sender + ": " + message.data.text + "</p>";
		terminal.scrollTop = terminal.scrollHeight;
	} else if (message.action == "changenick") {
		terminal.innerHTML += "<p><i>'" + message.data.oldnick + "' is now called '" + message.data.newnick + "'</i><p>";
		terminal.scrollTop = terminal.scrollHeight;
	}
};

function onclose() {
	if (ws != undefined && ws.readyState == ws.CLOSED) {
		// why is this function triggered so often???
		notify("<strong>Disconnected from server!</strong> Retrying in 3 sec...", "danger", 3000, 'noti-disconnected');
		window.setTimeout(connect(url), 3000);
	}
}

function send() {
	var message = {
		"action": "message",
		"data": {
			"sender": nick,
			"text": sendtxt.value
		}
	}
	ws.send(JSON.stringify(message));
	terminal.scrollTop = terminal.scrollHeight;
	sendtxt.value = "";
}

function setNick() {
	if (nickbox.value != "") {
		var message = {
			"action": "changenick",
			"data": {
				"oldnick": nick,
				"newnick": nickbox.value
			}
		}
		ws.send(JSON.stringify(message));
		nick = message.data.newnick;
		terminal.scrollTop = terminal.scrollHeight;
		sendtxt.focus();
	}
}

function notify(message, level='info', timeout=3000, id=undefined) {
	// message: a html text
	// level: "success", "info", "warning" or "danger"
	// timeout: the time to display the notification in ms
	// id: the html id for the notification. If id already exists, this function also closes the old notification
	if (!id) {
		id = 'noti' + Math.floor((Math.random() * 99999) + 1); // random id (hopefully a non existing id)
	} else if (document.getElementById(id)) {
		window.setTimeout(function() { $('#'+id).alert('close') }, 0); // dirty workaround: when directly closing, jquery has an internal eroor: too much recursion?!
	}
	notdiv.after('<div id="'+id+'" class="alert alert-'+level+' alert-dismissible fade in out" role="alert">\
			<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>' + message + '</div>');
	window.setTimeout(function() { $('#'+id).alert('close') }, timeout);
}
