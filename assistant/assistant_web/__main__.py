from .. import config
from .. import utils
import wikipedia
import signal
import sys


def on_message(mqtt_client, message):
    text = message.payload.decode('utf-8')

    if text == 'search_wiki':
        utils.read_aloud(mqtt_client, 'podaj hasło, które chcesz wyszukać na wikipedii', config.WEB_TOPIC)
    elif text == config.TTS_FINISHED:
        mqtt_client.publish(config.GPIO_TOPIC, config.GPIO_LED_ON)
        mqtt_client.publish(config.STT_TOPIC, config.WEB_TOPIC)
    else:
        if wikipedia.suggest(text) is not None:
            text = wikipedia.suggest(text)

        try:
            summary = wikipedia.summary(text, sentences=2)
            utils.read_aloud(mqtt_client, f'jak podaje wikipedia, {summary}')
        except wikipedia.exceptions.DisambiguationError as e:
            summary = wikipedia.summary(e.options[0], sentences=2)
            utils.read_aloud(mqtt_client, f'jak podaje wikipedia, {summary}')
        except wikipedia.exceptions.PageError:
            utils.read_aloud(mqtt_client, 'przepraszam, nie mogę znaleźć informacji na ten temat')


def main():
    ip, port = utils.get_connection_args(sys.argv)
    wikipedia.set_lang('pl')
    utils.setup_mqtt('web', ip, port, on_message)
    signal.pause()


if __name__ == '__main__':
    main()
