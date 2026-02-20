# Lokaliseringsguide

## Oversikt

DIAS Package Creator GUI støtter lokalisering/oversettelse gjennom et sentralt etikett-system. All brukerrettet tekst er lagret i én fil, noe som gjør det enkelt å oversette applikasjonen til forskjellige språk.

## Etiketthåndtering

### Plassering
Alle UI-etiketter er definert i:
- `src/gui/labels.py`

### Struktur
Etiketter er organisert som klassekonstanter i `Labels`-klassen:

```python
class Labels:
    """UI-etiketter og tekstkonstanter."""
    
    # Applikasjon
    APP_NAME = "DIAS Package Creator"
    
    # Menyelementer
    MENU_FILE = "File"
    MENU_NEW_PACKAGE = "New Package"
    # ... osv
```

### Bruk i koden
Importer og bruk etiketter i GUI-koden din:

```python
from .labels import labels

# Bruk etiketten
ttk.Label(frame, text=labels.LABEL_SOURCE)
ttk.Button(frame, text=labels.BTN_BROWSE, command=self._browse)
```

## Lage en oversettelse

For å oversette applikasjonen til et annet språk:

1. Kopier `src/gui/labels.py` til en ny fil (f.eks. `labels_nb.py` for norsk)
2. Oversett alle strengverdiene, men behold konstantnavnene uendret
3. Importer riktig etikettfil basert på brukerens preferanse eller systemets locale

### Eksempel på norsk oversettelse

```python
class Labels:
    """UI-etiketter og tekstkonstanter."""
    
    # Applikasjon
    APP_NAME = "DIAS Pakkeskaper"
    
    # Menyelementer
    MENU_FILE = "Fil"
    MENU_NEW_PACKAGE = "Ny pakke"
    MENU_LOAD_TEMPLATE = "Last inn metadata-mal"
    MENU_SAVE_TEMPLATE = "Lagre metadata-mal"
    MENU_EXIT = "Avslutt"
    
    # Kildevelger
    LABEL_SOURCE = "Kilde:"
    BTN_BROWSE = "Bla gjennom"
    BTN_FILE = "Fil"
    BTN_FOLDER = "Mappe"
    # ... osv
```

## Legge til nye etiketter

Når du legger til nye UI-elementer:

1. Legg til konstanten i `Labels`-klassen i `labels.py`
2. Bruk et beskrivende, store bokstaver-navn med prefix:
   - `LABEL_` for feltetiketter
   - `BTN_` for knapper
   - `MENU_` for menyvalg
   - `HEADING_` for seksjonstitler
   - `SECTION_` for skjemaavsnitt
   - `DIALOG_` for dialogtitler
   - `VALIDATION_` for valideringsmeldinger
3. Bruk etiketten i koden via `labels.YOUR_CONSTANT`

## Fordeler

- **Sentralisert styring**: All tekst er på ett sted
- **Enkel oversettelse**: Oversett én gang, brukes overalt
- **Konsistens**: Samme begreper brukes i hele applikasjonen
- **Vedlikeholdbarhet**: Oppdater etiketter uten å endre UI-kode
- **Versjonskontroll**: Spor endringer i etiketter separat fra logikk
