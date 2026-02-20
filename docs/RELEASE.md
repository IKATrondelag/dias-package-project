# Release-prosess (RELEASE.md)

Dette dokumentet beskriver prosessen for å bygge, signere og publisere nye versjoner av DIAS Package Creator.

## 1. Semantisk Versjonering (SemVer)
Prosjektet følger [Semantisk Versjonering 2.0.0](https://semver.org/):
- **MAJOR (X.y.z):** Inkompatible API-endringer eller store nye funksjoner.
- **MINOR (x.Y.z):** Bakoverkompatible nye funksjoner.
- **PATCH (x.y.Z):** Bakoverkompatible feilrettinger.

## 2. Release-workflow (Tag → Build → Sign → Publish)
Når en ny versjon skal utgis, følges denne prosessen:

1. **Oppdater CHANGELOG.md:**
   - Legg til en ny seksjon for den kommende versjonen med dato og en oppsummering av endringene (Features, Bug Fixes, etc.).
2. **Opprett en Git Tag:**
   - Tagg commiten på `main`-branchen med versjonsnummeret (f.eks. `v1.2.3`).
   - Push taggen til GitHub: `git push origin v1.2.3`.
3. **GitHub Actions (Build & Sign):**
   - Når en ny tag pushes, trigges automatisk workflowen `Windows EXE Build` (`.github/workflows/windows-exe.yml`).
   - Workflowen bygger EXE-filen ved hjelp av PyInstaller.
   - *(Fremtidig steg: Workflowen signerer EXE-filen med et kodesigneringssertifikat lagret i GitHub Secrets).*
   - Workflowen genererer en SHA256-sjekksum for ZIP-filen.
4. **Publisering (Publish):**
   - Workflowen oppretter automatisk en GitHub Release basert på taggen.
   - Følgende filer lastes opp som release-assets:
     - `dias-package-creator-windows-amd64.zip` (Kompilert applikasjon)
     - `dias-package-creator-windows-amd64.zip.sha256` (Sjekksum for verifisering)
     - `HANDOFF.md` (Overleveringsdokumentasjon)

## 3. Ansvar
- **Release Manager:** Ansvarlig for å oppdatere `CHANGELOG.md`, opprette taggen og verifisere at GitHub Actions fullfører vellykket.
- **System Owner:** Ansvarlig for å godkjenne innholdet i releasen (spesielt MAJOR-oppdateringer).
- **Utviklingsteam:** Ansvarlig for at koden er testet og klar for release før taggen opprettes.

## 4. Manuell Release (Fallback)
Hvis automatisk publisering feiler, kan en release trigges manuelt via GitHub Actions-grensesnittet:
1. Gå til "Actions" -> "Windows EXE Build".
2. Klikk "Run workflow".
3. Velg `main`-branchen.
4. Kryss av for "Upload EXE zip to an existing GitHub Release".
5. Skriv inn tag-navnet (f.eks. `v1.2.3`).
6. Klikk "Run workflow".
