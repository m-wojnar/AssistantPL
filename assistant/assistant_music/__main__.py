from .. import config
from .. import utils
from glob import glob
import random
import signal
import sys
import os
import vlc


extensions = [
    '*.mp3', '*.wav', '*.flac'
]


def on_message(mqtt_client, message, vlc_instance, player):
    text = message.payload.decode('utf-8')

    if text == 'random':
        play(mqtt_client, vlc_instance, player)
    elif text == 'stop' and player.get_state() == vlc.State.Playing:
        player.stop()


def play(mqtt_client, vlc_instance, player):
    files = []

    for ext in extensions:
        files += glob(os.path.join(os.getenv("HOME"), config.MUSIC_FOLDER, ext))

    if len(files) == 0:
        utils.read_aloud(mqtt_client, 'nie masz żadnych plików w folderze z muzyką')
    else:
        music_file = random.choice(files)
        media = vlc_instance.media_new(music_file)
        player.set_media(media)
        player.play()


def main():
    ip, port = utils.get_connection_args(sys.argv)
    vlc_instance = vlc.Instance()
    player = vlc_instance.media_player_new()
    utils.setup_mqtt('music', ip, port, on_message, vlc_instance=vlc_instance, player=player)
    signal.pause()


if __name__ == '__main__':
    main()
