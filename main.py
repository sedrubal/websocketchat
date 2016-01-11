#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A small and simple chat website using tornado and websockets.
"""

__authors__ = "sedrubal"
__email__ = "sebastian.endres@online.de",
__license__ = "GPLv3"
__url__ = "https://github.com/sedrubal/websocketchat"


import tornado.ioloop
import tornado.web
import tornado.websocket
import os
import json
import time


class ChatPage(tornado.web.RequestHandler):
    """
    A normal webpage providing some html, css and js, which uses websockets
    """
    def get(self):
        """the handler for get requests"""
        self.render("chat.html",
                    description=__doc__,
                    author=__authors__,
                    license=__license__,
                    url=__url__,
                    authors_url='/'.join(__url__.split('/')[:-1]))


class Client(object):
    """
    An object to store the connected clients
    """
    def __init__(self, socket, nick="Anonymous"):
        self.socket = socket
        self.nick = nick

    def change_nick(self, change_message):
        """
        if a message with action 'changenick' is received,
        the nick of the contact should be changed here
        :param: change_message: parsed message containing the old and new nick
        :return: True on success
        """
        if self.nick == change_message['data']['oldnick']:
            self.nick = change_message['data']['newnick']
            print("Changed nick from '{old}' to '{new}'".
                  format(old=change_message['data']['oldnick'],
                         new=change_message['data']['newnick']))
            return True
        else:
            print("Can't change nick from '{old}' to '{new}' as nick is '{n}'".
                  format(old=change_message['data']['oldnick'],
                         new=change_message['data']['newnick'],
                         n=self.nick))
            return False


class ChatWebSocket(tornado.websocket.WebSocketHandler):
    """
    The websocket server part
    """
    def open(self):
        """when a client connects, add this socket to list"""
        print("WebSocket opened")
        self.client = Client(socket=self)
        APP.clients.append(self.client)

    def on_message(self, message):
        """new message received"""
        msg = ChatWebSocket.parse_message(message)
        if msg is None:
            return
        if msg['action'] == 'changenick':
            if not self.client.change_nick(msg):
                return
        msg['serverdate'] = time.time()
        for client in APP.clients:
            client.socket.send(json.dumps(msg))

    def send(self, message):
        """send a message to my client"""
        self.write_message(message)

    def on_close(self):
        """the client of this socket leaved, remove this socket from list"""
        APP.clients.remove(self.client)
        print("WebSocket closed")

    @staticmethod
    def parse_message(message):
        """
        checks, if the received message json is valid and returns a dict
        """
        try:
            msg = json.loads(message)
        except ValueError:
            print("invalid message received: '%s'" % message)
            return None
        if not msg['action'] or not msg['data']:
            return None
        else:
            return msg

SETTINGS = {
    "template_path": os.path.join(os.path.dirname(__file__), "templates"),
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
}


def make_app():
    """create a new application and specify the url patterns"""
    return tornado.web.Application([
        (r"/websocket", ChatWebSocket),
        (r"/", ChatPage),
        (r"/static/", tornado.web.StaticFileHandler,
         dict(path=SETTINGS['static_path'])),
    ], **SETTINGS)

if __name__ == "__main__":
    APP = make_app()
    APP.listen(8888)
    APP.clients = []  # global list of all connected websocket clients
    tornado.ioloop.IOLoop.current().start()
