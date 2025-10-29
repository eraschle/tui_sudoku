# Emacs Setup für Sudoku TUI

## Voraussetzungen

### Erforderliche Emacs-Pakete

```elisp
;; In deiner init.el oder .emacs
(use-package python-mode
  :ensure t)

(use-package python-pytest
  :ensure t
  :after python-mode)

(use-package flycheck
  :ensure t
  :init (global-flycheck-mode))

(use-package projectile
  :ensure t
  :init (projectile-mode +1))
```

## Konfiguration

Die Projekt-Konfiguration ist bereits in `.dir-locals.el` vorhanden. Emacs lädt diese automatisch.

### Manuelle Konfiguration (optional)

Falls `.dir-locals.el` nicht funktioniert, füge dies zu deiner init.el hinzu:

```elisp
;; Sudoku TUI Project Settings
(defun my/sudoku-project-setup ()
  "Setup für Sudoku TUI Projekt."
  (when (string-match-p "soduku" (or (buffer-file-name) ""))
    (setq-local python-pytest-executable "uv run pytest")
    (setq-local python-check-command "uv run ruff check")
    (setq-local flycheck-python-pyright-executable "uv run pyright")
    (setq-local flycheck-python-ruff-executable "uv run ruff")))

(add-hook 'python-mode-hook #'my/sudoku-project-setup)
```

## Tests ausführen

### Mit python-pytest

**Alle Tests:**
```
M-x python-pytest
```

**Aktuellen Test:**
```
M-x python-pytest-function (C-c C-t t)
```

**Test-Datei:**
```
M-x python-pytest-file (C-c C-t f)
```

**Test unter Cursor:**
Cursor auf Test-Funktion setzen:
```
M-x python-pytest-function
```

### Mit Compilation Mode

**Alle Tests:**
```
M-x compile RET uv run pytest tests/
```

**Spezifische Tests:**
```
M-x compile RET uv run pytest tests/unit/domain/test_cell.py
```

**Mit Optionen:**
```
M-x compile RET uv run pytest tests/ -v -k test_cell
```

## Test-Kommandos im Detail

### Pytest Optionen

```bash
# Alle Tests
uv run pytest

# Mit verbose output
uv run pytest -v

# Nur fehlgeschlagene
uv run pytest --lf

# Bis zum ersten Fehler
uv run pytest -x

# Bestimmte Datei
uv run pytest tests/unit/domain/test_cell.py

# Bestimmte Test-Funktion
uv run pytest tests/unit/domain/test_cell.py::test_cell_creation

# Mit Pattern
uv run pytest -k "cell"

# Nur Unit-Tests
uv run pytest -m unit

# Nur Integration-Tests
uv run pytest -m integration

# Mit Coverage
uv run pytest --cov=src/sudoku --cov-report=html
```

## Keybindings (mit python-pytest)

Standardmäßig sind folgende Keybindings verfügbar:

- `C-c C-t t` - Test unter Cursor ausführen
- `C-c C-t f` - Alle Tests in Datei ausführen
- `C-c C-t p` - Alle Tests im Projekt ausführen
- `C-c C-t r` - Tests erneut ausführen
- `C-c C-t l` - Nur letzte fehlgeschlagene Tests

## Flycheck (Linting/Type Checking)

Flycheck sollte automatisch aktiviert sein und folgende Checker verwenden:
- **python-ruff** - Linting
- **python-pyright** - Type Checking

### Flycheck manuell ausführen

```
M-x flycheck-verify-setup     # Checker-Status prüfen
M-x flycheck-list-errors      # Fehler-Liste anzeigen
M-x flycheck-next-error       # Nächster Fehler
M-x flycheck-previous-error   # Vorheriger Fehler
```

## LSP Mode (optional, empfohlen)

Für beste Entwicklungserfahrung mit Python LSP:

```elisp
(use-package lsp-mode
  :ensure t
  :hook ((python-mode . lsp-deferred))
  :commands (lsp lsp-deferred)
  :config
  (setq lsp-pyright-use-library-code-for-types t)
  (setq lsp-pyright-diagnostic-mode "workspace"))

(use-package lsp-ui
  :ensure t
  :commands lsp-ui-mode
  :config
  (setq lsp-ui-doc-enable t)
  (setq lsp-ui-doc-position 'at-point))

(use-package lsp-pyright
  :ensure t
  :hook (python-mode . (lambda ()
                         (require 'lsp-pyright)
                         (lsp-deferred))))
```

## Debugging mit DAP

```elisp
(use-package dap-mode
  :ensure t
  :after lsp-mode
  :config
  (dap-auto-configure-mode)
  (require 'dap-python))
```

**Debug Test starten:**
```
M-x dap-debug
```

## Projektile Kommandos

Mit Projectile kannst du schnell zwischen Dateien wechseln:

```
C-c p f  - Datei im Projekt finden
C-c p p  - Projekt wechseln
C-c p c  - Kompilieren (läuft: uv run pytest)
C-c p u  - App ausführen (läuft: uv run sudoku)
```

## Troubleshooting

### Tests werden nicht gefunden

1. Prüfe ob `pytest.ini` existiert:
   ```bash
   ls -la /home/elyo/.config/elyo/soduku/pytest.ini
   ```

2. Prüfe Python-Path:
   ```elisp
   M-: (getenv "PYTHONPATH")
   ```

3. Stelle sicher, dass du im Projektverzeichnis bist:
   ```bash
   cd /home/elyo/.config/elyo/soduku
   ```

4. Reload `.dir-locals.el`:
   ```
   M-x revert-buffer
   ```
   oder
   ```
   M-x kill-buffer RET  # dann Datei neu öffnen
   ```

### Flycheck findet pyright nicht

```elisp
;; In init.el
(setq flycheck-python-pyright-executable "uv run pyright")
```

### Python-pytest findet uv nicht

Stelle sicher, dass `uv` in deinem PATH ist:
```bash
which uv
```

Falls nicht, füge zu deiner Emacs-Config hinzu:
```elisp
(setenv "PATH" (concat (getenv "PATH") ":/path/to/uv"))
(setq exec-path (append exec-path '("/path/to/uv")))
```

## Nützliche Workflows

### Test-Driven Development

1. Schreibe Test: `tests/unit/domain/test_new_feature.py`
2. Führe Test aus: `C-c C-t f`
3. Test schlägt fehl (erwartetes Verhalten)
4. Implementiere Feature: `src/sudoku/domain/...`
5. Führe Test erneut aus: `C-c C-t r`
6. Iteriere bis Test grün ist

### Refactoring mit Tests

1. Alle Tests ausführen: `C-c C-t p`
2. Sicherstellen alles grün: ✓
3. Refactoring durchführen
4. Tests erneut ausführen: `C-c C-t p`
5. Bei rot: Änderungen rückgängig machen

## Quick Reference

| Kommando | Keybinding | Beschreibung |
|----------|-----------|--------------|
| `python-pytest` | - | Alle Tests |
| `python-pytest-function` | `C-c C-t t` | Test unter Cursor |
| `python-pytest-file` | `C-c C-t f` | Datei-Tests |
| `python-pytest-project` | `C-c C-t p` | Projekt-Tests |
| `python-pytest-repeat` | `C-c C-t r` | Tests wiederholen |
| `flycheck-list-errors` | `C-c ! l` | Fehler auflisten |
| `projectile-test-project` | `C-c p P` | Projekt testen |

Viel Erfolg beim Entwickeln! 🚀
