# Sudoku TUI - Spielanleitung

## Installation

```bash
# Installation im Development-Modus
cd /home/elyo/.config/elyo/soduku
uv pip install -e .
```

## Starten

```bash
# App starten
uv run sudoku

# Oder direkt
uv run python -m sudoku.main
```

## Steuerung

### Tastatur-Layout (QWERTZ)

**Zahlen eingeben (linke Hand):**
- `q` = 1
- `w` = 2
- `e` = 3
- `r` = 4
- `t` = 5
- `z` = 6
- `u` = 7
- `i` = 8
- `o` = 9

**Alternative:** Normale Zahlentasten 1-9 funktionieren auch

**Cursor-Navigation (Vim-Style):**
- `h` = links
- `j` = runter
- `k` = hoch
- `l` = rechts

**Alternative:** Pfeiltasten funktionieren auch

**Aktionen:**
- `x` oder `Delete` oder `Backspace` = Zelle löschen
- `n` = Neues Spiel
- `s` = Statistiken anzeigen
- `Escape` = Zurück zum Menü
- `Ctrl+C` oder `Ctrl+Q` = Beenden

## Spielmodi

### Schwierigkeitsgrade
- **Leicht (Easy):** 30-40% der Zahlen werden entfernt
- **Mittel (Medium):** 45-55% der Zahlen werden entfernt
- **Schwer (Hard):** 60-65% der Zahlen werden entfernt

### Spielfeldgrößen
- **3x3 (Standard):** 9x9 Gitter mit 3x3 Boxen
- **3x2 (Variant):** 6x6 Gitter mit 3x2 Boxen

## Farbcodierung

- **Blau/Fett:** Vorgegebene (fixe) Zahlen
- **Weiß:** Ihre eingegebenen Zahlen
- **Rot:** Fehlerhafte Zahlen (Regelverstoß)
- **Cyan Hintergrund:** Aktuelle Cursor-Position
- **Grau/Dim:** Leere Zellen

## Statistiken

Die App speichert automatisch Ihre Spielstatistiken:
- Anzahl gespielter Spiele pro Schwierigkeitsgrad
- Anzahl gewonnener Spiele
- Durchschnittliche Spielzeit
- Gewinnrate

Statistiken werden in `~/.sudoku/statistics.json` gespeichert.

## Spielablauf

1. **Spielername eingeben:** Geben Sie Ihren Namen ein
2. **Schwierigkeitsgrad wählen:** Easy, Medium oder Hard
3. **Spielen:**
   - Navigieren Sie mit `hjkl` oder Pfeiltasten
   - Geben Sie Zahlen mit `qwertzuio` oder 1-9 ein
   - Löschen Sie Fehler mit `x`
4. **Gewinnen:** Füllen Sie alle Zellen korrekt aus
5. **Statistiken:** Sehen Sie Ihre Fortschritte mit `s`

## Tipps

- Die App validiert Ihre Eingaben in Echtzeit
- Fehlerhafte Zahlen werden rot markiert
- Sie können ein Spiel pausieren (Escape → Menü)
- Die Zeit läuft nur während des aktiven Spiels

## Architektur

Die App folgt **Clean Architecture** Prinzipien:
- **Domain Layer:** Geschäftslogik (Board, Game, Player)
- **Application Layer:** Use Cases (StartNewGame, MakeMove)
- **Infrastructure Layer:** Generator, Validator, Solver, TUI
- **Presentation Layer:** Controller

Alle Komponenten folgen **SOLID-Prinzipien** und **Clean Code** Best Practices.

## Tests ausführen

```bash
# Alle Tests
uv run pytest tests/

# Mit Coverage
uv run pytest tests/ --cov=src/sudoku --cov-report=html

# Nur Domain-Tests
uv run pytest tests/unit/domain/

# Nur Integration-Tests
uv run pytest tests/integration/
```

## Code-Qualität prüfen

```bash
# Linting
uv run ruff check src/

# Type-Checking
uv run pyright src/sudoku

# Formatierung
uv run ruff format src/
```

## Probleme?

Falls die App nicht startet:
1. Prüfen Sie die Installation: `uv pip list | grep sudoku`
2. Prüfen Sie Python-Version: `python --version` (benötigt >=3.11)
3. Installieren Sie Dependencies neu: `uv pip install -e ".[dev]"`

Viel Spaß beim Sudoku-Spielen! 🎮
