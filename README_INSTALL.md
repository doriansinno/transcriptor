# Installation und Nutzung

Diese Anleitung führt Schritt für Schritt durch die Einrichtung des lokalen Mitschrift-Tools auf Windows.

## 1. Python installieren
1. Lade die aktuelle Python-3.12-Version von [python.org/downloads](https://www.python.org/downloads/) herunter.
2. Während der Installation unbedingt den Haken **"Add Python to PATH"** setzen.
3. Installation abschließen.

## 2. Projekt vorbereiten
1. Lade den Projektordner auf deinen Rechner (z. B. per ZIP oder Git).
2. Öffne eine Eingabeaufforderung im Projektordner `mitschrift_tool`.

## 3. Abhängigkeiten installieren
Führe im Projektordner aus:

```bash
pip install -r requirements.txt
```

Falls beim Whisper-Download Fehler auftreten, bitte sicherstellen, dass `ffmpeg` installiert und im PATH verfügbar ist.

## 4. Programm starten
Starte das Tool mit:

```bash
python main.py
```

Beim ersten Start wirst du nach deinem Lizenzschlüssel gefragt. Anschließend wählst du die ID deines gewünschten Mikrofons aus der angezeigten Liste. Beides wird in `config.json` gespeichert.

## 5. Mitschrift verwenden
- **Option 1: Live-Mitschrift starten**: Das Tool nimmt über das gewählte Mikrofon auf, transkribiert live mit Whisper und schreibt fortlaufend in `mitschrift_raw.txt`.
  - Taste `n`: Notfall-Hilfe anfordern (letzte Blöcke werden an den Server geschickt).
  - Taste `q`: Mitschrift beenden.
  - Nach dem Beenden kannst du sofort eine Verbesserung anstoßen; das Ergebnis landet in `mitschrift_verbessert.txt`.
- **Option 2: Vorhandene Mitschrift verbessern**: Nutzt eine bestehende Textdatei (Standard: `mitschrift_raw.txt`) und speichert die optimierte Version in `mitschrift_verbessert.txt`.

## 6. Dateien finden
- `config.json`: Einstellungen wie Lizenzschlüssel und Mikrofon-ID.
- `mitschrift_raw.txt`: Roh-Transkript der Aufnahmen.
- `mitschrift_verbessert.txt`: Ausgabe der Verbesserung durch deinen Server.

Viel Erfolg beim Lernen! Bei Fehlermeldungen bitte Internetverbindung, Lizenzschlüssel oder Mikrofon-Einstellungen prüfen.
