# A place to store utility functions

# Imports
import time
import pandas as pd
import docx
import docx as dx
from docx.shared import RGBColor,Pt
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import parse_xml
from docx.oxml.ns import qn,nsdecls
from docx.oxml.shared import OxmlElement

def printEntire(dataframe):
    """
    Uses the context related settings to show the entire dataframe.
    """
    with pd.option_context('display.max_rows', None,
                           'display.max_columns', None,
                           'display.precision', 3,
                           ):
        print(dataframe)
        print()

def store_dataframe(dataframe, name):
    filepath = 'Output/Dataframes/' + name + '.xlsx'
    dataframe = dataframe
    try:
        dataframe.to_excel(filepath)
    except:
        print(f"ACCESS PERMISSION ERROR\n{name}.xlsx not saved because the file could not be accessed.\n")
        time.sleep(1)

def common_data(list1, list2):
    result = False
    # traverse in the 1st list
    for x in list1:
        # traverse in the 2nd list
        for y in list2:
            # if one common
            if x == y:
                result = True
                return result
    return

def is_substring_present_in_substring(data_to_search,string_to_find):
    """
    Tells you, by returning True or False, if the string you're looking for has been found,
    instead of the position of the found string.
    :param data_to_search: The larger string to look through, in search of the smaller string.
    :param string_to_find: The smaller string you are trying to find.
    :return: True or False
    """
    if data_to_search.find(string_to_find) >= 0:
        return True
    else:
        return False

def execute_all_methods(instance):
    methods = [method for method in dir(instance) if
               callable(getattr(instance, method)) and not method.startswith("__")]
    methods.sort(key=lambda x: getattr(instance, x).__code__.co_firstlineno)

    for method_name in methods:
        method = getattr(instance, method_name)
        method()