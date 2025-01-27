"""
After the program has run, the output needs to be checked for mistakes both human and software. This process should be automated as much as possible
"""

import re
import Utilities as util
from docx import Document
from math import ceil

class ExternalDiagnostics:
    def __init__(self):
        self.path = 'Output\Reports'
        self.reports = util.get_reports()
        self.genes_by_phenotype_type = {
            'NM_phenotype_genes': [
                'CYP1A2', 'CYP2A6', 'CYP2B6', 'CYP2C19', 'CYP2C8', 'CYP2C9',
                'CYP2D6', 'CYP2E1', 'CYP3A4', 'CYP4F2', 'DPYD',
                'G6PD', 'GSTP1', 'IFNL3', 'MTHFR1298', 'MTHFR677', 'RYR1',
                'TPMT', 'UGT1A1', 'VKORC1','OPRM1'
            ],
            'NA_phenotype_genes': ['NAT1', 'NAT2'],
            'NF_phenotype_genes': ['CACNA1S', 'CFTR', 'SLCO1B1','MTRNR1'],
            'expresser_phenotype_genes': ['CYP3A5'],
            'pos_neg_phenotype_genes': ['HLA-B*1502'],
            'PM_risico_phenotype_genes': ['F2','F5']
        }
        self.pharmacogenetic_genes_list = [
            'COMT','CACNA1S', 'CFTR', 'CYP1A2', 'CYP2A6', 'CYP2B6', 'CYP2C19',
            'CYP2C8', 'CYP2C9', 'CYP2D6', 'CYP2E1', 'CYP3A4', 'CYP3A5',
            'CYP4F2', 'DPYD', 'F2', 'F5', 'G6PD', 'GSTP1', 'HLA-B*1502',
            'IFNL3', 'MTHFR1298', 'MTHFR677', 'MTRNR1', 'NAT1', 'NAT2',
            'RYR1', 'SLCO1B1', 'TPMT', 'UGT1A1', 'VKORC1', 'OPRM1'
        ]
        self.infosheet_genes_list = [
            'COMT','CYP1A2', 'CYP2B6', 'CYP2C19', 'CYP2C9', 'CYP2D6', 'CYP3A4',
            'CYP3A5', 'DPYD', 'HLA-B*1502', 'MTHFR677', 'SLCO1B1',
            'TPMT', 'UGT1A1', 'VKORC1'
        ]
        self.nutrinomics_genes_list = [
            'ABCB1', 'ACE', 'ADIPOQ', 'ADRA2A', 'ALDH2', 'BCO1', 'BDNF-AS;BDNF',
            'DRD2', 'FTO', 'GC', 'GCK,YKT6', 'IGF1', 'LDLR', 'LOC105447645;FUT2',
            'MAO-B', 'MC4R', 'MTNR1B', 'NADSYN1', 'NBPF3', 'Sult1A1',
            'Sult1E1', 'TCF7L2', 'TMEM165;CLOCK', 'TNFa', 'UCP2', 'VDR'
        ]
        self.possible_phenotypes_by_type = {
            'NM_phenotype_genes': ['UM', 'RM', 'NM', 'IM', 'PM'],
            'NA_phenotype_genes': ['RA', 'NA', 'IA', 'SA'],
            'NF_phenotype_genes': ['IF', 'NF', 'DF', 'PF'],
            'expresser_phenotype_genes': ['non-expresser', 'homozygoot', 'heterozygoot'],
            'pos_neg_phenotype_genes': ['positief', 'negatief', 'risico'],
            'PM_risico_phenotype_genes': ['PM', 'risico']
        }
        self.normal_phenotype_dict = {
            'NM_phenotype_genes': 'NM',
            'NA_phenotype_genes': 'NA',
            'NF_phenotype_genes': 'NF',
            'expresser_phenotype_genes': 'non-expresser',
            'pos_neg_phenotype_genes': 'negatief',
            'PM_risico_phenotype_genes': 'PM'
        }

    def get_doc_type(self, document_path):
        if util.is_substring_present_in_string(document_path, 'FarmacogeneticReport'):
            return 'Farmacogenetics'
        elif util.is_substring_present_in_string(document_path, 'InfoSheet'):
            return 'InfoSheet'
        elif util.is_substring_present_in_string(document_path, 'NutrinomicsReport'):
            return 'Nutrinomics'
        else:
            return 'Medication'

    def check_phenotypes(self, document_path):
        document = Document(document_path)

        table_to_check = None
        if util.is_substring_present_in_string(document_path, 'FarmacogeneticReport'):
            table_to_check = 1
        elif util.is_substring_present_in_string(document_path, 'InfoSheet'):
            table_to_check = 0

        genes_to_check = []
        table = document.tables[table_to_check]
        for row in table.rows[1:]:
            gene = row.cells[0].text
            phenotype = row.cells[1].text
            phenotype_type = util.get_key_from_nested_value(self.genes_by_phenotype_type, gene)
            if phenotype_type in list(self.possible_phenotypes_by_type.keys()):
                if phenotype not in self.possible_phenotypes_by_type[phenotype_type]:
                    genes_to_check.append(gene)
                else:
                    pass
        return genes_to_check

    def check_genotypes(self, document_path):
        self.genotype_regex = {
            '\D\D/\D\D' : ['CACNA1S','CFTR','IFNL3','RYR1'],
            '\d\d\d\D\D' : ['SLCO1B1'],
            '\d\d\d\d\D\D' : ['VKORC1'],
            '\AAS' : ['DPYD'],
            '\D\D\D/\D\D\D' : ['COMT'],
            '(Null|\D)/(Null|\D)' : ['F2','F5','G6PD','HLA-B*1502','MTHFR1298','MTHFR677','MTRNR1','OPRM1'],
            '\*.*/\*.*' : ['other']
        }

        document = Document(document_path)

        if util.is_substring_present_in_string(document_path, 'NutrinomicsReport'):
            genes_to_check = []
            table = document.tables[0]
            for row in table.rows[1:]:
                gene = row.cells[0].text
                genotype = row.cells[2].text
                if not re.search('(\D/\D)|(\D)', genotype):
                    genes_to_check.append(gene)
            return genes_to_check


        table_to_check = None
        if util.is_substring_present_in_string(document_path, 'FarmacogeneticReport'):
            table_to_check = 1
        elif util.is_substring_present_in_string(document_path, 'InfoSheet'):
            table_to_check = 0

        genes_to_check = []
        table = document.tables[table_to_check]
        for row in table.rows[1:]:
            gene = row.cells[0].text
            genotype = row.cells[2].text
            regex = util.get_key_from_nested_value(self.genotype_regex, gene)
            if regex is not None:
                if not re.search(regex, genotype):
                    genes_to_check.append(gene)
            else:
                regex = util.get_key_from_nested_value(self.genotype_regex, 'other')
                if not re.search(regex, genotype):
                    genes_to_check.append(gene)

        return genes_to_check

    def check_gene_presence(self, document_path):
        document = Document(document_path)
        doc_type = self.get_doc_type(document_path)

        match doc_type:
            case 'Farmacogenetics':
                table_to_check = 1
                table = document.tables[table_to_check]
                present_genes = []
                for row in table.rows[1:]:
                    gene = row.cells[0].text
                    present_genes.append(gene)
                if not util.lists_contain_same_data(self.pharmacogenetic_genes_list, present_genes):
                    return False

            case 'InfoSheet':
                table_to_check = 0
                table = document.tables[table_to_check]
                present_genes = []
                for row in table.rows[1:]:
                    gene = row.cells[0].text
                    present_genes.append(gene)
                if not util.lists_contain_same_data(self.infosheet_genes_list, present_genes):
                    return False

            case 'Nutrinomics':
                table_to_check = 0
                table = document.tables[table_to_check]
                present_genes = []
                for row in table.rows[1:]:
                    gene = row.cells[0].text
                    present_genes.append(gene)
                if not util.lists_contain_same_data(self.nutrinomics_genes_list, present_genes):
                    return False

        return True

    def identify_missing_genes(self, document_path):
        document = Document(document_path)
        doc_type = self.get_doc_type(document_path)

        match doc_type:
            case 'Farmacogenetics':
                table_to_check = 1
                table = document.tables[table_to_check]
                present_genes = []
                for row in table.rows[1:]:
                    gene = row.cells[0].text
                    present_genes.append(gene)
                missing_genes = util.find_missing_items_in_list(self.pharmacogenetic_genes_list, present_genes)
                return missing_genes

            case 'InfoSheet':
                table_to_check = 0
                table = document.tables[table_to_check]
                present_genes = []
                for row in table.rows[1:]:
                    gene = row.cells[0].text
                    present_genes.append(gene)
                missing_genes = util.find_missing_items_in_list(self.infosheet_genes_list, present_genes)
                return missing_genes

            case 'Nutrinomics':
                table_to_check = 0
                table = document.tables[table_to_check]
                present_genes = []
                for row in table.rows[1:]:
                    gene = row.cells[0].text
                    present_genes.append(gene)
                missing_genes = util.find_missing_items_in_list(self.nutrinomics_genes_list, present_genes)
                return missing_genes

    def check_infosysteem(self, document_path):
        document = Document(document_path)
        table = document.tables[0]
        genes_to_check = []
        for row in table.rows[1:]:
            gene = row.cells[0].text
            infosysteem_text = row.cells[4]
            if infosysteem_text == 'Is (nog) niet verwerkt in het infosysteem':
                genes_to_check.append(gene)
        return genes_to_check

class PharmacoDiagnostics(ExternalDiagnostics):
    def pharmaco_reports_diagnostics(self):
        diag_file = open('Output/Diagnostics/pharmaco_reports_diagnostics.txt','w')
        diag_file.write('FarmacogeneticReport diagnostics\n')
        diag_file.write('Sample\tGene\tIssue\n')
        for report in self.reports:
            if util.is_substring_present_in_string(report, 'FarmacogeneticReport'):
                document_path = self.path + '\\' + report
                sample_id = document_path.split('_')[1]

                # Checking if all genes are present
                if not self.check_gene_presence(document_path):
                    diag_file.write(f'Sample: {sample_id}\t Issue: Not all genes present:\n')
                    missing_genes = self.identify_missing_genes(document_path)
                    for gene in missing_genes:
                        diag_file.write(f'\t{gene}\n')
                
                #Checking if all phenotypes are plausible
                list_of_genes_to_check = self.check_phenotypes(document_path)
                if len(list_of_genes_to_check) != 0:
                    for gene in list_of_genes_to_check:
                        diag_file.write(f'Sample: {sample_id}\tGene: {gene}\tIssue: Implausible phenotype\n')

                # Checking if genotypes are plausible
                list_of_genes_to_check = self.check_genotypes(document_path)
                if len(list_of_genes_to_check) != 0:
                    for gene in list_of_genes_to_check:
                        diag_file.write(f'Sample: {sample_id}\tGene: {gene}\tIssue: Implausible genotype\n')

        diag_file.close()


class InfosheetDiagnostics(ExternalDiagnostics):
    def infosheet_diagnostics(self):
        diag_file = open('Output/Diagnostics/infosheet_diagnostics.txt', 'w')
        diag_file.write('Infosheet diagnostics\n')
        diag_file.write('Sample\tGene\tIssue\n')
        for report in self.reports:
            if util.is_substring_present_in_string(report, 'InfoSheet'):
                document_path = self.path + '\\' + report
                sample_id = document_path.split('_')[1]

                # Checking if all genes are present
                if not self.check_gene_presence(document_path):
                    diag_file.write(f'Sample: {sample_id}\t Issue: Not all genes present\n')
                    missing_genes = self.identify_missing_genes(document_path)
                    for gene in missing_genes:
                        diag_file.write(f'\t{gene}\n')

                # Checking if all phenotypes are plausible
                list_of_genes_to_check = self.check_phenotypes(document_path)
                if len(list_of_genes_to_check) != 0:
                    for gene in list_of_genes_to_check:
                        diag_file.write(f'Sample: {sample_id}\tGene: {gene}\tIssue: Implausible phenotype\n')

                # Checking if genotypes are plausible
                list_of_genes_to_check = self.check_genotypes(document_path)
                if len(list_of_genes_to_check) != 0:
                    for gene in list_of_genes_to_check:
                        diag_file.write(f'Sample: {sample_id}\tGene: {gene}\tIssue: Implausible genotype\n')

                #Checking if infosystem has data
                list_of_genes_to_check = self.check_infosysteem(document_path)
                if len(list_of_genes_to_check) != 0:
                    for gene in list_of_genes_to_check:
                        diag_file.write(f'Sample: {sample_id}\tGene: {gene}\tIssue: No data in infosystem\n')

        diag_file.close()

class NutrinomicsDiagnostics(ExternalDiagnostics):
    def nutrinomics_diagnostics(self):
        diag_file = open('Output/Diagnostics/nutrinomics_diagnostics.txt', 'w')
        diag_file.write('Nutrinomics diagnostics\n')
        diag_file.write('Sample\tGene\tIssue\n')
        for report in self.reports:
            if util.is_substring_present_in_string(report, 'NutrinomicsReport'):
                document_path = self.path + '\\' + report
                sample_id = document_path.split('_')[1]

                # Checking if all genes are present
                if not self.check_gene_presence(document_path):
                    diag_file.write(f'Sample: {sample_id}\t Issue: Not all genes present\n')
                    missing_genes = self.identify_missing_genes(document_path)
                    for gene in missing_genes:
                        diag_file.write(f'\t{gene}\n')

                # Checking if all genotypes are plausible
                list_of_genes_to_check = self.check_genotypes(document_path)
                if len(list_of_genes_to_check) != 0:
                    for gene in list_of_genes_to_check:
                        diag_file.write(f'Sample: {sample_id}\tGene: {gene}\tIssue: Implausible genotype\n')

        diag_file.close()

"""
class CustomerDataDiagnostics(Diagnostics):
    def customerdata_diagnostics(self):
        diag_file = open('Output/Diagnostics/customerdata_diagnostics.txt', 'w')
        for report in self.reports:
            document_path = self.path + '\\' + report
            sample_id = document_path.split('_')[1]
"""

class GeneralDiagnostics(ExternalDiagnostics):
    def metadata(self, generation_times, unique_samples_list):
        diag_file = open('Output/Diagnostics/metadata.txt', 'w')
        diag_file.write('Metadata:\n')
        diag_file.write('Version 2.0.0\n\n') # 1.0.0 voor release met UI.

        for report, time in zip(['Farmacogenetics','Infosheets','Nutrinomics','Medication'], generation_times):
            diag_file.write(f'{report} generated in {time:.1f} seconds.\n')
        diag_file.write(f'Total time: {sum(generation_times):.1f} seconds\n\n')

        number_of_samples = len(unique_samples_list)
        diag_file.write(f'Number of samples: {number_of_samples}\n')
        number_of_reports = len(self.reports)
        diag_file.write(f'Number of reports: {number_of_reports}\n')
        if number_of_reports != 3 * number_of_samples:
            diag_file.write(f'UNEXPECTED AMOUNT OF REPORTS \nEXPECTED {number_of_samples*4}, GOT {number_of_reports}')
        diag_file.write(f'Number of batches to bill: {ceil((number_of_samples / 24))}')
        diag_file.close()

    def sample_data(self, dataframe):
        diag_file = open('Output/Diagnostics/sample_data.txt', 'w')

        unique_gene_list = dataframe['gene'].unique().tolist()

        for gene in unique_gene_list:
            # Bepaalt de frequentie van de fenotypes
            subset = dataframe[dataframe['gene'] == gene]
            normalized_values = subset['phenotype'].value_counts(normalize=True)
            diag_file.write(f'{gene} frequencies:\n{normalized_values}\n')

            # Bepaalt hoeveel dat afwijkt van de norm
            gene_type = util.get_key_from_nested_value(self.genes_by_phenotype_type, gene)
            if gene_type != None:
                normal_phenotype = self.normal_phenotype_dict[gene_type]
                amount_of_normal_genes = subset.loc[subset['phenotype'] == normal_phenotype, 'phenotype'].value_counts()
                if len(amount_of_normal_genes) == 0:
                    amount_of_normal_genes = 0
                else:
                    amount_of_normal_genes = amount_of_normal_genes.iloc[0]
                amount_of_abnormal_genes = subset.loc[subset['phenotype'] != normal_phenotype, 'phenotype'].value_counts()
                if len(amount_of_abnormal_genes) == 0:
                    amount_of_abnormal_genes = 0
                else:
                    amount_of_abnormal_genes = amount_of_abnormal_genes.iloc[0]
                total_genes = amount_of_normal_genes + amount_of_abnormal_genes
                proportion_abnormal_genes = (amount_of_abnormal_genes / total_genes) * 100
                diag_file.write(f'Percentage deviant phenotypes: {proportion_abnormal_genes}%\n')
            else:
                diag_file.write(f'Phenotype did not have to be determined\n\n')
                continue

        diag_file.close()

class InlineDiagnostics:
    def __init__(self):
        self.genes_by_phenotype_pattern = {
            r'^[U,R,N,I,P]M$': [
                ['COMT', 'CYP1A2', 'CYP2B6', 'CYP2C9', 'CYP2C19', 'CYP2D6', 'CYP3A4', 'DPYD', 'G6PD', 'MTHFR677',
                 'NUDT15', 'TPMT', 'UGT1A1', 'VKORC1'], 'NM'], # Zoals NM
            r'^[I,N,D,P]F$': [['ABCG2', 'SLCO1B1', 'ABCB1'], 'NF'], # Zoals NF
            r'^[a-z]{1,12}$|^non-expresser$': [['CYP3A5'], 'non-expresser'], # Zoals een string tot max 12 kleine letters
            r'^negatief$|^risico$': [['HLA-B*1502', 'HLA-B*5701', 'HLA-A*3101'], 'negatief'], # negatief of risico
            r'^[U,R,N,I,P]M$|^Deficient$': [['G6PD'], 'NM'] # Zoals NM of Deficient
        }

        self.genes_by_genotype_pattern = {
            r'\D\D/\D\D' : ['CACNA1S', 'CFTR','RYR1',"VDR"], # Zoals WT/WT
            r'\d\d\d\D\D' : ['SLCO1B1'], # Zoals 521TC
            r'\d\d\d\d\D\D' : ['VKORC1'], # Zoals 1639GG
            r'^AS: ' : ['DPYD'], # Zoals AS: 2 of AS: 1.5
            r'\D\D\D/\D\D\D' : ['COMT'], # Zoals Met/Met
            r'(Null/Present)/(Null/Present)' : ['GSTM1'], # Zoals Null/Present
            r'(\D\.=|Null)/(\D\.=|Null)' : ['MTRNR1'], # Zoals m.=/Null
            r'(Null|\D|Val)/(Null|\D|Val)' : ["ABCB1", "ABCG2", "ACE", "ADIPOQ", "ADRA2A", "ALDH2", "AMDHD1", "BChE", "BCO1",
                                      "BDNF", "CYP1A1", "CYP1A2", "CYP2R1", "CYP17A1", "CYP24A1",
                                      'DHCR7 / NADSYN1', "DRD2", "F2", "F5", "FTO", "G6PD", "GC", "GCK, YKT6", "GSTP1",
                                      "IFNL3/IL28B", "IGF1", "LDLR", "LOC105447645; FUT2", "MAO-B", "MC4R", "MnSOD",
                                      "MTHFR1298", "MTHFR677", "MTNR1B",  "NBPF3", "NQ01", "NUDT15", "OPRM1", "PON1",
                                      "Sult1E1", "TCF7L2", "TMEM165; CLOCK", "TNFa",
                                      "TPMT", "UCP2", "UGT1A1"], # Zoals A/A of Null/A of Null/Val
            r'(Null|\*\D)/(Null|\*\D)' : ['GSPT1', 'GSTT1'],# Zoals *A/*A of Null/*A
            r'^negatief$|^positief$': ['HLA-A*3101', 'HLA-B*1502', 'HLA-B*5702'], # negatief of positief
            r'(\*.*|Null)/(\*.*|Null)' : ['other'], # Zoals *1/*1 of zelfs *4.001/*7A+1B, en ook *1/Null
        }

        # AANPASSEN! HET IS NU EEN DICT OF LISTS
        self.genes_by_normal_genotype = {
            'ABCB1': 'T/T',
            'ACE': 'A/A',
            'ADIPOQ': 'G/G',
            'ADRA2A': 'G/G',
            'ALDH2': 'G/G',
            'AMDHD1': 'C/C',
            'BChE': r'U/U|K/U',
            'BCO1': 'A/A',
            'BDNF': r'C/C|Val/Val',
            'CACNA1S': 'WT/WT',
            'CFTR': 'WT/WT',
            'CYP1A1': 'T/T',
            'CYP1B1': r'\*1/\*1',
            'CYP2A6': r'(\*1[A-K]|\*(1|6|11|13|14|22|30|31|38|44|50|2|9|17|23|25|26|28|41))/(\*1[A-K]|\*(1|6|11|13|14|22|30|31|38|44|50|2|9|17|23|25|26|28|41))',
            'CYP2C8': r'\*1[A-C]/\*1[A-C]',
            'CYP2E1': r'^(?!.*\*5B).*',
            'CYP2F1': r'\*1/\*1',
            'CYP2R1': r'A/A',
            'CYP4F2': r'\*1/\*1',
            'CYP17A1': 'A/A',
            'CYP24A1': 'T/T',
            'DHCR7 / NADSYN1': 'G/G',
            'DRD2': 'C/C',
            'F2': 'G/G',
            'F5': 'C/C',
            'FTO': 'G/G',
            'GC': 'T/T',
            'GCK, YKT6': 'G/G',
            'GSTP1': r'\*A/\*A',
            'GSTT1': r'Null/\*A|\*A/\*A|\*A/Null',
            'GSTM1': r'Null/Present|Present/Null|Present/Present',
            'HLA-B*3101': 'WT/WT',
            'IFNL3/IL28B': 'C/C',
            'IGF1': 'G/G',
            'LDLR': 'G/G',
            'LOC105447645; FUT2': 'A/A',
            'MAO-B': 'T/T|T',
            'MC4R': 'T/T',
            'MnSOD': r'A/A|Val/Val',
            'MTHFR1298': 'A/A',
            'MTRNR1': r'm.=/Null|m.=/m.=|Null/m.=',
            'MTNR1B': 'C/C',
            'NAT1': r'\*(4|18|20|21|23|24|25|27|29)/\*(4|18|20|21|23|24|25|27|29)',
            'NAT2': r'\*(4|18)/\*(4|18)',
            'NBPF3': 'T/T',
            'NQ01': 'G/G',
            'OPRM1': 'A/A',
            'PON1': 'T/T',
            'RYR1': 'WT/WT',
            'Sult1A1': r'\*1/\*1',
            'Sult1E1': 'C/C',
            'TCF7L2': 'C/C',
            'TMEM165; CLOCK': 'A/A',
            'TNFa': 'G/G',
            'UCP2': 'G/G',
            'VDR': 'WT/WT'
        }

    def is_fenotype_deviation(self, phenotype, gene):
        for pattern in self.genes_by_phenotype_pattern.keys():
            if re.fullmatch(pattern, phenotype):
                if gene in self.genes_by_phenotype_pattern[pattern][0]:
                    return not phenotype == self.genes_by_phenotype_pattern[pattern][1]

    def is_genotype_deviation(self, genotype, gene_to_check):
        regex_pattern = self.genes_by_normal_genotype[gene_to_check]
        return not re.fullmatch(regex_pattern, genotype)