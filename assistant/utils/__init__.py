from .. import config
import paho.mqtt.client as mqtt
import signal
import atexit
import os


def _on_close(mqtt_client, module_name):
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    print(f'Assistant {module_name} module closed')


def _on_sigint(signum, frame):
    exit(0)


def setup_mqtt(module_name, ip, port, on_message, client_name=None, subscribe=None, **kwargs):
    if client_name is None:
        client_name = f'assistant_{module_name.lower()}'

    if subscribe is None:
        subscribe = [f'assistant/{module_name.lower()}']
    elif not isinstance(subscribe, list):
        subscribe = [subscribe]

    mqtt_client = mqtt.Client(client_name)
    mqtt_client.on_message = lambda client, userdata, message: on_message(client, message, **kwargs)
    mqtt_client.connect(ip, port)

    atexit.register(lambda: _on_close(mqtt_client, module_name))
    signal.signal(signal.SIGINT, _on_sigint)

    mqtt_client.subscribe([(channel, 0) for channel in subscribe])
    mqtt_client.loop_start()

    print(f'Assistant {module_name} module started, PID={os.getpid()}')
    return mqtt_client


def get_connection_args(argv):
    if len(argv) == 1:
        return '127.0.0.1', 1883
    elif len(argv) == 2:
        return argv[1], 1883
    else:
        return argv[1], int(argv[2])


def read_aloud(mqtt_client, text, send_to=None):
    send_to = send_to if send_to is not None else config.BOT_TOPIC
    mqtt_client.publish(config.TTS_TOPIC, f'{send_to}#{text}')
