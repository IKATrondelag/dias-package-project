# Security

Dette dokumentet beskriver kun applikasjonsspesifikke sikkerhetsforhold for DIAS Package Creator.
Organisatoriske krav (tilgangsstyring, nøkkelhåndtering, DPIA, internkontroll, etc.) skal dekkes i institusjonens egne policyer.

## Scope

- Gjelder kodebasen og kjøring av DIAS Package Creator.
- Gjelder ikke overordnede institusjonelle sikkerhetskrav.

## Hva applikasjonen gjør

- Kjører lokalt som skrivebordsapplikasjon.
- Leser filer fra valgt kilde og skriver DIAS-pakke til valgt målmappe.
- Genererer XML-filer (`info.xml`, `mets.xml`, PREMIS/logg) og beregner sjekksum (SHA-256).

## Hva applikasjonen ikke gjør

- Ingen innebygd kryptering av innholdsfiler.
- Ingen automatisk anonymisering eller pseudonymisering.
- Ingen hemmelighetshåndtering/secret manager i runtime.

## Sikker bruk

- Ikke legg hemmeligheter i kode, templates eller konfigurasjonsfiler.
- Vurder innhold før pakking: filer kan inneholde personopplysninger eller annen sensitiv informasjon.
- Kjør applikasjonen med minst mulige rettigheter og skriv til kontrollerte målmapper.
- Verifiser output ved behov med tilgjengelige valideringsrutiner/tester.

## Rapportering av sårbarheter

- Ikke opprett offentlig issue for aktive sårbarheter.
- Meld fra privat til prosjektansvarlig/repository-maintainer med:
  - beskrivelse av problem
  - hvordan det kan reproduseres
  - påvirket versjon/plattform
  - forslag til avbøtende tiltak (hvis tilgjengelig)
