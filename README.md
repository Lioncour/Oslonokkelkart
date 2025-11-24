# Oslonøkkelen Timeline Map

Interaktivt tidslinjekart som visualiserer hvor og når ulike Oslonøkkelen-tilbud er tilgjengelige. Dra tidslinjeslideren for å se hvilke steder som er aktive på en gitt dato, og få oversikt over antall steder totalt samt fordeling per kategori.

## Teknologi
- HTML, CSS og JavaScript
- Leaflet.js med OpenStreetMap-fliser
- Ingen rammeverk eller build-steg – hele prosjektet er statisk

## Lokalt oppsett
1. Hold `data.xml` lokalt (den er ignorert av Git).
2. Kjør `python extract_locations.py` for å generere `data.js` med navn, koordinater, dato og kategori.
3. Åpne `index.html` i nettleseren din.

`data.js` inneholder kun felt som trengs for visualiseringen, slik at den kan publiseres uten å eksponere hele XML-modellen.
