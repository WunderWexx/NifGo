import pandas as pd
import PySimpleGUI as sg
import Utilities
import time
from os import listdir, rename
from os.path import isfile, join
import subprocess
from time import sleep
import re

"""
Een script om uit een grote groep rapporten een enkele batch the filteren gebaseer op klantdata.
1. Klantgegevens worden geïmporteerd
2. Alle samplecodes voor die batch worden bepaald
3. De opslag van rapporten en pdf's worden bepaald
4. De opslag voor de gefilterde batch wordt bepaald
5. De rapporten met de juist samplecodes in de naam worden naar de nieuwe opslag verplaatst
"""

lijst_van_samples = [
    "D402000396",
    "BFX0034308",
    "BFX0034496",
    "BFX0034451",
    "BFX0034467",
    "BFX0034455",
    "BFX0034457",
    "BFX0034469",
    "BFX0034478",
    "BFX0034482",
    "BFX0034465",
    "BFX0034491",
    "BFX0034494",
    "BFX0034461",
    "BFX0034470",
    "BFX0034473",
    "BFX0034495",
    "BFX0034458",
    "BFX0034472",
    "BFX0034025",
    "G001040535",
    "G001040506",
    "G001040550",
    "G001040519"
]

word_opslag = sg.popup_get_folder(f"Selecteer de map met Word bestanden",
                             title="File selection", keep_on_top=True)

pdf_opslag = sg.popup_get_folder(f"Selecteer de map met PDF bestanden",
                             title="File selection", keep_on_top=True)

nieuwe_opslag = sg.popup_get_folder(f"Selecteer de map waar de gefilterde batch wordt opgeslagen",
                             title="File selection", keep_on_top=True)

def rapporten_overzetten(opslag, lijst_van_samples):
    rapporten = [file for file in listdir(opslag) if isfile(join(opslag, file)) and not file.startswith('~$')]
    for rapport in rapporten:
        if any(identifier in rapport for identifier in lijst_van_samples):
            rename(opslag+'/'+rapport, nieuwe_opslag+'/'+rapport)

rapporten_overzetten(word_opslag, lijst_van_samples)
rapporten_overzetten(pdf_opslag, lijst_van_samples)