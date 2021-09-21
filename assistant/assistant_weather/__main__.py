from .. import config
from .. import utils
from pyowm.commons.exceptions import NotFoundError
from pyowm import OWM
import signal
import sys


def read_clouds(value):
    if 0 <= value < 2:
        return 'bezchmurnie'
    elif value < 12.5:
        return 'prawie bezchmurnie'
    elif value < 25:
        return 'mało chmur'
    elif value < 37.5:
        return 'zachmurzenie małe'
    elif value < 50:
        return 'zachmurzenie umiarkowane'
    elif value < 62.5:
        return 'pochmurnie'
    elif value < 75:
        return 'zachmurzenie duże'
    elif value < 87.5:
        return 'zachmurzenie prawie całkowite'
    elif value <= 100:
        return 'zachmurzenie całkowite'
    else:
        return ''


def read_fall(dict):
    if '1h' not in dict and '3h' not in dict:
        return 'brak'

    value = dict.get('1h', dict['3h'] / 3)

    if value < 0.1:
        return 'brak'
    elif value < 2.5:
        return 'lekki opad'
    elif value < 7.5:
        return 'umiarkowany opad'
    elif value >= 7.5:
        return 'silny opad'


def on_message(mqtt_client, message, owm_manager):
    text = message.payload.decode('utf-8')

    if text == 'now':
        utils.read_aloud(mqtt_client, 'podaj nazwę miasta, dla którego chcesz sprawdzić pogodę', config.WEATHER_TOPIC)
    elif text == config.TTS_FINISHED:
        mqtt_client.publish(config.GPIO_TOPIC, config.GPIO_LED_ON)
        mqtt_client.publish(config.STT_TOPIC, config.WEATHER_TOPIC)
    else:
        try:
            weather = owm_manager.weather_at_place(text.title()).weather
            temp = weather.temperature('celsius')['temp']
            wind = weather.wind()['speed']

            utils.read_aloud(mqtt_client, f'''
                w mieście {text} jest obecnie {temp:.0f} stopni Celsjusza,
                {read_clouds(weather.clouds)}
                wiatr {wind:.1f} metra na sekundę,
                {read_fall(weather.rain)} deszczu,
                {read_fall(weather.snow)} śniegu.
            ''')
        except NotFoundError:
            utils.read_aloud(mqtt_client, f'przepraszam, nie potrafię znaleźć miasta {text}')


def main():
    ip, port = utils.get_connection_args(sys.argv)
    owm = OWM(config.OWM_API_KEY)
    utils.setup_mqtt('weather', ip, port, on_message, owm_manager=owm.weather_manager())
    signal.pause()


if __name__ == '__main__':
    main()
