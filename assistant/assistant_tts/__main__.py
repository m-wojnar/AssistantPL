from .. import config
from .. import utils
from gtts import gTTS
import vlc
import signal
import time
import sys


def on_message(mqtt_client, message):
    send_to, text = message.payload.decode('utf-8').split('#')
    gTTS(text, lang='pl').save('tts.mp3')

    player = vlc.MediaPlayer('tts.mp3')
    player.play()

    while player.get_state() != vlc.State.Ended:
        time.sleep(0.2)

    mqtt_client.publish(send_to, config.TTS_FINISHED)


def main():
    ip, port = utils.get_connection_args(sys.argv)
    utils.setup_mqtt('TTS', ip, port, on_message)
    signal.pause()


if __name__ == '__main__':
    main()
