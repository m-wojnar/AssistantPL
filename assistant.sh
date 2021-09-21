#!/bin/bash

# Maksymilian Wojnar

if [[ $# -gt 2 ]]; then
	echo "Użycie skryptu: ./assistant.sh [ip] [port]"
	exit 1
fi

if [[ $# -lt 2 ]]; then
	port="1883"
else
	port=$2
fi

if [[ $# -lt 1 ]]; then
	ip="127.0.0.1"
else
	ip=$1
fi

declare -a pids=()
modules=('gpio' 'tts' 'stt' 'bot' 'jokes' 'time' 'web' 'notes' 'weather' 'music')

for module in "${modules[@]}"; do
	python3 -m "assistant.assistant_${module}" $ip $port &
	pids+=($!)
done

read -p $'Naciśnij enter po załadowaniu wszystkich modułów, aby zakończyć działanie asystenta\n\n'

for pid in "${pids[@]}"; do
	kill -SIGINT $pid
done




