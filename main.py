import tornado.ioloop
import tornado.web
import tornado.websocket

import logging


logging.basicConfig(format='%(asctime)s  %(levelname)-8s '
                           '[%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S')
logging.getLogger().setLevel(logging.INFO)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('!TEST!')


class ChatHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin: str) -> bool:
        return True

    def open(self):
        logging.info(f'Client connected!')

    def on_message(self, message):
        logging.info(f'ON MESSAGE METHOD, {message}')
        self.write(message)

    def close(self):
        logging.info('Someone has left the chat...')

def make_app():
    return tornado.web.Application([
        (r'/', ChatHandler)
    ], debug=True)

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
