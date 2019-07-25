import tornado.ioloop
import tornado.web
import tornado.websocket

import logging

import motor
import asyncio


logging.basicConfig(format='%(asctime)s  %(levelname)-8s '
                           '[%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S')
logging.getLogger().setLevel(logging.INFO)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('!TEST!')


async def foobar():
    res = 123
    # client = motor.motor_tornado.MotorClient()
    # db = client.test
    # res = await db.collection.find_one({'item':'planner'})
    print(res, flush=True)
    logging.debug('Before await')
    await asyncio.sleep(1)
    print(321, flush=True)
    logging.debug('After await')


class ChatHandler(tornado.websocket.WebSocketHandler):
    connections = set()

    def check_origin(self, origin: str) -> bool:
        return True

    def open(self):
        logging.info(f'Client connected!')
        self.connections.add(self)

    def on_message(self, message):
        logging.info(f'ON MESSAGE METHOD, {message}')
        tornado.ioloop.IOLoop().current().run_sync(foobar)
        for connection in self.connections:
            connection.write_message(message)

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
