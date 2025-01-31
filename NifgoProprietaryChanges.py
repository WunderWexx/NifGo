# All the changes NifGo wants made to the standard ThermoFisher output.

# You might try using a loop for PhenotypeChanges instead of applying each change. See what's faster.

import numpy as np
import Utilities as util
from ELT import Extract
import re

class GeneralChanges:
    def __init__(self, dataframe):
        self.dataframe = dataframe

    def pick_first_result(self):
        """
        Goes through the phenotype and genotype columns and picks the first result in a cell if there are multiple.
        """
        columns = ['phenotype','genotype']
        for column in columns:
            self.dataframe[column] = self.dataframe[column].apply(lambda x: x.split(',')[0] if isinstance(x, str) else x)
            self.dataframe[column] = self.dataframe[column].apply(lambda x: x.split('_or_')[0] if isinstance(x, str) else x)


class GeneNameChanges:
    def __init__(self, dataframe):
        self.dataframe = dataframe

    def MTHFR677(self):
        mask = self.dataframe['gene'] == 'MTHFRC677T'
        self.dataframe.loc[mask, 'gene'] = np.where(True, 'MTHFR677', 'ERROR')

    def MTHFR1298(self):
        mask = self.dataframe['gene'] == 'MTHFRA1298C'
        self.dataframe.loc[mask, 'gene'] = np.where(True, 'MTHFR1298', 'ERROR')


class PhenotypeChanges:
    def __init__(self, dataframe):
        self.dataframe = dataframe

    def change_EM_phenotypes_to_NM(self):
        """
        Exactly what it says on the tin. All phenotypes 'EM' and those containing 'Not_' are changed to 'NM'.
        :return: Changes the aforementioned values to EM in the dataframe.
        """
        function = lambda row: 'NM' if row == 'EM' else row
        self.dataframe['phenotype'] = self.dataframe['phenotype'].apply(function)

    def CACNA1S(self):
        """
        if the genotype is WT/WT then the phenotype shall become NF, otherwise it will become DF. This has the effect
        that everything without two WT alleles has a decreased function.
        """
        mask = self.dataframe['gene'] == 'CACNA1S'
        self.dataframe.loc[mask, 'phenotype'] = np.where(self.dataframe.loc[mask, 'genotype'] == 'WT/WT',
                                                         'NF', # If indeed WT/WT
                                                         'DF') # If not WT/WT

    def G6DP(self):
        """
        The Indeterminate phenotype is changed to NM.
        """
        mask = self.dataframe['gene'] == 'G6PD'
        no_change = self.dataframe.loc[mask, 'phenotype']
        self.dataframe.loc[mask, 'phenotype'] = np.where(
            self.dataframe.loc[mask, 'phenotype'].isin(['Indeterminate', 'Normal']),
            'NM',
            no_change)

    def CYP1A2(self):
        """
        Doesn't seem to have been carried out in the previous program. Changes basically everything to IM because
        normal/normal does not fit the notation standard of CYP1A2.
        :return:
        """
        mask = self.dataframe['gene'] == 'CYP1A2'
        self.dataframe.loc[mask, 'phenotype'] = np.where(self.dataframe.loc[mask, 'genotype'] == 'normal/normal',
                                                         'NM',
                                                         'IM')

    def CYP2C19(self):
        """
        Changes phenotype to NM if genotype *1/*17
        """
        mask = self.dataframe['gene'] == 'CYP2C19'
        no_change = self.dataframe.loc[mask, 'phenotype']
        self.dataframe.loc[mask, 'phenotype'] = np.where(self.dataframe.loc[mask, 'genotype'] == '*1/*17',
                                                         'NM',
                                                         no_change)

    def CYP3A4(self):
        mask = self.dataframe['gene'] == 'CYP3A4'
        condition = [
            (self.dataframe.loc[mask, 'genotype'] == "*1/*22") | (self.dataframe.loc[mask,'genotype'] == "*3/*22"),
            (self.dataframe.loc[mask,'genotype'] == "*22/*22")
        ]
        no_change = self.dataframe.loc[mask, 'phenotype']
        self.dataframe.loc[mask, 'phenotype'] = np.where(condition[0], 'IM',
                                                np.where(condition[1],'PM', no_change))

    def IFNL3(self):
        mask = self.dataframe['gene'] == 'IFNL3'
        condition = [
            (self.dataframe.loc[mask, 'genotype'] == "rs12979860C/rs12979860C"),
            (self.dataframe.loc[mask, 'genotype'] == "rs12979860T/rs12979860T"),
        ]
        self.dataframe.loc[mask, 'phenotype'] = np.where(condition[0], 'NM',
                                                np.where(condition[1], 'PM', 'IM'))

    def CYP2B6(self):
        mask = self.dataframe['gene'] == 'CYP2B6'
        condition = [
            self.dataframe.loc[mask, 'genotype'].isin(["*1/*5", "*5/*5", "*4/*13"]),
            self.dataframe.loc[mask, 'genotype'] == '*1/*22'
            ]
        no_change = self.dataframe.loc[mask, 'phenotype']
        self.dataframe.loc[mask, 'phenotype'] = np.where(condition[0],'NM',
                                                np.where(condition[1], 'RM', no_change))

    def GSTP1(self):
        mask = self.dataframe['gene'] == 'GSTP1'
        condition = self.dataframe.loc[mask, 'genotype'].isin(['*A/*C', '*A/*B'])
        no_change = self.dataframe.loc[mask, 'phenotype']
        self.dataframe.loc[mask, 'phenotype'] = np.where(condition, 'IM', no_change)

    def CYP2C8(self):
        mask = self.dataframe['gene'] == 'CYP2C8'
        condition = [
            self.dataframe.loc[mask, 'genotype'].isin(['*1A/*4+1C', '*1B/*3', '*1A/*3']),
            self.dataframe.loc[mask, 'genotype'] == '*3/*3',
            self.dataframe.loc[mask, 'genotype'] == 'unknown',
            self.dataframe.loc[mask, 'genotype'].str.count('\*3') == 1
        ]
        no_change = self.dataframe.loc[mask, 'phenotype']
        self.dataframe.loc[mask, 'phenotype'] = np.where(condition[0], 'IM',
                                                np.where(condition[1], 'PM',
                                                np.where(condition[2], 'IM',
                                                np.where(condition[3], 'IM',
                                                no_change))))

    def CYP2C9(self):
        mask = self.dataframe['gene'] == 'CYP12C9'
        no_change = self.dataframe.loc[mask, 'phenotype']
        self.dataframe.loc[mask, 'phenotype'] = np.where(self.dataframe.loc[mask, 'genotype'] == '*1/*50',
                                                         'NM', no_change)

    def TPMT(self):
        mask = self.dataframe['gene'] == 'TPMT'
        no_change = self.dataframe.loc[mask, 'phenotype']
        self.dataframe.loc[mask, 'phenotype'] = np.where(
            self.dataframe.loc[mask, 'genotype'].str.contains(r'(?:\*1[A-Z]?)/(\*3[A-Z]?)',
                                                              regex=True),
            'IM',
            no_change
        )

    def CFTR(self):
        mask = self.dataframe['gene'] == 'CFTR'
        no_change = self.dataframe.loc[mask, 'phenotype']
        self.dataframe.loc[mask, 'phenotype'] = np.where(self.dataframe.loc[mask, 'genotype'] == 'F508delCTT/WT',
                                                         'NF', no_change)

    def CYP3A5(self):
        CYP3A5_dict = {
            "PM": "non-expresser",
            "IM": "intermediate-expresser",
            "NM": "homozygoot"
        }
        mask = self.dataframe['gene'] == 'CYP3A5'
        condition = self.dataframe.loc[mask, 'phenotype'].isin(CYP3A5_dict.keys())  # This is also a mask
        if_true = self.dataframe.loc[mask, 'phenotype'].map(CYP3A5_dict)
        self.dataframe.loc[mask, 'phenotype'] = np.where(condition, if_true, 'ERROR')


class GenotypeChanges:
    def __init__(self, dataframe):
        self.dataframe = dataframe

    def ABCB1(self):
        ABCB1_dict = {
            "A/A": "T/T",
            "G/G": "C/C",
            "A/G": "T/C",
            "G/A": "T/C"
        }
        mask = self.dataframe['gene'] == 'ABCB1'
        condition = self.dataframe.loc[mask, 'genotype'].isin(ABCB1_dict.keys())
        if_true = self.dataframe.loc[mask, 'genotype'].map(ABCB1_dict)
        self.dataframe.loc[mask, 'genotype'] = np.where(condition, if_true, 'ERROR')

    def ABCG2(self):
        ABCG2_dict = {
            "rs2231142G/rs2231142G": "G/G",
            "rs2231142G/rs2231142T": "G/T",
            "rs2231142T/rs2231142T": "T/T",
        }
        mask = self.dataframe['gene'] == 'ABCG2'
        condition = self.dataframe.loc[mask, 'genotype'].isin(ABCG2_dict.keys())
        if_true = self.dataframe.loc[mask, 'genotype'].map(ABCG2_dict)
        self.dataframe.loc[mask, 'genotype'] = np.where(condition, if_true, 'ERROR')

    def COMT(self):
        """
        Changes the phenotype based on the dict below.
        If no valid combination is found, the phenotype is unknown and will be manually altered in the report.
        """
        COMT_dict = {
            'NM': 'Val/Val',
            'IM': 'Val/Met',
            'PM': 'Met/Met'
        }
        mask = self.dataframe['gene'] == 'COMT'
        condition = self.dataframe.loc[mask, 'phenotype'].isin(COMT_dict.keys())  # This is also a mask
        if_true = self.dataframe.loc[mask, 'phenotype'].map(COMT_dict)
        self.dataframe.loc[mask, 'genotype'] = np.where(condition, if_true, 'ERROR')


    def IFNL3(self):
        mask = self.dataframe['gene'] == 'IFNL3'
        condition = [
            (self.dataframe.loc[mask, 'phenotype'] == "NM"),
            (self.dataframe.loc[mask, 'phenotype'] == "PM"),
        ]
        self.dataframe.loc[mask, 'genotype'] = np.where(condition[0], 'WT/WT',
                                                         np.where(condition[1], 'MT/MT', 'WT/MT'))

    def VKORC1(self):
        VKORC1_dict = {
            'NM': '1639GG',
            'IM': '1639AG',
            'PM': '1639AA'
        }
        mask = self.dataframe['gene'] == 'VKORC1'
        condition = self.dataframe.loc[mask, 'phenotype'].isin(VKORC1_dict.keys()) #This is also a mask
        if_true = self.dataframe.loc[mask,'phenotype'].map(VKORC1_dict)
        self.dataframe.loc[mask,'genotype'] = np.where(condition, if_true, 'ERROR')

    def SLCO1B1(self):
        SLCO1B1_dict = {
            "NF": "521TT",
            "PF": "521CC",
            "DF": "521TC"
        }
        mask = self.dataframe['gene'] == 'SLCO1B1'
        condition = self.dataframe.loc[mask, 'phenotype'].isin(SLCO1B1_dict.keys())  # This is also a mask
        if_true = self.dataframe.loc[mask, 'phenotype'].map(SLCO1B1_dict)
        self.dataframe.loc[mask, 'genotype'] = np.where(condition, if_true, 'ERROR')

    def CYP2C9(self):
        mask = self.dataframe['gene'] == 'CYP12C9'
        no_change = self.dataframe.loc[mask, 'genotype']
        self.dataframe.loc[mask, 'genotype'] = np.where(self.dataframe.loc[mask, 'phenotype'] == 'NM',
                                                         '*1/*1', no_change)

    def CFTR(self):
        mask = self.dataframe['gene'] == 'CFTR'
        no_change = self.dataframe.loc[mask, 'genotype']
        self.dataframe.loc[mask, 'genotype'] = np.where(self.dataframe.loc[mask, 'phenotype'] == 'NF',
                                                         'WT/WT', no_change)

    def UGT1A1(self):
        def take_first_stars(known_call):
            x = known_call
            y = x.split("/")
            first_part = y[0].split("+")[0]
            second_part = y[1].split("+")[0]
            new_known_call = first_part + "/" + second_part
            return new_known_call

        mask = self.dataframe['gene'] == 'UGT1A1'
        find_plus = lambda x: util.is_substring_present_in_string(x, '+')
        condition = self.dataframe.loc[mask, 'genotype'].map(find_plus)
        no_change = self.dataframe.loc[mask, 'genotype']
        self.dataframe.loc[mask, 'genotype'] = np.where(condition,
                                                         self.dataframe.loc[mask, 'genotype'].apply(take_first_stars),
                                                         no_change)

    def MTHFR677(self):
        MTHFR677_dict = {
            "A/A": "T/T",
            "G/G": "C/C",
            "A/G": "T/C",
            "G/A": "T/C"
        }
        mask = self.dataframe['gene'] == 'MTHFR677'
        condition = self.dataframe.loc[mask, 'genotype'].isin(MTHFR677_dict.keys())
        if_true = self.dataframe.loc[mask, 'genotype'].map(MTHFR677_dict)
        self.dataframe.loc[mask, 'genotype'] = np.where(condition, if_true, 'ERROR')

    def MTHFR1298(self):
        MTHFR1298_dict = {
            "T/T": "A/A",
            "G/G": "C/C",
            "T/G": "A/C",
            "G/T": "A/C"
        }
        mask = self.dataframe['gene'] == 'MTHFR1298'
        condition = self.dataframe.loc[mask, 'genotype'].isin(MTHFR1298_dict.keys())
        if_true = self.dataframe.loc[mask, 'genotype'].map(MTHFR1298_dict)
        self.dataframe.loc[mask, 'genotype'] = np.where(condition, if_true, 'ERROR')

    def RYR1(self):
        RYR1_dict = {
            r"^(?!WT/).+/WT$": "MT/WT",
            r"^(?!WT/).+/(?!WT).+$": "MT/MT",
            r"^WT/WT$": "WT/WT"
        }

        mask = self.dataframe['gene'] == 'RYR1'

        def classify_genotype(genotype):
            for pattern, replacement in RYR1_dict.items():
                if re.match(pattern, genotype):  # Check if genotype matches any pattern
                    return replacement
            return "ERROR"  # Default if no pattern matches

        self.dataframe.loc[mask, 'genotype'] = self.dataframe.loc[mask, 'genotype'].apply(classify_genotype)


class CombinedChanges:
    def __init__(self, dataframe):
        self.dataframe = dataframe

    def DPYD_genotype(self):
        def DPYD_get_activity(known_call):
            # *13 = c.1679T>G
            #'c.1129-5923C>G', 'c.1905+1G>A', 'c.1129-5923C>G', 'c.295_298delTCAT'
            allel_list = known_call.split("/")
            allel1 = allel_list[0]
            if allel1 == '':
                return 'ERROR' #If DPYD is unknown, and thus the known_call is empty, an ERROR will be inserted into the dataframe to denote an unknown
            allel2 = allel_list[1]
            actLvl = None
            #Eurofins test onder andere de variaties c.1679T>G, c.1236G>A en c.2846A>T.
            # Als deze 3 variaties niet zijn gevonden dan aangeven in de rapportage activiteitsscore 2
            if not util.common_data(allel_list, ['c.1679T>G', "c.1236G>A", "c.2846A>T"]):
                actLvl = 2

            # Als bij 1 allel een van de variaties c.2846A>T of c.1236G>A worden gevonden dan aangeven
            # in de rapportage activiteitsscore 1,5.
            variaties = ["c.2846A>T", "c.1236G>A"]
            if (
                (allel1 in variaties and allel2 not in variaties)
                or (allel2 in variaties and allel1 not in variaties)
            ):
                actLvl = 1.5

            # Als bij 1 allel de variatie *13 wordt gevonden dan aangeven in de rapportage activiteitsscore 1
            if ('c.1679T>G' in allel_list) and (allel1 != allel2):
                actLvl = 1

            # Bij uitslagen 1236GA/2846AT, 1236GA/*13 en 2846AT/*13 de activiteitsscore 0,5
            if (
                ("c.2846A>T" and "c.1236G>A" in allel_list)
                or (actLvl == 1 and util.common_data(allel_list, ["c.2846A>T", "c.1236G>A"]))
            ):
                actLvl = 0.5

            # Bij de uitslag *13/*13 aangeven in de rapportage de activiteitsscore 0
            if (allel1 == allel2) and allel1 == 'c.1679T>G':
                actLvl = 0

            if actLvl == None:
                raise Exception(f"No activity level determined for DYPD {known_call}")
            else:
                return f'AS: {actLvl}'

        mask = self.dataframe['gene'] == 'DPYD'
        no_change = self.dataframe.loc[mask, 'genotype']
        self.dataframe.loc[mask, 'genotype'] = np.where(True, self.dataframe.loc[mask, 'genotype'].apply(DPYD_get_activity),
                                                        no_change)

    def DPYD_phenotype(self):
        data = Extract().pharmacydata()
        DPYD_data = data[data['Gen'] == 'DPYD']

        def DPYD_get_phenotype(genotype):
            result = DPYD_data.loc[DPYD_data['Uitslag'] == genotype, 'Fenotype/Functie']
            if not result.empty:
                return result.iloc[0]
            else:
                return 'ERROR'

        mask = self.dataframe['gene'] == 'DPYD'
        no_change = self.dataframe.loc[mask, 'phenotype']
        self.dataframe.loc[mask, 'phenotype'] = np.where(True,
                                                        self.dataframe.loc[mask, 'genotype'].apply(DPYD_get_phenotype),
                                                        no_change)