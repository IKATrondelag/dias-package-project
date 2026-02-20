# Installasjonsveiledning (INSTALL.md)

Dette dokumentet beskriver hvordan DIAS Package Creator installeres og konfigureres for drift.

## 1. Systemkrav
- **Operativsystem:** Windows 10 / Windows 11 / Windows Server 2019+ (64-bit)
- **Minne (RAM):** Minimum 4 GB (8 GB anbefalt for store batch-jobber)
- **Diskplass:** Minimum 500 MB for applikasjonen, pluss tilstrekkelig plass for genererte pakker og logger.
- **Nettverk:** Tilgang til Essarch API (hvis integrasjon er aktivert).

## 2. Avhengigheter
- Ingen eksterne avhengigheter kreves for den kompilerte EXE-filen (alt er inkludert).
- For kildekode-kjøring kreves Python 3.11+ og pakkene i `requirements.txt`.

## 3. Tjenestekonto-oppsett
Hvis applikasjonen skal kjøres som en tjeneste eller automatisert batch-jobb:
1. Opprett en dedikert tjenestekonto (f.eks. `svc_dias_creator`).
2. Gi kontoen lese- og skrivetilgang til:
   - Mappen der applikasjonen er installert.
   - Mappen for input-data.
   - Mappen for output-pakker.
   - Logg-mappen.
3. Kontoen trenger *ikke* administratorrettigheter.

## 4. Installasjon (Steg-for-steg)
1. Last ned siste release (`dias-package-creator-windows-amd64.zip`) fra GitHub Releases.
2. Verifiser SHA256-sjekksummen:
   ```powershell
   Get-FileHash dias-package-creator-windows-amd64.zip -Algorithm SHA256
   ```
   Sammenlign med innholdet i `.sha256`-filen.
3. Pakk ut ZIP-filen til ønsket installasjonskatalog (f.eks. `C:\DIAS\PackageCreator`).
4. Kopier `dias_config.example.yml` til `dias_config.yml` og tilpass konfigurasjonen (se `CONFIG_GUIDE.md`).
5. Sett nødvendige miljøvariabler (se seksjon 5).

## 5. Miljøvariabler
Følgende miljøvariabler kan settes for å overstyre konfigurasjonsfilen:
- `DIAS_ENV`: Miljø (f.eks. `production`, `staging`, `development`).
- `DIAS_LOG_LEVEL`: Loggnivå (f.eks. `INFO`, `DEBUG`).
- `DIAS_API_KEY`: API-nøkkel for Essarch-integrasjon (bør settes via sikker vault/secret manager).

## 6. Verifiseringstester
Etter installasjon, kjør en test for å verifisere at alt fungerer:
1. Åpne applikasjonen (`dias-package-creator.exe`).
2. Gå til "Validering"-fanen og velg en test-pakke.
3. Verifiser at valideringen fullføres uten feil.
4. Sjekk loggfilen i logg-mappen for å bekrefte at oppstart og validering ble logget korrekt.

## 7. Oppgradering og Rollback
**Oppgradering:**
1. Ta backup av `dias_config.yml` og eventuelle andre lokale tilpasninger.
2. Last ned og pakk ut den nye versjonen over den gamle (eller i en ny mappe).
3. Verifiser at konfigurasjonsformatet ikke har endret seg (sjekk `../CHANGELOG.md`).
4. Start applikasjonen og kjør verifiseringstester.

**Rollback:**
1. Slett den nye versjonen.
2. Gjenopprett forrige versjon fra backup eller last ned forrige release fra GitHub.
3. Gjenopprett `dias_config.yml` fra backup.
4. Start applikasjonen og verifiser.
