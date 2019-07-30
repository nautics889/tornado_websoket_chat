import tornado.ioloop
import tornado.web
import tornado.websocket

import logging

import motor
from datetime import datetime
import json


logging.basicConfig(format='%(asctime)s  %(levelname)-8s '
                           '[%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S')
logging.getLogger().setLevel(logging.DEBUG)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('!TEST!')


class ChatHandler(tornado.websocket.WebSocketHandler):
    connections = set()

    def check_origin(self, origin: str) -> bool:
        return True

    async def open(self):
        logging.info(f'Client connected!')
        self.connections.add(self)

        client = motor.motor_tornado.MotorClient()
        db = client.test
        async for m in db.foobar.find({}, limit=5).sort([('_id', -1)]):
            data = {'content': m.pop('content'),
                    'timestamp': str(m.pop('timestamp'))}
            logging.info(f'MESSAGE DATA: {data}')
            await self.write_message(json.dumps(data))

    async def on_message(self, content):
        logging.info(f'ON MESSAGE METHOD, {content}')

        received_at = datetime.now()

        client = motor.motor_tornado.MotorClient()
        db = client.test
        res = await db.foobar.insert_one({'content': content,
                                          'timestamp': received_at})
        logging.debug(res)

        for connection in self.connections:
            connection.write_message({'content': content,
                                      'timestamp': str(received_at)})

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
