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
        try:
            msg = json.loads(message)
        except ValueError:
            print("invalid message received: '%s'" % message)
            return
        msg['serverdate'] = time.time()
        for socket in APP.websockets:
            socket.send(json.dumps(msg))

    def send(self, message):
        """send a message to my client"""
        self.write_message(message)

    def on_close(self):
        """the client of this socket leaved, remove this socket from list"""
        APP.websockets.remove(self)
        print("WebSocket closed")


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
    APP.websockets = []  # global list of all connected websockets
    tornado.ioloop.IOLoop.current().start()
