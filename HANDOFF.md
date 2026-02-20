# Handoff: CI/CD (kortversjon)

Dette dokumentet er en enkel overlevering for drift av workflowene.

## Hva som finnes

- `.github/workflows/ci.yml`
  - Kjøres på push/PR til `main` og `develop`
  - Kjører: lint, security, test, docs
  - Bygg/release skjer kun på tagger `v*`
- `.github/workflows/windows-exe.yml`
  - Valgfri Windows EXE-build
  - Kan kjøres manuelt (workflow_dispatch)
  - Kjøres automatisk ved `release: published`

## Viktige kvalitetsgrep

- Concurrency aktivert (avbryter gamle runs på samme branch/tag)
- Job-timeouts satt for å unngå heng
- CI har minimum coverage-krav (25%)
- Full test-suite må være grønn før release

## Minimal release-prosess

1. Sørg for grønn CI på siste commit.
2. Oppdater `CHANGELOG.md`.
3. Opprett tag: `vX.Y.Z`.
4. Push tag til GitHub.
5. CI lager release-assets automatisk.
6. (Valgfritt) Kjør `Windows EXE Build` manuelt for ekstra build/upload.

## Når bruke Windows EXE-workflow manuelt

Brukes når:
- noen trenger ny `.exe` uten ny kode-release
- lokal bygging feiler hos teammedlemmer

Valg ved manuell kjøring:
- `upload_to_release = false`: kun artifact
- `upload_to_release = true` + `release_tag = vX.Y.Z`: last opp til eksisterende release

## Docker-merknad

GitHub-hosted runners kan ikke bygge Windows EXE i Linux Docker-container.
Støttet løsning her er native `windows-latest` runner.

## Anbefalt dokumentasjonssett (kort og nok)

Behold disse som primære dokumenter:
- `README.md` (bruk, installasjon, lenker)
- `HANDOFF.md` (CI/CD + release)
- `CONFIG_GUIDE.md` (kun config)

Andre filer kan stå, men trenger ikke være obligatoriske i sluttrapporten.
