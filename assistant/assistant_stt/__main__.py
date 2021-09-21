from .. import config
from .. import utils
import speech_recognition as sr
import signal
import sys


def on_message(mqtt_client, message):
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.2)
        audio = recognizer.listen(source)
        mqtt_client.publish(config.GPIO_TOPIC, config.GPIO_LED_PULSE)

    try:
        text = recognizer.recognize_google(audio, language='pl-PL')
        mqtt_client.publish(message.payload.decode("utf-8"), text)
    except sr.UnknownValueError:
        utils.read_aloud(mqtt_client, 'przepraszam, nie usłyszałem co mówisz')
    except sr.RequestError:
        utils.read_aloud(mqtt_client, 'przepraszam, wystąpił problem z połączeniem')


def main():
    ip, port = utils.get_connection_args(sys.argv)
    utils.setup_mqtt('STT', ip, port, on_message)
    signal.pause()


if __name__ == '__main__':
    main()
