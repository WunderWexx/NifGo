# Where everything comes together

# imports
from timeit import default_timer as timer
import Diagnostics
import ELT
from ELT import ThermoFisher_determined_genes, probeset_id_dict
import Utilities as util
from Cards import cards
import pandas as pd
import NifgoProprietaryChanges as changes
from FarmacogeneticReport import farmacogenetic_report
from info_sheet import InfoSheet
from NutrigenomicsReport import nutrigenomics_report
from HandlingUnknowns import HandlingUnknowns
from multiprocessing import Pool, cpu_count
from functools import partial
from docx2pdf import convert


# Functie voor multi-processing
def generate_farmacogenetic_report(id, dataframe, customer_data):
    farmaco = farmacogenetic_report(sample_id=id, dataframe=dataframe, customer_data=customer_data)
    farmaco.report_generation()

def generate_infosheet(id, dataframe, customer_data):
    infosheet = InfoSheet(sample_id=id, dataframe=dataframe, customer_data=customer_data)
    infosheet.report_generation()

def generate_nutrinomics_report(id, dataframe, customer_data):
    nutrigenomics = nutrigenomics_report(sample_id=id, dataframe=dataframe, customer_data=customer_data)
    nutrigenomics.report_generation()

if __name__ == "__main__":

    # settings
    pd.options.mode.chained_assignment = None  # default='warn'

    # Delete existing reports
    ask_delete_reports = util.popup_yes_no("Wilt u de bestaande rapporten verwijderen?")
    if ask_delete_reports:
        util.empty_folder('Output/Reports')
        util.empty_folder('Output/Reports/PDF')

    # Phenotypes.rpt ingestion and transformation
    phenotypes_df = ELT.Extract().phenotype_rpt()
    phenotypes_df = ELT.Load().phenotype_rpt(phenotypes_df)
    print('phenotype import DONE')
    phenotype_transformation = ELT.Transform().phenotype_rpt(phenotypes_df)
    phenotype_transformation.remove_cel_suffix()
    phenotype_transformation.drop_gene_function()
    phenotype_transformation.filter_thermofisher_genes(ThermoFisher_determined_genes)
    phenotype_transformation.rename_known_call()

    phenotypes_df = phenotype_transformation.dataframe
    util.store_dataframe(phenotypes_df, 'phenotypes')
    print('phenotype transformation DONE')

    # Genotypes.txt ingestion and transformation
    print('genotype import [...]',end='\r')
    genotypes_df = ELT.Extract().genotype_txt()
    genotypes_df = ELT.Load().genotype_txt(genotypes_df, probeset_id_dict.values())
    print('genotype import DONE')
    genotypes_transformation = ELT.Transform().genotype_txt(genotypes_df, probeset_id_dict)
    genotypes_transformation.drop_columns_after_last_sample()
    genotypes_transformation.drop_cel_call_code_suffix()
    genotypes_transformation.unpivot_dataframe()
    genotypes_transformation.reorder_and_rename_columns()
    genotypes_transformation.add_gene_names()

    genotypes_df = genotypes_transformation.dataframe
    util.store_dataframe(genotypes_df, 'genotypes')
    print('genotype transformation DONE')

    # Data preparation
    data_preparation = ELT.DataPreparation(genotypes_df, phenotypes_df)
    data_preparation.merge_geno_and_phenotype_dataframes()
    data_preparation.determine_phenotype()
    data_preparation.move_MTHFR1298_and_CYP2C19()
    data_preparation.merge_VDR()
    data_preparation.keep_only_batch_relevant_data()

    complete_dataframe = data_preparation.complete_dataframe
    util.store_dataframe(complete_dataframe, 'complete')
    print('complete dataframe creation DONE')

    # Implementing Nifgo changes
    general_changes = changes.GeneralChanges(complete_dataframe)
    util.execute_all_methods(general_changes)
    complete_dataframe = general_changes.dataframe

    gene_name_changes = changes.GeneNameChanges(complete_dataframe)
    util.execute_all_methods(gene_name_changes)
    complete_dataframe = gene_name_changes.dataframe

    phenotype_changes = changes.PhenotypeChanges(complete_dataframe)
    util.execute_all_methods(phenotype_changes)
    complete_dataframe = phenotype_changes.dataframe

    genotype_changes = changes.GenotypeChanges(complete_dataframe)
    util.execute_all_methods(genotype_changes)
    complete_dataframe = genotype_changes.dataframe

    combined_changes = changes.CombinedChanges(complete_dataframe)
    util.execute_all_methods(combined_changes)
    complete_dataframe = combined_changes.dataframe
    util.store_dataframe(complete_dataframe, 'complete')
    print('Implementing NifGo changes DONE')

    # Handling unknowns
    print('Handling unknowns [...]')
    handler = HandlingUnknowns(complete_dataframe)
    handler.correct_unknowns()
    handler.detect_unknowns()
    complete_dataframe = handler.dataframe
    util.store_dataframe(complete_dataframe, 'complete')
    handler.detect_unknowns()
    print('Handling unknowns DONE')

    # Import customer data
    customerdata_present = util.popup_yes_no("Heeft u het bestand met de klantdata?")
    if customerdata_present:
        customerdata_df = pd.read_excel(util.popup_get_file('customer data'), header=None)
        customerdata_df = ELT.Transform.customer_data().columns_and_dates(customerdata_df)
    else:
        customerdata_df = None

    # Generate cards.xlsx file
    kaarten_jn = util.popup_yes_no('Wilt u het kaartenbestand genereren?')
    if kaarten_jn:
        cards(complete_dataframe,customerdata_df)
        print('Generating cards.xlsx DONE')
    else:
        print('No cards generated')

    # Define unique list of sample_id's for report generation
    unique_sample_id_list = complete_dataframe['sample_id'].unique().tolist()

    # Farmacogenetic Reports generation
    print('Generating farmacogenetic reports [...]')
    timer_start = timer()
    partial_generate_farmacogenetic_report = partial(generate_farmacogenetic_report,
                                                     dataframe=complete_dataframe,
                                                     customer_data=customerdata_df)
    with Pool(cpu_count()) as pool:
        pool.map(partial_generate_farmacogenetic_report, unique_sample_id_list)
    timer_end = timer()
    farmacogenetics_generation_time = timer_end - timer_start
    print('Generating farmacogenetic reports DONE')

    # Infosheet generation
    print('Generating info sheets [...]')
    timer_start = timer()
    partial_generate_infosheet = partial(generate_infosheet,
                                         dataframe=complete_dataframe,
                                         customer_data=customerdata_df)
    with Pool(cpu_count()) as pool:
        pool.map(partial_generate_infosheet, unique_sample_id_list)
    timer_end = timer()
    infosheets_generation_time = timer_end - timer_start
    print('Generating info sheets DONE')

    # Nutrinomics Reports generation
    print('Generating nutrinomics reports [...]')
    timer_start = timer()
    partial_generate_nutrinomics_report = partial(generate_nutrinomics_report,
                                                  dataframe=complete_dataframe,
                                                  customer_data=customerdata_df)
    with Pool(cpu_count()) as pool:
        pool.map(partial_generate_nutrinomics_report, unique_sample_id_list)
        # ValueError: Length of values (26) does not match length of index (23) betekent dat er genen missen uit het source bestand
    timer_end = timer()
    nutrinomics_generation_time = timer_end - timer_start
    print('Generating nutrinomics reports DONE')

    # Export to PDF
    ask_pdf_generation = util.popup_yes_no("Wilt u de PDF bestanden aanmaken?")
    if ask_pdf_generation:
        print('Exporting to PDF [...]'
              '\nThis may take up to 15 minutes.'
              '\n!!! You CANNOT open Word.docx documents during this time. !!!')
        reports = util.get_reports()
        try:
            convert('Output/Reports/','Output/Reports/PDF')
        except:
            pdf_reports = util.get_reports('Output\\Reports\\PDF')
            if len(pdf_reports) == len(reports):
                pass
            else:
                missed_conversions = []
                print(f'ERROR ENCOUNTERED\n{len(pdf_reports)} out of {len(reports)} reports converted.\nMissed conversions:')
                for pdf in pdf_reports:
                    pdf_report = pdf.replace('pdf','docx')
                    if pdf_report not in reports:
                        missed_conversions.append(pdf_report)
                for report in missed_conversions:
                    print(report)
        print('Exporting to PDF DONE')
    else:
        print('NO PDF EXPORT')

    # Check if all genotypes in genotypes_df are filled, so diagnostics can be run on those
    if genotypes_df['genotype'].isnull().any():
        # Run diagnostics
        print('Generating diagnostics [...]')
        ext_diag = Diagnostics.ExternalDiagnostics()
        ext_diag.check_phenotype_shape()
        ext_diag.check_genotype_shape()
        ext_diag.check_deviation_percentage()
        if customerdata_df is not None:
            ext_diag.check_customerdata_available_to_reports(customerdata_df)
        ext_diag.check_batch_size()
        print('Generating diagnostics DONE')
    else:
        print('Not all genotypes present. No diagnostics generated. Please add any missing genotypes to the corrected unknowns file.')