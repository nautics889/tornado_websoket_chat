import json
import logging
import os
import psutil
from datetime import datetime
from typing import Any

import motor
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.options import options

logging.basicConfig(format='%(asctime)s  %(levelname)-8s '
                           '[%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S')
LOGGER = logging.getLogger()


class StartPageHandler(tornado.web.RequestHandler):
    """A handler which contains methods to handle a start page."""
    def get(self, *args: Any) -> None:
        """A method to handle GET-requests.

        :return: None
        """
        self.render('index.html',
                    HOSTNAME=options.HOSTNAME,
                    PORT=options.PORT)


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
            LOGGER.warning('Invalid message recieved: %s' % str(e))

    def check_origin(self, origin: str) -> bool:
        """A method to verify CORS.

        :param origin (str): CORS
        :return (bool): flag represents allowance status
        """
        return True

    async def open(self):
        LOGGER.info('Client connected!')
        self.connections.add(self)

        db = self.application.mongo_client.test
        async for m in db.foobar.find({}, limit=5).sort([('_id', -1)]):
            data = {'content': m.pop('content'),
                    'timestamp': str(m.pop('timestamp'))}
            await self.write_message(json.dumps(data))

    async def on_message(self, raw_data):
        data = self._deserialize_message(raw_data)
        content = data.get('content')

        LOGGER.info('ON MESSAGE METHOD, %s', content)

        received_at = datetime.now()

        db = self.application.mongo_client.test
        await db.foobar.insert_one({'content': content,
                                    'timestamp': received_at})

        for connection in self.connections:
            connection.write_message({'content': content,
                                      'timestamp': str(received_at)})

    def on_close(self) -> None:
        self.connections.remove(self)
        LOGGER.info('Someone has left the chat...')

    @staticmethod
    def send_performance_data() -> None:
        """Send performance data to all connected users."""
        num_of_cores = psutil.cpu_count()
        if not num_of_cores:
            LOGGER.warning('Could not define number of CPU cores!')
            return

        data = {'type': 'performance_info_message',
                'number_of_cores': [num for num in range(1, num_of_cores+1)],
                'cpu_usage': psutil.cpu_percent(percpu=True),
                'ram_used': psutil.virtual_memory().percent}
        for connection in ChatHandler.connections:
            connection.write_message(data)


class ConcreteApplication(tornado.web.Application):
    def __init__(self, *args, **kwargs) -> None:
        super(ConcreteApplication, self).__init__(*args, **kwargs)

        self.performance_broadcasting_task = tornado.ioloop.PeriodicCallback(
            ChatHandler.send_performance_data,
            500
        )

        self.mongo_client = kwargs.get('mongo_client')

def make_app():
    _ = 'mongodb://{}:{}@{}:{}'.format(options.MONGO_USER,
                                       options.MONGO_PASSWORD,
                                       options.MONGO_HOSTNAME,
                                       options.MONGO_PORT)
    return ConcreteApplication(
        [
            (r'/', ChatHandler),
            (r'/main/', StartPageHandler)
        ],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=True, mongo_client=motor.motor_tornado.MotorClient(_))

if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)

    options.define('HOSTNAME', type=str, default='localhost')
    options.define('PORT', type=int, default=80)
    options.define('MONGO_USER', type=str, default='root')
    options.define('MONGO_PASSWORD', type=str, default='password')
    options.define('MONGO_HOSTNAME', type=str, default='localhost')
    options.define('MONGO_PORT', type=int, default=27017)

    options.parse_config_file('server.conf')

    app = make_app()
    app.listen(options.PORT)
    app.performance_broadcasting_task.start()
    tornado.ioloop.IOLoop.current().start()
