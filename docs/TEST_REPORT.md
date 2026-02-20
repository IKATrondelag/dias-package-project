# Testrapport og overlevering

Dette dokumentet beskriver testnivå for applikasjonen.
## 1. Formaal

- Bekrefte at applikasjonen fungerer stabilt ved ordinert bruk.
- Gi neste forvalter et praktisk utgangspunkt for videre drift og utvikling.

## 2. Dekning i dagens testsuite (faktisk)

Foelgende er verifisert i automatiske tester i `tests/`:

- Validering av input, metadata, stier og diskplass (`test_validation.py`, `test_dias_controller.py`).
- XML-generering for `info.xml`, `mets.xml` og PREMIS/logg (`test_dias_creator.py`, `test_premis.py`).
- PREMIS-hendelser/agenter, inkludert SIP/AIP-filtrering (`test_premis.py`, `test_dias_controller.py`).
- Filkopiering og SHA-256-sjekksummer i controller/file-processing (`test_dias_controller.py`, `test_dias_creator.py`).
- Bakgrunnsjobber, progresjon og avbrudd i job manager (`test_job_manager.py`).
- Grunnleggende pakkestruktur-validering i validator (`test_package_validator.py`).
- Konfigurasjonslasting fra YAML (`test_config_loader.py`).
- Opprettelse av pakke-kvittering etter vellykket pakking (`test_dias_controller.py`).

## 3. Hva som er normalt for tilsvarende applikasjoner

- Hovedvekt på enhetstester og integrasjonstester i kodebasen.
- Begrenset antall manuelle GUI-scenarier som release-gate.
- Ytelsestester gjennomfores ved behov, ikke ved hver release.
- Eksterne miljø-tester (f.eks. staging hos tredjepart) planlegges separat og eies av drift/forvaltning.

## 4. Status ved avslutning

- Siste lokale testkjoring: `python -m pytest .\tests\`
- Resultat: bestatt (exit code `0`).
- Ingen kjente blokkerende feil fra automatiske tester i avsluttende leveranse.

## 5. Ikke dekket av testsuiten (taes ikke som verifisert)

- Manuell GUI ende-til-ende test er ikke dekket av automatiske tester.
- Full ende-til-ende verifisering mot eksternt stagingmiljø er ikke dekket.
- Storskala belastningstester/ytelsesgrenser er ikke gjennomført.

## 6. Kort forslag til videre arbeid

- Etabler 1-2 manuelle release-sjekker for GUI-flyt (kilde -> metadata -> ferdig pakke).
- Legg til en lett integrasjonstest som verifiserer forventede output-filer etter `_create_package_task`.
- Avklar om staging-test mot eksternt arkivmiljø skal være et release-krav.
- Definer en enkel ytelsesbaseline (f.eks. representative datamaengder) dersom dette er viktig for drift.

## 7. Driftsoverlevering til ny forvalter

Ny ansvarlig bør minimum kjenne til:

- Oppstart: `python app.py`
- Test: `python -m pytest .\tests\`
- Bygg: `python -m PyInstaller --clean --noconfirm build_exe.spec`
- Konfigurasjon:
	- `dias_config.yml` (defaults for metadata/PREMIS)
	- `.env` (miljøspesifikke innstillinger)

Relevante dokumenter:

- `README.md`
- `CONFIG_GUIDE.md`
- `SECURITY.md`
- `CHANGELOG.md`
