import tornado.ioloop
import tornado.web
import tornado.websocket

import logging

import motor
from datetime import datetime
import json
from bson import json_util


logging.basicConfig(format='%(asctime)s  %(levelname)-8s '
                           '[%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S')
logging.getLogger().setLevel(logging.INFO)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('!TEST!')


class ChatHandler(tornado.websocket.WebSocketHandler):
    connections = set()q

    def check_origin(self, origin: str) -> bool:
        return True

    async def open(self):
        logging.info(f'Client connected!')
        self.connections.add(self)

        client = motor.motor_tornado.MotorClient()
        db = client.test
        async for m in db.foobar.find({}, limit=5).sort([('_id', -1)]):
            m.pop('_id')
            #m['timestamp'] = str(m['timestamp'])
            self.write_message(json.dumps(m, default=str))

    async def on_message(self, message):
        logging.info(f'ON MESSAGE METHOD, {message}')
        client = motor.motor_tornado.MotorClient()
        db = client.test

        res = await db.foobar.insert_one({'message': message,
                                          'timestamp': datetime.now()})
        logging.debug(res)

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
