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
    "G001040549",
    "G001040649",
    "G001040648",
    "G001040551",
    "G001040651",
    "G001040566",
    "G001040604",
    "G001040606",
    "G001040700",
    "G001040654",
    "G001040685",
    "G001040680",
    "G001040658",
    "G001040670",
    "G001040596",
    "G001040595",
    "G001040557",
    "G001040681"
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