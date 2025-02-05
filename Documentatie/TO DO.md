### Voor NifGo  
- Update `Diagnostics.py` for the new array
	- Fenotype moet juiste vorm hebben
	- Genotype moet juiste vorm hebben
	- Missende genen moet bepaald worden. Dynamisch uit laatste template voor alle soorten rapporten
	- Zijn voor alle rapporten klantgegevens aanwezig?
	- Hoeveel rapporten zijn er gegenereerd, en hoeveel batches is dat?
	- Tijd die aspecten dingen kosten
- Ontbrekende klantgegevens diagnosticeren / klantgegevens automatisch controleren. Inline. 
- Automatische manier om geslacht te checken.
- `ELT.Transform.genotype_txt.drop_columns_after_last_sample()` needs to work with regex  
- Update recognition of columns in `genotype.txt` since the structure is inconsistent.  
- Ensure customer data works with headers instead of column indices.  
### Voor mezelf  
- Inladen van data optimaliseren.  
- Regex error verwijderen.
- Een UI toevoegen / Het mogelijk maken om te kiezen welke delen van het programma worden uitgevoerd.  
- Code optimaliseren  