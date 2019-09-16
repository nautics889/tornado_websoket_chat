import json
import logging
import os
from datetime import datetime
from typing import Any, Union
from random import randint

import motor
import tornado.ioloop
import tornado.web
import tornado.websocket

logging.basicConfig(format='%(asctime)s  %(levelname)-8s '
                           '[%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S')
logging.getLogger().setLevel(logging.DEBUG)


class StartPageHandler(tornado.web.RequestHandler):
    """A handler which contains methods to handle a start page."""
    def get(self, *args: Any) -> None:
        """A method to handle GET-requests.

        :return: None
        """
        self.render('index.html')


class ChatHandler(tornado.websocket.WebSocketHandler):
    """Main websocket handler responsible to hadle WS-messages.

    Attributes:
        connections (set): set of living WS-connections.
    """
    connections = set()

    def _deserialize_message(self, data: str):
        try:
            return json.loads(data)
        except json.JSONDecodeError as e:
            logging.warning('Invalid message recieved: %s' % str(e))

    def check_origin(self, origin: str) -> bool:
        """A method to verify CORS.

        :param origin (str): CORS
        :return (bool): flag represents allowance status
        """
        return True

    async def open(self):
        logging.info(f'Client connected!')
        self.connections.add(self)

        db = self.application.mongo_client.test
        async for m in db.foobar.find({}, limit=5).sort([('_id', -1)]):
            data = {'content': m.pop('content'),
                    'timestamp': str(m.pop('timestamp'))}
            await self.write_message(json.dumps(data))

    async def on_message(self, raw_data):
        data = self._deserialize_message(raw_data)
        content = data.get('content')

        logging.info(f'ON MESSAGE METHOD, {content}')

        received_at = datetime.now()

        db = self.application.mongo_client.test
        res = await db.foobar.insert_one({'content': content,
                                          'timestamp': received_at})
        logging.debug(res)

        for connection in self.connections:
            connection.write_message({'content': content,
                                      'timestamp': str(received_at)})

    def on_close(self) -> None:
        self.connections.remove(self)
        logging.info('Someone has left the chat...')

    @staticmethod
    def send_performance_data():
        for connection in ChatHandler.connections:
            connection.write_message({'type': 'performance_info_message',
                                      'msg': [randint(1,10) for _ in range(4)]})


class ConcreteApplication(tornado.web.Application):
    def __init__(self, *args, **kwargs) -> None:
        super(ConcreteApplication, self).__init__(*args, **kwargs)

        self.performance_broadcasting_task = tornado.ioloop.PeriodicCallback(
            ChatHandler.send_performance_data,
            2000
        )

        self.mongo_client = kwargs.get('mongo_client')

def make_app():
    _ = 'mongodb://root:password@chatting_mongo_1:27017'
    return ConcreteApplication(
        [
            (r'/', ChatHandler),
            (r'/main/', StartPageHandler)
        ],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=True, mongo_client=motor.motor_tornado.MotorClient(_))

if __name__ == "__main__":
    app = make_app()
    app.listen(8990)
    app.performance_broadcasting_task.start()
    tornado.ioloop.IOLoop.current().start()
