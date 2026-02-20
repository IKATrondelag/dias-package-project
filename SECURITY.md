# Sikkerhetsbeskrivelse (SECURITY.md)

Dette dokumentet beskriver sikkerhetsrutiner, nøkkelhåndtering og tilgangskontroll for DIAS Package Creator.

## 1. Nøkkelhåndtering og Kryptering
- **Signeringsnøkler:**
  - Windows EXE-filer signeres med et gyldig kodesigneringssertifikat.
  - Sertifikatet og den private nøkkelen lagres sikkert i en Hardware Security Module (HSM) eller en sikker KeyVault (f.eks. Azure Key Vault, AWS KMS).
  - Tilgang til signeringsnøkkelen er strengt begrenset til autoriserte CI/CD-pipelines og utvalgte release-ansvarlige.
- **API-nøkler:**
  - API-nøkler for integrasjon mot Essarch eller andre eksterne systemer skal aldri hardkodes i kildekoden eller lagres i klartekst i konfigurasjonsfiler.
  - Bruk miljøvariabler (f.eks. `DIAS_API_KEY`) eller en sikker secret manager for å injisere API-nøkler ved kjøretid.
- **Krypteringspolicy:**
  - Sensitive filer og data i pakkene (f.eks. personopplysninger) bør krypteres før de overføres til Essarch, i henhold til organisasjonens retningslinjer.
  - All kommunikasjon mot eksterne API-er (f.eks. Essarch) skal skje over HTTPS/TLS 1.2+.

## 2. CI/CD Secrets
- **GitHub Actions:**
  - Secrets som brukes i CI/CD-pipelines (f.eks. `GITHUB_TOKEN`, signeringssertifikater, passord) lagres som GitHub Secrets.
  - Secrets eksponeres aldri i bygge-logger.
  - Tilgang til å endre eller lese secrets er begrenset til repository-administratorer.

## 3. Tilgangskontroll
- **Kildekode:**
  - Tilgang til GitHub-repositoriet er styrt via rollebasert tilgangskontroll (RBAC).
  - Kun autoriserte utviklere har skrivetilgang til `main`-branchen.
  - Alle endringer krever pull requests og code review før de merges.
- **Driftsmiljø:**
  - Tilgang til servere og maskiner der applikasjonen kjører, er begrenset til autorisert driftspersonell.
  - Tjenestekontoer brukes for automatisert kjøring, med minimum nødvendige rettigheter (Least Privilege Principle).

## 4. Personvern og Anonymisering
- **Personvernvurdering (DPIA):**
  - En formell vurdering av personopplysninger i pakkene bør utføres av organisasjonens personvernombud (PVO).
  - Applikasjonen i seg selv lagrer ikke personopplysninger, men behandler filer som kan inneholde sensitive data.
- **Anonymiseringsrutiner:**
  - Hvis pakkene inneholder sensitive personopplysninger som ikke skal arkiveres i klartekst, må disse anonymiseres eller pseudonymiseres *før* de mates inn i DIAS Package Creator.
  - Applikasjonen tilbyr for øyeblikket ingen innebygd funksjonalitet for automatisk anonymisering av innhold.
