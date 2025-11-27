"""Konsolen-Einstiegspunkt für das Mitschrift-Tool.

Der Flow:
- Lizenz prüfen und speichern
- Mikrofon auswählen
- Menü für Live-Mitschrift oder nachträgliche Verbesserung
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from audio_transcriber import AudioTranscriber
from gpt_client import emergency_help, improve_notes
from license_client import LicenseError, check_license

CONFIG_PATH = Path("config.json")
RAW_PATH = Path("mitschrift_raw.txt")
IMPROVED_PATH = Path("mitschrift_verbessert.txt")


def load_config() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {}
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print("Warnung: config.json ist beschädigt. Es wird eine neue Datei angelegt.")
        return {}


def save_config(config: Dict[str, Any]) -> None:
    CONFIG_PATH.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")


def ensure_license(config: Dict[str, Any]) -> Dict[str, Any]:
    key = config.get("license_key")
    if not key:
        key = input("Bitte Lizenzschlüssel eingeben: ").strip()
    try:
        info = check_license(key)
    except LicenseError as exc:
        print(f"Lizenzprüfung fehlgeschlagen: {exc}")
        raise SystemExit(1)
    config["license_key"] = key
    save_config(config)
    print(f"Lizenz erfolgreich geprüft. Plan: {info.get('plan', 'unbekannt')}, gültig bis: {info.get('expires', 'unbekannt')}")
    return config


def select_microphone(config: Dict[str, Any]) -> Dict[str, Any]:
    if "mic_device_id" in config:
        return config

    print("Kein Mikrofon hinterlegt. Verfügbare Geräte:")
    devices = AudioTranscriber.list_input_devices()
    for idx, name in devices:
        print(f"  [{idx}] {name}")

    while True:
        choice = input("Bitte ID des gewünschten Mikrofons eingeben: ").strip()
        if choice.isdigit():
            config["mic_device_id"] = int(choice)
            save_config(config)
            return config
        print("Ungültige Eingabe. Bitte eine Zahl eingeben.")


def run_live_transcription(config: Dict[str, Any]) -> None:
    transcriber = AudioTranscriber(
        device_id=config.get("mic_device_id"),
        sample_rate=16000,
        block_duration=5,
        language=config.get("language", "de"),
    )
    try:
        transcriber.start()
    except Exception as exc:  # pragma: no cover - Laufzeitabhängig
        print(f"Fehler beim Start der Aufnahme: {exc}")
        return

    print("Live-Mitschrift läuft. Drücke 'n' für Notfall-Hilfe, 'q' zum Beenden.")
    while True:
        choice = input("Aktion (n/q): ").strip().lower()
        if choice == "q":
            break
        if choice == "n":
            context = transcriber.get_recent_text()
            if not context:
                print("Noch keine Transkription verfügbar.")
                continue
            print("Notfall-Hilfe wird angefragt...")
            try:
                result = emergency_help(context, license_key=config["license_key"])
            except Exception as exc:  # pragma: no cover - Laufzeitabhängig
                print(f"Fehler bei der Notfall-Anfrage: {exc}")
                continue
            print("Kurze Antwort:")
            print(result.get("short_answer", "(keine Daten)") or "(leer)")
            print("\nAusführliche Erklärung:")
            print(result.get("detailed_explanation", "(keine Daten)") or "(leer)")

    print("Mitschrift wird beendet...")
    transcriber.stop()

    choice = input("Mitschrift jetzt verbessern lassen? (j/n): ").strip().lower()
    if choice == "j":
        if not RAW_PATH.exists():
            print("Keine Mitschrift-Datei gefunden.")
            return
        full_text = RAW_PATH.read_text(encoding="utf-8")
        try:
            improved = improve_notes(full_text, license_key=config["license_key"])
        except Exception as exc:  # pragma: no cover - Laufzeitabhängig
            print(f"Fehler bei der Verbesserung: {exc}")
            return
        IMPROVED_PATH.write_text(improved, encoding="utf-8")
        print(f"Verbesserte Version wurde in {IMPROVED_PATH} gespeichert.")


def run_improvement_only(config: Dict[str, Any]) -> None:
    filename = input(f"Dateiname der Mitschrift (Standard: {RAW_PATH.name}): ").strip()
    path = Path(filename) if filename else RAW_PATH
    if not path.exists():
        print(f"Datei {path} wurde nicht gefunden.")
        return
    text = path.read_text(encoding="utf-8")
    try:
        improved = improve_notes(text, license_key=config["license_key"])
    except Exception as exc:  # pragma: no cover - Laufzeitabhängig
        print(f"Fehler bei der Verbesserung: {exc}")
        return
    IMPROVED_PATH.write_text(improved, encoding="utf-8")
    print(f"Verbesserte Version wurde in {IMPROVED_PATH} gespeichert.")


def main() -> None:
    config = load_config()
    config = ensure_license(config)
    config = select_microphone(config)

    while True:
        print("\nBitte Option wählen:")
        print("[1] Live-Mitschrift starten")
        print("[2] Vorhandene Mitschrift verbessern")
        print("[3] Programm beenden")
        choice = input("Auswahl: ").strip()
        if choice == "1":
            run_live_transcription(config)
        elif choice == "2":
            run_improvement_only(config)
        elif choice == "3":
            print("Auf Wiedersehen!")
            break
        else:
            print("Ungültige Auswahl. Bitte 1, 2 oder 3 eingeben.")


if __name__ == "__main__":
    main()
