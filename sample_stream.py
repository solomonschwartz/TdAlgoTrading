import asyncio
import pprint

from selenium import webdriver

from tda.auth import easy_client
from tda.streaming import StreamClient

import config

API_KEY = config.CONSUMER_KEY
ACCOUNT_ID = config.ACCOUNT_NUMBER
REDIRECT_URI = config.REDIRECT_URI
TOKEN_PATH = config.JSON_PATH


class MyStreamConsumer:
    """
    We use a class to enforce good code organization practices
    """

    def __init__(self, api_key, account_id, credentials_path, queue_size=0):
        """
        We're storing the configuration variables within the class for easy
        access later in the code!
        """
        self.api_key = api_key
        self.account_id = account_id
        self.credentials_path = credentials_path
        self.tda_client = None
        self.stream_client = None
        self.symbols = [
            'GOOGL', 'BP', 'CVS', 'ADBE', 'CRM', 'SNAP', 'AMZN',
            'BABA', 'DIS', 'TWTR', 'M', 'USO', 'AAPL', 'NFLX', 'GE', 'TSLA',
            'F', 'SPY', 'FDX', 'UBER', 'ROKU', 'X', 'FB'
        ]

        # Create a queue so we can queue up work gathered from the client
        self.queue = asyncio.Queue(queue_size)

    def initialize(self):
        """
        Create the clients and log in. Using easy_client, we can get new creds
        from the user via the web browser if necessary
        """
        self.tda_client = easy_client(
            # You can customize your browser here
            webdriver_func=lambda: webdriver.Chrome(),
            api_key=self.api_key,
            redirect_uri=REDIRECT_URI,
            token_path=self.credentials_path)
        self.stream_client = StreamClient(
            self.tda_client, account_id=self.account_id)

        # The streaming client wants you to add a handler for every service type
        self.stream_client.add_level_one_equity_handler(
            self.handle_level_one_equity)

    async def stream(self):
        await self.stream_client.login()  # Log into the streaming service
        await self.stream_client.quality_of_service(StreamClient.QOSLevel.REAL_TIME)
        await self.stream_client.level_one_equity_subs(symbols=self.symbols)

        # Kick off our handle_queue function as an independent coroutine
        asyncio.ensure_future(self.handle_queue())

        # Continuously handle inbound messages
        while True:
            await self.stream_client.handle_message()

    async def handle_level_one_equity(self, msg):
        """
        This is where we take msgs from the streaming client and put them on a
        queue for later consumption. We use a queue to prevent us from wasting
        resources processing old data, and falling behind.
        """
        # if the queue is full, make room
        if self.queue.full():  # This won't happen if the queue doesn't have a max size
            print('Handler queue is full. Awaiting to make room... Some messages might be dropped')
            await self.queue.get()
        await self.queue.put(msg)

    async def handle_queue(self):
        """
        Here we pull messages off the queue and process them.
        """
        while True:
            msg = await self.queue.get()
            pprint.pprint(msg)
            pprint.pprint("hello")


async def main():
    """
    Create and instantiate the consumer, and start the stream
    """
    consumer = MyStreamConsumer(API_KEY, ACCOUNT_ID,TOKEN_PATH)
    consumer.initialize()
    await consumer.stream()

if __name__ == '__main__':
    asyncio.run(main())