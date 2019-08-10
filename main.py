import json
import logging
import os
from datetime import datetime

import motor
import tornado.ioloop
import tornado.web
import tornado.websocket

logging.basicConfig(format='%(asctime)s  %(levelname)-8s '
                           '[%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S')
logging.getLogger().setLevel(logging.DEBUG)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')


class ChatHandler(tornado.websocket.WebSocketHandler):
    connections = set()

    def _deserialize_message(self, data):
        try:
            return json.loads(data)
        except json.JSONDecodeError as e:
            logging.warning('Invalid message recieved: %s' % str(e))

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
            await self.write_message(json.dumps(data))

    async def on_message(self, raw_data):
        data = self._deserialize_message(raw_data)
        content = data.get('content')

        logging.info(f'ON MESSAGE METHOD, {content}')

        received_at = datetime.now()

        client = motor.motor_tornado.MotorClient('chatting_mongo_1', 27017)
        db = client.test
        res = await db.foobar.insert_one({'content': content,
                                          'timestamp': received_at})
        logging.debug(res)

        for connection in self.connections:
            connection.write_message({'content': content,
                                      'timestamp': str(received_at)})

    def on_close(self) -> None:
        self.connections.remove(self)
        logging.info('Someone has left the chat...')

def make_app():
    return tornado.web.Application(
        [
            (r'/', ChatHandler),
            (r'/main/', MainHandler)
        ],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=True)

if __name__ == "__main__":
    app = make_app()
    app.listen(8990)
    tornado.ioloop.IOLoop.current().start()
