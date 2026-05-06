# Projektüberblick

Stand: 2026-05-06

## Kurzfassung

Das Projekt ist ein Python-Codebase rund um Telemetrieanalyse für Assetto Corsa Competizione. Der Kern ist bereits klar erkennbar:

- MoTeC-CSV-Dateien werden geladen und auf einen einheitlichen Distanzraster normalisiert.
- Track-Metadaten aus JSON-Dateien werden mit Telemetrie zusammengeführt.
- Daraus werden pro Runde Segmente und Kurven analysiert.
- Die Analysen werden als Dataclasses, DataFrames und Exportdateien weiterverarbeitet.
- Daneben gibt es erste LLM- und ML-Experimente sowie ein kleines Streamlit-Dashboard.

Der produktiv wirkende Schwerpunkt liegt aktuell klar auf `src/lap` und `src/telemetry`. Die LLM-, ML- und Score-Bausteine wirken eher experimentell oder unvollständig.

## Repo-Struktur auf einen Blick

### Wichtige Root-Ordner

- `src/`
  - eigentlicher Anwendungscode
- `test_output/`
  - Exportziel für erzeugte CSV-/Excel-Dateien
- `logs/`, `.log/`
  - Laufzeit- und Analyse-Logs
- `old/`
  - ältere Skripte und historische Telemetriedateien
- `scratchbook/`
  - Experimente, Notizen, Plot- und Streamlit-Spielwiese
- `_information/`
  - Referenzmaterial und Domain-Notizen
- `_brain_factory/`
  - konzeptionelle Sammlung, Ideenspeicher, Obsidian-Inhalte

### Relevante Dateien im Root

- `requirements.txt`
  - Abhängigkeiten für Data/ML/Streamlit
- `.env`
  - enthält Laufzeit-Secret(s); sollte nicht im Repo landen
- `lap_telemetry_log.log`
  - erzeugtes Laufzeitlog im Projektroot

## Fachliches Zielbild

Das Projekt sieht nach einem "ACC Driver Coach" aus:

- Fahrertelemetrie aus ACC / MoTeC analysieren
- Kurven- und Segmentverhalten strukturiert bewerten
- daraus Coaching-, Vergleichs- oder Setup-Hinweise ableiten
- perspektivisch LLMs und ML für Empfehlung, Erklärung und Auswertung nutzen

Es gibt zusätzlich Anzeichen für folgende Nebenpfade:

- Setup-Parsing von ACC-Setup-Dateien
- Setup-Beratung per Gemini Function Calling
- Prädiktive oder erklärende ML-Auswertung auf Basis exportierter Lap-Features

## Technischer Datenfluss

Der aktuelle Hauptpfad ist:

1. Telemetrie-Datei aus `src/assets/MoTec/<track>/telemetry_files/`
2. Laden der Track-Metadaten aus
   - `<track>_segments.json`
   - `<track>_corners.json`
3. Resampling der MoTeC-Daten auf integer `Distance`
4. As-of-Merge von Segment- und Kurvenmetadaten auf die Telemetrie
5. Berechnung zusätzlicher Kennwerte wie `gForceVector`
6. Aufbau eines `LapModel`
7. Ableitung von
   - Kurvenmodellen (`CornerModel`)
   - Segmentmetriken
   - Export-DataFrames
8. Optionaler Export nach CSV/Excel oder Anzeige im Dashboard

## Zentrale Module

### `src/main.py`

Funktioniert aktuell als Batch-Einstieg für Datensammlung und Export.

Aufgaben:

- sammelt alle Telemetrie-Dateien für einen Track
- lädt jede Runde über `TelemetryLoader`
- baut pro Runde ein `LapModel`
- sammelt alle analysierten Kurven in einem gemeinsamen DataFrame
- schreibt Ergebnisse nach `test_output/<track>.csv` und `test_output/<track>.xlsx`

Auffällig:

- harte Pfade und Tracknamen
- eher Skript als stabiler Applikationseinstieg
- `load_raw_telemetry_df_from_file_path()` baut einen Pfad relativ zu `assets/...`, während an anderen Stellen `src/assets/...` verwendet wird

### `src/telemetry/telemetry_loader.py`

Das ist der wichtigste technische Einstiegspunkt.

Verantwortung:

- MoTeC-CSV einlesen
- erste Headerzeilen überspringen
- Telemetrie auf einen 1-Meter-Raster interpolieren
- Segment- und Kurven-Metadaten aus JSON laden
- Metadaten per `merge_asof` an Telemetrie anheften
- Kurvenlabels nach `cornerEnd_m` wieder ausnullen
- `gForceVector` ergänzen

Stärken:

- klarer Pipeline-Charakter
- Track-spezifische Assets sind sauber getrennt
- Resampling und Merge-Logik sind fachlich nachvollziehbar

Risiken:

- Trackliste ist statisch (`TRACKS = ["spa", "donnington", "brands_hatch"]`)
- uneinheitliche Pfadkonventionen
- einzelne Strings/Kommentare deuten auf Encoding-Probleme hin

### `src/telemetry/telemetry_calculator.py`

Stellt numerische Hilfsfunktionen bereit.

Enthalten sind u. a.:

- `calc_g_force_vector`
- Änderungsraten
- Varianz/Stabilität
- Korrelationen
- Integrale
- Quantile
- Umrechnung Raddrehzahl -> Geschwindigkeit

Einordnung:

- sinnvoll als gemeinsame Mathe-/Feature-Bibliothek
- wird bereits produktiv genutzt
- enthält noch TODOs zu Validation und Fehlerbehandlung

### `src/lap/lap_model.py`

Das ist die zentrale Domänenschicht für eine einzelne Runde.

Verantwortung:

- hält den normalisierten Raw-Lap-DataFrame
- baut Kurvenmodelle für alle `corner_id`
- analysiert alle Segmente
- stellt Zugriffsmethoden für Rohdaten, Kurvenmodelle und aggregierte DataFrames bereit

Wichtige Outputs:

- `corner_models: dict[int, CornerModel]`
- `segments_df`
- `get_all_analyzed_corners_as_df()`
- `get_raw_lap_df(...)`

Einordnung:

- aktuell der wichtigste Application-Service im Projekt
- bündelt die eigentliche Nutzung der Telemetriedaten

### `src/lap/corner/corner_model.py`

Stellt den Zugriff auf eine einzelne Kurve bereit.

Funktionen:

- hält den Raw-Corner-DataFrame
- baut ein `Corner`-Dataclass-Objekt
- liefert Daten als
  - Dataclass
  - Dict
  - DataFrame
  - JSON
- erlaubt Fenster innerhalb der Kurve, z. B. Brake Point bis Apex

Einordnung:

- ordentliche Access-Layer-Idee
- gut geeignet als API für Coaching- oder Vergleichslogik

### `src/lap/analyzer/`

Hier sitzt die eigentliche Metriklogik.

Wichtige Komponenten:

- `corner_analyzer.py`
  - orchestriert Unteranalysen für Speed, Steer, Throttle, Brake, G-Force
- `segment_analyzer.py`
  - fasst lineare Streckenabschnitte zusammen
- `brake_analyzer.py`
- `speed_analyzer.py`
- `steer_analyzer.py`
- `throttle_analyzer.py`
- `gforce_analyzer.py`

Einordnung:

- das ist der analytische Kern des Projekts
- Struktur ist bereits brauchbar modularisiert
- die vorhandenen Änderungen im Git-Status deuten darauf hin, dass hier aktiv gearbeitet wird

### `src/lap/lap_dataclasses.py`

Definiert die Transportobjekte des Projekts.

Vorhanden sind u. a.:

- atomare Metriken
  - `SpeedMetrics`
  - `BrakeMetrics`
  - `ThrottleMetrics`
  - `SteerMetrics`
  - `GForceMetrics`
- zusammengesetzte Objekte
  - `CarDynamics`
  - `DriverPerformance`
  - `CornerMetrics`
  - `Corner`
  - `Lap`
  - `SegmentMetrics`
  - `Segment`

Stärken:

- gutes Domain-Modell
- Statusprotokoll über `ok` / `empty` / `invalid`

Auffälligkeit:

- die Datei enthält offensichtlich doppelte bzw. versehentlich verschachtelte Dataclass-Definitionen im Bereich `SegmentMetrics`
- das ist ein technischer Hotspot und sollte bereinigt werden

### `src/lap/adapter.py`

Konvertiert Dataclasses rekursiv nach:

- Dict
- JSON
- DataFrame

Einordnung:

- sinnvoller Infrastrukturbaustein
- wichtig für Export und UI-Anbindung

### `src/lap/dataframe_validation.py`

Kapselt DataFrame-Prüfungen:

- leer / nicht leer
- Pflichtspalten vorhanden
- `Distance` nicht als Float

Einordnung:

- gute zentrale Stelle für Guards
- wird bereits in mehreren Modulen genutzt

### `src/telemetry/telemetry_dashboard.py`

Erstes Streamlit-Dashboard für Telemetrieanzeige.

Was es tut:

- Tracks aus `assets/MoTec` lesen
- CSV-Dateien auswählen
- Runde laden
- nach Segment und Kurve filtern
- `gForceVector` als Line Chart anzeigen

Probleme im aktuellen Stand:

- inkonsistente Imports (`from telemetry_loader import TelemetryLoader`)
- Dateisuche passt nicht zur tatsächlichen Struktur der Telemetrie-Unterordner
- eher Prototyp als lauffertiges Frontend

### `src/setup/setup_parser.py`

Parser für ACC-Setup-Dateien.

Liest u. a. aus:

- Reifen und Alignment
- Elektronik
- Mechanical Balance
- Dämpfer
- Aero

Einordnung:

- fachlich nützlich
- aktuell skriptartig aufgebaut
- top-level `open(...)` beim Import ist für Bibliothekscode problematisch

### `src/llm/`

Aktuell eher Experimentierbereich.

- `geimini_tryout.py`
  - Gemini-Integration mit Function Calling und Setup-Abfrage
- `practice_01.py`
  - Schema-/JSON-Ausgabeexperiment

Einordnung:

- noch nicht als stabile Anwendungsschicht integriert
- gemischte Sprache, feste Pfade, direkte CLI-Interaktion

### `src/ml/model_01.py`

Früher ML-Prototyp auf exportierten Lap-Features.

Genutzt werden:

- `scikit-learn`
- `Pipeline`
- `SimpleImputer`
- `StandardScaler`
- `LinearRegression`

Einordnung:

- klar experimentell
- hängt von vorbereiteten Exportdateien ab
- kein integrierter Trainings- oder Evaluationsworkflow

### `src/lap/lap_comparer.py`

Vergleichsschicht für Runden, aber noch nicht konsolidiert.

Auffällig:

- hängt noch am alten Analyzer (`_OLD_lap_analyzer`)
- wirkt nicht auf dem aktuellen `LapModel`-Pfad aufgebaut
- enthält unvollständige Methoden

## Assets und Daten

### Track-Assets

Unter `src/assets/MoTec/` liegen pro Track:

- `<track>_corners.json`
- `<track>_segments.json`
- optional `telemetry_files/` mit vielen CSV-Runden

Erkannte Tracks:

- `spa`
- `donnington`
- `brands_hatch`

### Prompt-Assets

Unter `src/assets/prompts/` liegen Textprompts für:

- Aero
- Dampers
- Electronics
- Manager
- Mechanical Grip
- Tyres

Das deutet auf geplante oder teilweise begonnene Setup-/Coaching-Pipelines hin.

### Setup-Assets

Unter `src/assets/setups/` liegen Beispiel- oder Platzhalter-Setups.

## Abhängigkeiten

Laut `requirements.txt` nutzt das Projekt im Kern:

- `pandas`
- `numpy`
- `pydantic`
- `scikit-learn`
- `pytest`, `pytest-cov`
- `python-dotenv`
- `protobuf`
- `colorama`
- `streamlit`
- `matplotlib`

Wichtige Beobachtung:

- Für die LLM-Skripte scheint zusätzlich `google-genai` oder ein ähnliches Google-SDK benötigt zu werden, steht aber nicht in `requirements.txt`.
- `openpyxl` wird in `main.py` für ExcelWriter implizit benötigt, ist aber ebenfalls nicht in `requirements.txt` aufgeführt.

## Reifegrad nach Bereichen

### Relativ ausgereift

- Telemetrie laden und normalisieren
- Track-Metadaten anreichern
- Kurven-/Segmentanalyse als Modulstruktur
- Dataclass- und DataFrame-Ausgabe

### Mittel

- Exportpfad über `main.py`
- Logging
- DataFrame-Validierung

### Früh / experimentell

- Streamlit-Dashboard
- LLM-Integration
- ML-Modelltraining
- Lap-Scoring-Module
- Lap-Vergleich auf neuer Architektur

## Technische Schulden und Risiken

### 1. Pfadkonsistenz

Im Repo existieren mehrere konkurrierende Pfadmuster:

- `src/assets/...`
- `assets/...`
- relative `../assets/...`

Das ist aktuell einer der größten praktischen Risikofaktoren für Ausführung, Tests und Wiederverwendung.

### 2. Unsaubere Trennung zwischen Bibliothek und Skript

Mehrere Module führen direkt beim Import Seiteneffekte aus, z. B.:

- Dateizugriffe
- `print(...)`
- direkte Initialisierungen

Das erschwert Wiederverwendung, Tests und modulare Integration.

### 3. Teilweise inkonsistente oder alte Codepfade

Beispiele:

- `lap_comparer.py` hängt an altem Analyzer-Code
- `_OLD_lap_analyzer.py` ist noch im produktionsnahen Importumfeld
- `telemetry_dashboard.py` passt nicht sauber zur aktuellen Asset-Struktur

### 4. Dataclass-Datei mit Strukturproblemen

`src/lap/lap_dataclasses.py` enthält erkennbare Doppelungen und verschachtelte Definitionen, die nicht wie beabsichtigt wirken. Das sollte priorisiert bereinigt werden, bevor weitere Features darauf aufbauen.

### 5. Fehlende echte Tests

Im Projekt selbst sind keine klaren Testmodule erkennbar. `pytest` ist zwar als Dependency vorhanden, aber eine projektweite Testsuite fehlt praktisch.

### 6. Secret-Handling

Die `.env` liegt im Workspace und enthält ein echtes API-Secret. Das ist aus Security-Sicht ein unmittelbarer Punkt:

- Secret nicht versionieren
- falls bereits geteilt oder gepusht: Key rotieren
- `.gitignore` und lokale Konfiguration prüfen

### 7. Encoding-Artefakte

Mehrere Dateien zeigen kaputte Sonderzeichen in Kommentaren/Docstrings. Das ist kein Laufzeitkiller, aber es senkt Lesbarkeit und wirkt auf Dauer erosiv.

## Git-Status zum Zeitpunkt der Sichtung

Im Worktree liegen bereits nicht von mir initiierte Änderungen vor, u. a. in:

- `.gitignore`
- `src/README.md`
- `src/lap/analyzer/brake_analyzer.py`
- `src/lap/analyzer/throttle_analyzer.py`
- `src/main.py`

Zusätzlich gibt es gelöschte bzw. entfernte Dateien. Das sollte bei jeder weiteren Arbeit am Projekt berücksichtigt werden.

## Mein Gesamtbild

Das Projekt hat einen klaren und brauchbaren Kern:

- Telemetrie normalisieren
- Trackkontext anreichern
- Kurven und Segmente in Domänenobjekte übersetzen
- daraus Feature- und Analyse-Outputs erzeugen

Das Fundament für einen echten "Driver Coach" ist also vorhanden. Der Unterschied zwischen Kern und Randbereichen ist aber deutlich:

- `telemetry/` und große Teile von `lap/` wirken wie der tragende Kern
- `llm/`, `ml/`, Dashboard und Scoring wirken wie angebundene oder geplante Ausbaupfade

## Empfohlene nächste Schritte

Wenn das Projekt konsolidiert werden soll, würde ich in dieser Reihenfolge arbeiten:

1. Pfad- und Einstiegspunktkonsistenz herstellen
2. `lap_dataclasses.py` bereinigen
3. `telemetry_dashboard.py` und `setup_parser.py` von Skriptverhalten auf saubere Module umbauen
4. kleine Testsuite für Loader, Validator und `LapModel` ergänzen
5. danach erst LLM-/ML- und Score-Schichten weiter integrieren

## Relevante Dateien für den Einstieg

- [src/main.py](/abs/path/C:/Users/Anwender/PycharmProjects/gemini api/src/main.py)
- [src/telemetry/telemetry_loader.py](/abs/path/C:/Users/Anwender/PycharmProjects/gemini api/src/telemetry/telemetry_loader.py)
- [src/telemetry/telemetry_calculator.py](/abs/path/C:/Users/Anwender/PycharmProjects/gemini api/src/telemetry/telemetry_calculator.py)
- [src/lap/lap_model.py](/abs/path/C:/Users/Anwender/PycharmProjects/gemini api/src/lap/lap_model.py)
- [src/lap/corner/corner_model.py](/abs/path/C:/Users/Anwender/PycharmProjects/gemini api/src/lap/corner/corner_model.py)
- [src/lap/analyzer/corner_analyzer.py](/abs/path/C:/Users/Anwender/PycharmProjects/gemini api/src/lap/analyzer/corner_analyzer.py)
- [src/lap/lap_dataclasses.py](/abs/path/C:/Users/Anwender/PycharmProjects/gemini api/src/lap/lap_dataclasses.py)
- [src/setup/setup_parser.py](/abs/path/C:/Users/Anwender/PycharmProjects/gemini api/src/setup/setup_parser.py)
- [src/telemetry/telemetry_dashboard.py](/abs/path/C:/Users/Anwender/PycharmProjects/gemini api/src/telemetry/telemetry_dashboard.py)
