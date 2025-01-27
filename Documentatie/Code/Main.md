Main is het centrale script. Dit run je om het programma te draaien. Het doorloopt stukje voor stukje alle processen die nodig zijn om de data binnen te halen, de rapporten te genereren, en deze te controleren.

Allereerst wordt gevraagd of men de rapporten die al aanwezig zijn verwijderd moeten worden. Dit zodat de nieuwe rapporten niet met de oude mixen. Dit is niet nodig als rapporten met dezelfde naam worden gegenereerd.

Hierna wordt het Extract Load Transform proces afgetrapt. Dit staat uitvoerig beschreven in de [[ELT|documentatie van ELT.Py]].
Na het aanmaken van de phenotypes, genotypes, en complete dataframes worden deze opgeslagen als xlsx file voor de leesbaarheid.

De "[[NifgoProprietaryChanges|business logic]]" die Nifgo graag ziet wordt hierna toegepast op het complete dataframe, die daarna naar complete.xlsx wordt overschreven.

Aangezien in de data niet altijd gevuld is of bruikbare resultaten geeft wordt deze data vanuit een extern geleverd Excel bestand gecorrigeerd. 