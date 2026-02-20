# Testrapport (TEST_REPORT.md)

Dette dokumentet inneholder testresultater for DIAS Package Creator, inkludert end-to-end testing mot Essarch staging og belastningstester.

## 1. End-to-End Testing mot Essarch Staging

### 1.1. SUPPLEMENT-scenario
- **Testcase:** Opprett og valider en SUPPLEMENT-pakke mot Essarch staging.
- **Input:** Eksisterende AIP-ID, nye metadata-filer.
- **Forventet Output:** Pakken valideres vellykket og aksepteres av Essarch staging som et gyldig supplement.
- **Faktisk Resultat:** [Ikke utført ennå - krever Essarch staging-miljø]
- **Testdata:** `test_data/supplement_test_1`
- **Testtimer:** [TBD]

### 1.2. REPLACEMENT-scenario
- **Testcase:** Opprett og valider en REPLACEMENT-pakke mot Essarch staging.
- **Input:** Eksisterende AIP-ID, oppdaterte datafiler og metadata.
- **Forventet Output:** Pakken valideres vellykket og aksepteres av Essarch staging som en gyldig erstatning.
- **Faktisk Resultat:** [Ikke utført ennå - krever Essarch staging-miljø]
- **Testdata:** `test_data/replacement_test_1`
- **Testtimer:** [TBD]

## 2. Belastningstester (Batch/Ytelse)

### 2.1. 100 Pakker
- **Testcase:** Generer og valider 100 pakker i en batch-jobb.
- **Input:** 100 sett med testdata (filer og metadata).
- **Forventet Output:** Alle 100 pakker genereres og valideres uten feil innen rimelig tid (f.eks. < 5 minutter).
- **Faktisk Resultat:** [Ikke utført ennå]
- **Ytelse:** [TBD]
- **Anbefalt Maskinvare:** [TBD]

### 2.2. 500 Pakker
- **Testcase:** Generer og valider 500 pakker i en batch-jobb.
- **Input:** 500 sett med testdata.
- **Forventet Output:** Alle 500 pakker genereres og valideres uten minnelekkasjer eller krasj.
- **Faktisk Resultat:** [Ikke utført ennå]
- **Ytelse:** [TBD]
- **Anbefalt Maskinvare:** [TBD]

### 2.3. 1000 Pakker
- **Testcase:** Generer og valider 1000 pakker i en batch-jobb.
- **Input:** 1000 sett med testdata.
- **Forventet Output:** Systemet håndterer belastningen stabilt, logger korrekt, og fullfører jobben.
- **Faktisk Resultat:** [Ikke utført ennå]
- **Ytelse:** [TBD]
- **Anbefalt Maskinvare:** [TBD]

## 3. Oppsummering av Testtimer
- **Totalt antall testtimer:** [TBD] (Del av ~150 t totalt estimat)
- **Gjenstående testtimer:** [TBD]
