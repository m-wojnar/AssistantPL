from .. import config
from .. import utils
from gpiozero import PWMLED, Button
import signal
import sys


def on_message(mqtt_client, message, led):
    text = message.payload.decode('utf-8')

    if text == config.GPIO_LED_ON:
        led.on()
    elif text == config.GPIO_LED_OFF:
        led.off()
    elif text == config.GPIO_LED_PULSE:
        led.pulse()


def on_button_pressed(mqtt_client, led):
    led.on()
    mqtt_client.publish(config.MUSIC_TOPIC, 'stop')
    mqtt_client.publish(config.STT_TOPIC, config.BOT_TOPIC)


def main():
    led = PWMLED(3)
    led.off()

    ip, port = utils.get_connection_args(sys.argv)
    mqtt_client = utils.setup_mqtt('GPIO', ip, port, on_message, led=led)

    button = Button(27, bounce_time=0.01)
    button.when_pressed = lambda: on_button_pressed(mqtt_client, led)

    signal.pause()


if __name__ == '__main__':
    main()
