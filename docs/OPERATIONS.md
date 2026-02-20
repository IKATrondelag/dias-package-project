# Driftsveiledning (OPERATIONS.md)

Dette dokumentet beskriver daglige rutiner, roller og ansvar for drift av DIAS Package Creator.

## 1. Roller og Ansvar
- **Systemansvarlig (System Owner):** Ansvarlig for applikasjonens livssyklus, budsjett og SLA.
- **Driftsansvarlig (Operations Manager):** Ansvarlig for daglig drift, overvåking, oppgraderinger og feilsøking.
- **Brukerstøtte (Support):** Førstelinje for brukerhenvendelser og feilrapportering.
- **Utvikler (Developer):** Ansvarlig for feilretting, nye funksjoner og teknisk dokumentasjon.

## 2. Daglige Rutiner
- **Logg-sjekkliste:**
  - Sjekk loggfilene i `logs/`-mappen for feilmeldinger (`ERROR` eller `CRITICAL`).
  - Verifiser at loggrotasjon fungerer (maks 5 backup-filer, maks 10 MB per fil).
  - Se etter uvanlig høy minnebruk eller ytelsesproblemer i loggene.
- **Diskplass:**
  - Overvåk diskplass på serveren/maskinen der applikasjonen kjører.
  - Sørg for at det er nok plass til genererte pakker og logger.
- **Backup:**
  - Ta daglig backup av konfigurasjonsfiler (`dias_config.yml`).
  - Ta backup av genererte pakker og logger i henhold til organisasjonens retningslinjer.

## 3. Feilsøking og Logginnsamling
Ved feil eller supporthenvendelser, følg disse trinnene:
1. **Identifiser feilen:** Be brukeren om en beskrivelse av feilen, tidspunkt og eventuelle feilmeldinger på skjermen.
2. **Finn korrelasjons-ID:** Be brukeren om korrelasjons-ID-en (hvis tilgjengelig i feilmeldingen) eller finn den i loggen basert på tidspunktet.
3. **Samle logger:**
   - Gå til logg-mappen (standard: `logs/`).
   - Finn loggfilen(e) for det aktuelle tidspunktet.
   - Søk etter korrelasjons-ID-en i loggfilen for å finne alle relaterte logginnslag.
4. **Analyser loggene:** Se etter `ERROR` eller `CRITICAL` meldinger og stack traces.
5. **Eskaler:** Hvis feilen ikke kan løses av support, eskaler til utvikler med loggfiler og beskrivelse.

## 4. Eskaleringstrinn og Kontaktpunkter
- **Nivå 1 (Support):** Førstelinje for brukerhenvendelser. Løser kjente problemer og samler logger.
- **Nivå 2 (Drift):** Håndterer infrastrukturproblemer, oppgraderinger og konfigurasjonsfeil.
- **Nivå 3 (Utvikling):** Håndterer kodefeil, nye funksjoner og komplekse tekniske problemer.

**Kontaktinformasjon:**
- Support: support@example.com
- Drift: drift@example.com
- Utvikling: dev@example.com

## 5. SLA og Ansvarslinje
- **Responstid:** Kritiske feil (system nede) skal påbegynnes innen 2 timer i arbeidstiden.
- **Løsningstid:** Kritiske feil skal løses eller ha en midlertidig løsning (workaround) innen 8 timer.
- **Oppgraderinger:** Planlagte oppgraderinger skal varsles minst 1 uke i forveien og utføres utenfor kjernetid.
- **Ansvar:** Systemansvarlig er ansvarlig for at SLA overholdes.
