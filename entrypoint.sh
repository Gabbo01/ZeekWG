#!/bin/bash
set -e

# Se vuoi eseguire qualcosa con Zeek all'avvio:
# zeek -r /pcap/input.pcap

# Avvia Flask
exec python3 app.py
