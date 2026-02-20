# DIAS Package Creator

Et skrivebordsprogram (Tkinter) for å lage DIAS-pakker (SIP/AIP) med automatisk generering av `info.xml`, `mets.xml` og PREMIS-logg.

## Rask start

```bash
pip install -r requirements.txt
python app.py
```

## Konfigurasjon

1. Kopier `dias_config.example.yml` til `dias_config.yml` for standardverdier i skjema.
2. Kopier eventuelt `.env.example` til `.env` for avansert oppsett.

Mer informasjon: `CONFIG_GUIDE.md`.

## Bygg kjørbar fil

```bash
pip install .[build]
python -m PyInstaller --clean --noconfirm build_exe.spec
```

Output havner i `dist/`.

## Kjør tester

```bash
python -m pytest tests/
```

## Pakkestruktur (kort)

```text
[AIC_UUID]/
  info.xml
  [AIP_UUID]/
    log.xml
    content/[SIP_UUID].tar
```

`[SIP_UUID].tar` inneholder blant annet `mets.xml`, `log.xml`, `administrative_metadata/premis.xml` og innholdsfiler.

## Viktige mapper

- `src/gui/`: GUI
- `src/core/`: arbeidsflyt og pakkeoppretting
- `src/dias_package_creator/`: XML-generatorer og validering
- `tests/`: tester

## Lisens

MIT, se `LICENSE`.