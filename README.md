# Polski asystent głosowy

Asystent został stworzony jako projekt w ramach przedmiotu "Programowanie w języku Python" w trakcie studiów Informatyki na WIEiT AGH (semestr letni 2020/21).

## Opis projektu

Projekt ten jest realizacją prostego asystenta głosowego, z którym możemy rozmawiać w języku polskim. Został on napisany w języku Python i podzielony na moduły, które komunikują się za pomocą protokołu MQTT. Asystent rozpoznaje i odpowiada na polecenia dotyczące:

- prostej konwersacji i podstawowych pytań,
- aktualnej pogody w danym miejscu,
- godziny i daty,
- opowiadania żartów,
- odtwarzania muzyki,
- zarządzania notatkami (dodawanie/usuwanie/odczytywanie),
- wyszukiwanie informacji na Wikipedii.

## Wymagania

Do uruchomienia asystenta na Raspberry Pi konieczne jest zainstalowanie następującego oprogramowania:

- Python 3,
- python3-gpiozero (do obsługi GPIO),
- mosquitto (broker MQTT),
- vlc (odtwarzacz multimediów),
- pulseaudio/oprogramowanie obsługujące mikrofon i głośnik.

Dodatkowo, wymagane są pakiety Pythona 3 (możliwe do zainstalowania przez pip3):

- numpy,
- gpiozero,
- python-vlc,
- speech_recognition,
- gtts,
- pyowm,
- wikipedia,
- paho-mqtt.

Asystent został przystosowany do działania i przetestowany na systemie Raspberry Pi OS na urządzeniu Raspberry Pi Zero W. Do działania wymagane jest również posiadanie mikrofonu, głośnika oraz przycisku i diody LED podłączonych do pinów GPIO (odpowiednio nr 27 oraz 3).

## Uruchomienie

Po zainstalowaniu oraz włączeniu wymaganych elementów, projekt można uruchomić za pomocą skrytpu bash'owego `assistant.sh`. Skrypt uruchamia na raz wszystkie moduły asystenta, ma możliwość ustawienia adresu i portu brokera MQTT przez podanie ich jako argumenty. Możliwe jest również uruchamianie poszczególnych modułów ręcznie - wówczas z pozycji głównego katalogu (tego, w którym umieszczony został skrypt `assistant.sh` i folder `assistant`) należy uruchomić dany moduł za pomocą polecenia `python3 -m assistant_* [ip] [port]`.

## Moduły asystenta

Asystent został podzielony na wiele małych modułów, każdy z nich jest odpowiedzialny za jedną z funkcjonalności programu. Taka budowa pozwala na łatwe modyfikowanie i rozszerzanie projektu (nawet bez konieczności wyłączania asystenta). Aby dodać nowe polecenia, wystarczy je zakodować w pliku `commands.txt` w folderze `assistant/assistant_bot`, uruchomić napisany moduł oraz zrestartować bota. Podobnie jest z modyfikacją istniejącego modułu, wystarczy go uruchomić ponownie. Dodatkowo moduły są od siebie niezależne i komunikują się za pomocą protokołu MQTT, zatem awaria w jednym z nich nie powoduje przerwania działania całego programu.

Oto krótki opis każdego z modułów:
1. GPIO - odpowiedzialny za wykrycie naciśnięcia przycisku (zainicjowanie interakcji z asystentem) oraz diody LED (włączona gdy nasłuchuje; wyłączona gdy jest w stanie spoczynku; pulsująca gdy asystent odpowiada na pytanie lub przygotowuje odpowiedź), korzysta z `gpiozero`.
2. STT - moduł konwertujący głos nagrany przez mikrofon na tekst (za pomocą biblioteki `speech_recognition`).
3. TTS - konwersja tekstu na plik dźwiękowy z mową i jego odtworzenie (biblioteki `gtts` oraz `vlc`).
4. bot - moduł dopasowujący otrzymany tekst do jednej z komend zapisanych w pliku `commands.txt`. Dopasowanie odbywa się poprzez zbudowanie wektora N-gramów $(n = 3)$ dla wszystkich komend z pliku i danego tekstu oraz wyznaczenie podobieństwa za pomocą metryki cosinusowej. Jeśli podobieństwo jest większe, niż pewien próg `min_cos`, wybierana jest komenda, która ma największy wskaźnik podobieństwa; w przeciwnym przypadku komendy nie ma w systemie i asystent nie będzie potrafił odpowiedzieć na dane polecenie. Moduł ten odpowiada jedynie za rozpoznanie komendy - gdy już to zrobi, wysyła polecenie do innego modułu, który jest odpowiedzialny za obsługę tej czynności.
5. jokes - moduł losujący żart z pliku `assistant/assistant_jokes/jokes.txt` i odczytujący go.
6. music - moduł losujący plik muzyczny z katalogu `config.MUSIC_FOLDER` oraz odtwarzający go.
7. notes - akcje dodawania, usuwania oraz odczytywania notatek. Notatki są zapisywane w pliku `assistant_notes.pkl` za pomocą modułu `pickle`, aby można je było odczytać również po ponownym uruchomieniu asystenta.
8. time - odczytanie aktualnej godziny lub daty.
9. weather - moduł pobierający aktualną pogodę w danym mieście za pomocą OpenWeatherMap API oraz biblioteki `pyowm`, interpretujący pobrane dane oraz odczytujący najważniejsze informacje. 
10. web - wyszukiwanie informacji na Wikipedii za pośrednictwem biblioteki `wikipedia`. Moduł stara się wyszukać najbardziej zbliżony artykuł, pobiera go oraz odczytuje kilka zdań podsumowania na dany temat.
11. config - moduł zawierające stałe wykorzystywane w programie (np. napisy tematów poszczególnych modułów), ścieżki do plików lub stałe do konfiguracji (np. klucz do OWM API).
12. utils - funkcje pomocnicze wykorzystywane we wszystkich modułach - konfiguracja MQTT, pobranie parametrów z wejścia, odczytywanie na głos odpowiedzi wraz ze wskazaniem modułu, który należy poinformować, że odtwarzanie się zakończyło.

## Komunikacja między modułami

Na przykładzie odczytywania aktualnej pogody, przedstawię przepływ informacji między modułami w moim programie:

1. Po naciśnięciu przycisku, moduł GPIO wysyła informację do modułu STT, aby rozpocząć nasłuchiwanie.
2. Po rozpoznaniu mowy na nagraniu, moduł STT wysyła informację do modułu bota z tekstem.
3. Bot rozpoznaje komendę i wysyła informację do modułu weather.
4. Moduł weather chce odczytać komunikat o wyborze miasta, zatem wysyła tekst z informacją do modułu TTS.
5. TTS wysyła informację do weather o zakończeniu odtwarzania wiadomości.
6. Weather prosi moduł STT o nasłuchiwanie.
7. Po rozpoznaniu głosu, STT odpowiada do weather wiadomością z tekstem.
8. Weather pobiera informacje o pogodzie, generuje odpowiedź dla użytkownika i wysyła ją do TTS.
9. TTS odczytuje na głos wiadomość, a na koniec informuje moduł bot o zakończeniu działania (bot wyłącza diodę LED i kończy interakcję z użytkownikiem).
