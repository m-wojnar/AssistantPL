from .. import config
from .. import utils
import pickle
import signal
import sys


class NotesManager:
    def __init__(self):
        self._adding_title = True
        self._title = None

        try:
            with open(config.NOTES_FILE, 'rb') as file:
                self.notes = pickle.load(file)
        except:
            self.notes = {}

    def _save(self):
        with open(config.NOTES_FILE, 'wb') as file:
            pickle.dump(self.notes, file)

    def add(self, text):
        if self._adding_title:
            self._title = text
            self._adding_title = False
            return f'podaj treść notatki o tytule {text}', config.NOTES_ADD
        else:
            self.notes[self._title] = text
            self._title = None
            self._adding_title = True
            self._save()
            return f'dodano nową notatkę', None

    def list(self):
        if len(self.notes) == 0:
            return 'nie masz żadnych zapisanych notatek'
        else:
            return ''.join(f'tytuł notatki: {key}, treść: {value},' for key, value in self.notes.items())

    def remove(self, title):
        if title not in self.notes:
            return f'nie masz notatki o tytule: {title}'
        else:
            del self.notes[title]
            self._save()
            return f'usunięto notatkę o tytule: {title}'


def on_message(mqtt_client, message, notes):
    text = message.payload.decode('utf-8')

    if text == config.NOTES_ADD:
        on_message.mode = config.NOTES_ADD
        utils.read_aloud(mqtt_client, 'podaj tytuł notatki, którą chcesz dodać', config.NOTES_TOPIC)
    elif text == config.NOTES_REMOVE:
        on_message.mode = config.NOTES_REMOVE
        utils.read_aloud(mqtt_client, 'podaj tytuł notatki, którą chcesz usunąć', config.NOTES_TOPIC)
    elif text == config.NOTES_LIST:
        utils.read_aloud(mqtt_client, notes.list())
    elif text == config.TTS_FINISHED and on_message.mode is not None:
        mqtt_client.publish(config.GPIO_TOPIC, config.GPIO_LED_ON)
        mqtt_client.publish(config.STT_TOPIC, config.NOTES_TOPIC)
    elif on_message.mode is not None:
        if on_message.mode == config.NOTES_ADD:
            response, on_message.mode = notes.add(text)
        elif on_message.mode == config.NOTES_REMOVE:
            response = notes.remove(text)
            on_message.mode = None

        if on_message.mode is not None:
            utils.read_aloud(mqtt_client, response, config.NOTES_TOPIC)
        else:
            utils.read_aloud(mqtt_client, response)


def main():
    ip, port = utils.get_connection_args(sys.argv)
    utils.setup_mqtt('notes', ip, port, on_message, notes=NotesManager())
    signal.pause()


if __name__ == '__main__':
    main()
