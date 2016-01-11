var sendtxt = document.getElementById('sendtxt');
var terminal = document.getElementById('terminal');
var nickbox = document.getElementById('nickbox');
var notdiv = $('#notifications');
sendtxt.value = "";
terminal.value = "";

nick = "Anonymous";

var ws = new WebSocket("ws://localhost:8888/websocket");

ws.onopen = function() {
	var message = {
		"action": "message",
		"data": {
			"sender": nick,
			"text": "Hello World"
		}
	}
	ws.send(JSON.stringify(message));
};

ws.onmessage = function (evt) {
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

ws.onclose = function() {
	notify("<strong>Disconnected from server!</stron>", "danger", 3600000);
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
	var message = {
		"action": "changenick",
		"data": {
			"oldnick": nick,
			"newnick": nickbox.value
		}
	}
	nick = message.data.newnick;
	ws.send(JSON.stringify(message));
	terminal.scrollTop = terminal.scrollHeight;
	sendtxt.focus();
}

function notify(message, level, timeout) {
	// message: a html text
	// level: "success", "info", "warning" or "danger"
	// timeout: the time to display the notification in ms
	var id = Math.floor((Math.random() * 99999) + 1);
	notdiv.after('<div id="noti'+id+'" class="alert alert-'+level+' alert-dismissible fade in out" role="alert">\
			<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>' + message + '</div>');
	var alert = $('#noti'+id).alert();
	window.setTimeout(function() { alert.alert('close') }, timeout);
}
