from .. import config
from .. import utils
import random
import signal
import sys


class JokesGenerator:
    def __init__(self):
        self.jokes = []
        self.reload()

    def reload(self):
        with open(config.JOKES_FILE, encoding='utf-8') as file:
            self.jokes = file.read().splitlines()

    def random_next(self):
        while True:
            random.shuffle(self.jokes)

            for joke in self.jokes:
                yield joke


def on_message(mqtt_client, message, random_jokes):
    if message.payload.decode('utf-8') == 'random':
        utils.read_aloud(mqtt_client, next(random_jokes))


def main():
    ip, port = utils.get_connection_args(sys.argv)
    utils.setup_mqtt('jokes', ip, port, on_message, random_jokes=JokesGenerator().random_next())
    signal.pause()


if __name__ == '__main__':
    main()
