# All the changes NifGo wants made to the standard ThermoFisher output.

# You might try using a loop for PhenotypeChanges instead of applying each change. See whats faster.

import numpy as np

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

    def RYR1(self):
        """
        The Indeterminate phenotype is changed to NM.
        """
        mask = self.dataframe['gene'] == 'RYR1'
        no_change = self.dataframe.loc[mask, 'phenotype']
        self.dataframe.loc[mask, 'phenotype'] = np.where(self.dataframe.loc[mask, 'phenotype'] == 'Indeterminate',
                                                         'NM',
                                                         no_change)

    def G6DP(self):
        """
        The Indeterminate phenotype is changed to NM.
        """
        mask = self.dataframe['gene'] == 'G6PD'
        no_change = self.dataframe.loc[mask, 'phenotype']
        self.dataframe.loc[mask, 'phenotype'] = np.where(self.dataframe.loc[mask, 'phenotype'] == 'Indeterminate',
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
        condition = [
            (self.dataframe['genotype'] == "*1/*22") | (self.dataframe['genotype'] == "*3/*22"),
            (self.dataframe['genotype'] == "*22/*22")
        ]
        self.dataframe['phenotype'] = np.where(condition[0], 'IM',
                                               np.where(condition[1],'PM', self.dataframe['phenotype']))

class GenotypeChanges:
    def __init__(self, dataframe):
        self.dataframe = dataframe

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
        function = lambda row: COMT_dict[row] if row['phenotype'] in COMT_dict else 'unknown'
        self.dataframe['genotype'] = self.dataframe.apply(function, axis=1)