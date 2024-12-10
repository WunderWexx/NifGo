# Documentation

_This documentation is work in progress, and is now little more than some glorified notes_

## Hoe dingen aangepast moeten worden
De filosofie is dat alle functies los van elkaar staan, en vrijwel zelfvoorzienend zijn. Als er ergens iets niet klopt hoeft daar idealiter maar 1 functie voor gewijzigd te worden.
Dit programma is gemaakt met gemak van onderhoud eerst, en daarna pas snelheid.
### Aanpassen welke genen in welke rapporten gerapporteerd worden
##### Voor Nutrinomics
1. In nutrinomics_IA de nutrinomics_genes list aanpassen zodat er alle genen in staan die in het rapport komen. Met deze lijst wordt de nutri_markers.xlsx file gefilterd.

### Aanpassen op basis van welke SNP's genen worden bepaald
1. nutri_markers.xlsx aanpassen.

### Aanpassen van rapport opmaak en teksten
Alle teksten in de rapporten staan in het .py bestand van het desbetreffende rapport. De code is zoveel mogelijk gebouwd om het rapport te spiegelen.

## To-Do, in order of priority
### For NifGo
- Fix DPYD phenotype ✅
- Names must be added automatically. ✅ 
- Reports also available in PDF format ✅
- Adjust ABCB1 genotype. Use C-T instead of G-A ✅
- Remove `Not_` and `_or_` ✅
- Move CYP2C19 a few lines down ✅
- Move MTHFR1298 one line down ✅
- Update `requirements.txt` ✅
- Add a gene ✅
- Handle missing customer data to avoid errors ✅
- Handle missing birthdates properly ✅
- Ensure complete reports are generated; no partial data allowed ✅
- If data is missing in Nutrinomics, an ERROR should occur instead of an exception ✅
- Finalize diagnostics.py ✅
- Update `Diagnostics.py` for the new array
- `ELT.Transform.genotype_txt.drop_columns_after_last_sample()` needs to work with regex
- Handle missing data in source files.
- Update recognition of columns in `genotype.txt` since the structure is inconsistent.
- Diagnose missing customer data / auto-check customer data.
- Ensure customer data works with headers instead of column indices.

### For Myself
- The version will increase by one full point with the release of this branch.
- Gradually replace all standard input files with code or CSV files.
- Add a UI / Make it possible to choose what parts of the program to execute
- Create a batch file for automatic updates.
- Finalize diagnostics.
- Translate everything into English.
- Provide every report-generating class with an AI assistant.
- Add exceptions for issues like empty cells in `aanpassingen.xlsx`.
- Clean up and split the medication match dictionary (`medicatiematch`) into different dictionaries.

## Changelog
### V2.0.0
Now using the new array!
The info in `Globals.py` was moved to `ELT.py`.
`CheckMissingProbesetID.py` was removes, because it is deprecated with the new array.
dbSNP is no longer reported in the Nutrinomics report.