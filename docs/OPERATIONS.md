# Driftsveiledning (OPERATIONS.md)

Dette dokumentet dekker kun drift av applikasjonen DIAS Package Creator.
Organisatoriske policyer (roller, SLA, bemanning, eskaleringsmatrise) skal ligge i institusjonens egne styringsdokumenter.

## 1. Scope

- Oppstart, konfigurasjon, logging, feilsøking og bygg/release av applikasjonen.
- Gjelder lokal kjøring og CI-baserte builds i dette repoet.

## 2. Grunnleggende drift

- Start applikasjon: `python app.py`
- Kjør tester: `python -m pytest .\tests\`
- Bygg executable: `python -m PyInstaller --clean --noconfirm build_exe.spec`

Anbefalt før release:

- Grønn testsuite.
- Oppdatert `CHANGELOG.md`.
- Verifisering av bygget artifact (`dist/`).

## 3. Konfigurasjon og filer

- Standardverdier: `dias_config.yml` (kopieres typisk fra `dias_config.example.yml`).
- Miljøinnstillinger: `.env` (valgfritt, basert på `.env.example`).
- XSD-filer som brukes av appen ligger i prosjektroten.

## 4. Logging og feilsøking

Ved feil:

1. Noter tidspunkt, handling og feilmelding fra bruker.
2. Finn relevante logger i applikasjonens loggområde.
3. Se etter `ERROR`/`CRITICAL` og tilhørende stack trace.
4. Reproduser med samme input om mulig.
5. Kjør tester for å bekrefte om feilen er generell eller miljøspesifikk.

Praktisk minimum for feilrapport:

- Kort beskrivelse av problem.
- Trinn for reproduksjon.
- Plattform/versjon.
- Relevant loggutdrag.

## 5. Backup og datahåndtering

- Backupbehov for genererte pakker, logger og konfigurasjon avgjøres av driftsmiljøet.
- Dette dokumentet definerer ikke institusjonelle krav til oppbevaringstid eller frekvens.

## 6. CI/CD og release-artifacts

- CI-workflow: `.github/workflows/ci.yml`
- Windows EXE-workflow: `.github/workflows/windows-exe.yml`
- `docs/HANDOFF.md` skal ikke inkluderes i release-artifacts.

## 7. Relaterte dokumenter

- `README.md`
- `SECURITY.md`
- `docs/TEST_REPORT.md`
- `docs/HANDOFF.md`
