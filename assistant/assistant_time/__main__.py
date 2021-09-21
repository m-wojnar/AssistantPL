from .. import config
from .. import utils
from datetime import date, datetime
import locale
import signal
import sys


def on_message(mqtt_client, message):
    text = message.payload.decode('utf-8')

    if text == 'now':
        utils.read_aloud(mqtt_client, f'jest {datetime.now().strftime("%H:%M")}')
    elif text == 'date':
        utils.read_aloud(mqtt_client, f'dzisiaj jest {date.today().strftime("%A, %d %B %Y")}')


def main():
    ip, port = utils.get_connection_args(sys.argv)
    locale.setlocale(locale.LC_ALL, 'pl_PL.UTF-8')
    utils.setup_mqtt('time', ip, port, on_message)
    signal.pause()


if __name__ == '__main__':
    main()
