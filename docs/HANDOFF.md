# Handoff: CI/CD (kortversjon)

Dette dokumentet er en kort oppsummering ved prosjektavslutning.

## Status for dette dokumentet

- Type: engangsdokument
- Vedlikehold: kun ved vesentlige endringer i drift/ansvar

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
- Tidsavbrudd på jobber satt for å unngå at systemet henger
- CI har minimum test coverage-krav (25%)
- Hele test-suiten må være grønn før release

## Referanse: release-prosess

1. Sørg for grønn CI på siste commit.
2. Oppdater `CHANGELOG.md`.
3. Opprett tag: `vX.Y.Z`.
4. Push tag til GitHub.
5. CI lager release-assets automatisk.
6. (Valgfritt) Kjør `Windows EXE Build` manuelt for ekstra build/upload.

## Når bruke Windows EXE-workflow manuelt

Brukes når:
- noen trenger ny `.exe` uten ny utgivelse
- lokal bygging feiler hos teammedlemmer

Valg ved manuell kjøring:
- `upload_to_release = false`: kun artifact
- `upload_to_release = true` + `release_tag = vX.Y.Z`: last opp til eksisterende release

## Docker-merknad

GitHub-hosted runners kan ikke bygge Windows EXE i Linux Docker-container.
Støttet løsning her er native `windows-latest` runner.

