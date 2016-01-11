#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.ioloop
import tornado.web
import tornado.websocket

CHAT_HTML = './assets/chat.html'


class ChatPage(tornado.web.RequestHandler):
    """
    A normal webpage providing some html, css and js, which uses websockets
    """
    def get(self):
        """the handler for get requests"""
        self.write(open(CHAT_HTML).read())


class ChatWebSocket(tornado.websocket.WebSocketHandler):
    """
    The websocket server part
    """
    def open(self):
        """when a client connects, add this socket to list"""
        print("WebSocket opened")
        APP.websockets.append(self)

    def on_message(self, message):
        """new message received"""
        # TODO check messages
        for socket in APP.websockets:
            socket.send(message)

    def send(self, message):
        """send a message to my client"""
        self.write_message(message)

    def on_close(self):
        """the client of this socket leaved, remove this socket from list"""
        APP.websockets.remove(self)
        print("WebSocket closed")


def make_app():
    """create a new application and specify the url patterns"""
    return tornado.web.Application([
        (r"/websocket", ChatWebSocket),
        (r"/", ChatPage),
    ])

if __name__ == "__main__":
    APP = make_app()
    APP.listen(8888)
    APP.websockets = []  # global list of all connected websockets
    tornado.ioloop.IOLoop.current().start()
