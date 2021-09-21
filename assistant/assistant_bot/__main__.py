from .. import config
from .. import utils
from collections import Counter
import numpy as np
import signal
import sys


class CommandRecognizer:
    min_cos = 0.3

    def __init__(self):
        self.commands = []
        self.reload()

    def reload(self):
        self.commands = [command for command in CommandRecognizer.read_commands()]

    @staticmethod
    def get_ngrams(text, n=3):
        return Counter(text[i:i + n] for i in range(len(text) - n + 1))

    @staticmethod
    def read_commands():
        with open(config.COMMANDS_FILE, encoding='utf-8') as file:
            for line in file.read().splitlines():
                elements = line.split('|')
                yield CommandRecognizer.get_ngrams(elements[0]), elements[1], elements[2]

    def get_command(self, text):
        text_ngrams = CommandRecognizer.get_ngrams(text)
        best_i = np.argmax([*map(lambda x: CommandRecognizer.cosine(x[0], text_ngrams), self.commands)])
        best_cos = CommandRecognizer.cosine(self.commands[best_i][0], text_ngrams)

        if best_cos >= CommandRecognizer.min_cos:
            return self.commands[best_i][1], self.commands[best_i][2]
        else:
            return None, None

    @staticmethod
    def cosine(a_ngrams, b_ngrams):
        dot = sum(a_ngrams[key] * b_ngrams[key] for key in (a_ngrams & b_ngrams).keys())
        a_values = sum(value ** 2 for value in a_ngrams.values())
        b_values = sum(value ** 2 for value in b_ngrams.values())

        return dot / np.sqrt(a_values * b_values)


def on_message(mqtt_client, message, recognizer):
    text = message.payload.decode('utf-8')

    if text == config.TTS_FINISHED:
        mqtt_client.publish(config.GPIO_TOPIC, config.GPIO_LED_OFF)
    elif text == config.RELOAD_CMD:
        recognizer.reload()
    else:
        topic, command = recognizer.get_command(text.lower())

        if command is None:
            utils.read_aloud(mqtt_client, 'przepraszam, nie potrafię odpowiedzieć na twoje pytanie')
        else:
            mqtt_client.publish(topic, command)


def main():
    ip, port = utils.get_connection_args(sys.argv)
    utils.setup_mqtt('bot', ip, port, on_message, recognizer=CommandRecognizer())
    signal.pause()


if __name__ == '__main__':
    main()
