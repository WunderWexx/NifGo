import pandas as pd
import PySimpleGUI as sg
import utilities as util

filepath = sg.popup_get_file("Selecteer bestand",
                                  title= "Invoer bestand", keep_on_top=True) #Voorheen askForFile()
df = pd.read_csv(filepath, sep="@", header=None, engine = "python")

util.printEntire(df)

filepath = sg.popup_get_file("Selecteer bestand",
                                  title= "Invoer bestand", keep_on_top=True) #Voorheen askForFile()
df = pd.read_csv(filepath, sep="@", header=None, engine = "python")

util.printEntire(df)