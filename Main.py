# Where everything comes together

# imports
import os
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

if __name__ == '__main__':
    print("\n\nDe functionaliteit van deze file wordt voortaan aangeroepen vanuit GUI.py.\n\n")

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

def generation_script(delete_reports: bool,
                      phenotype_file: str,
                      genotype_file: str,
                      corrected_unknowns_file: str = None,
                      customer_data_file: str = None,
                      generate_cards: bool = False,
                      generate_pdf: bool = False,
                      ):

    # settings
    pd.options.mode.chained_assignment = None  # default='warn'

    # Delete existing reports
    if delete_reports:
        util.empty_folder('Output/Reports')
        util.empty_folder('Output/Reports/PDF')

    # Phenotypes.rpt extraction and transformation
    print("Importing phenotype data [...]")
    phenotypes_df = pd.read_csv(phenotype_file, sep="@", header=None, engine="python")
    phenotypes_df = ELT.Load().phenotype_rpt(phenotypes_df)
    print('Importing phenotype data DONE')
    phenotype_transformation = ELT.Transform().phenotype_rpt(phenotypes_df)
    phenotype_transformation.remove_cel_suffix()
    phenotype_transformation.drop_gene_function()
    phenotype_transformation.filter_thermofisher_genes(ThermoFisher_determined_genes)
    phenotype_transformation.rename_known_call()
    phenotype_transformation.replace_null_with_missing()

    print('Transforming phenotype data [...]')
    phenotypes_df = phenotype_transformation.dataframe
    util.store_dataframe(phenotypes_df, 'phenotypes')
    print('Transforming phenotype data DONE')

    # Genotypes.txt extraction
    print('Importing genotype data [...]')
    genotypes_df = ELT.Extract().extract_genotype_txt(genotype_file)
    print('Importing genotype data DONE')

    # Checking sex
    sex_check_df = Diagnostics.ExternalDiagnostics.check_sex(genotypes_df)

    # Genotypes.txt transformation
    print('Transforming genotype data [...]')
    genotypes_df = ELT.Load().genotype_txt(genotypes_df, probeset_id_dict.values())
    genotypes_transformation = ELT.Transform().genotype_txt(genotypes_df, probeset_id_dict)
    genotypes_transformation.drop_columns_after_last_sample()
    genotypes_transformation.drop_cel_call_code_suffix()
    genotypes_transformation.unpivot_dataframe()
    genotypes_transformation.reorder_and_rename_columns()
    genotypes_transformation.add_gene_names()

    genotypes_df = genotypes_transformation.dataframe
    util.store_dataframe(genotypes_df, 'genotypes')
    print('Transforming genotype data DONE')

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
    del genotypes_df
    del phenotypes_df

    # Implementing Nifgo changes
    """ # Code removed on 2025-12-19. Choices in phenotype will now be determined via unknowns.
    general_changes = changes.GeneralChanges(complete_dataframe)
    util.execute_all_methods(general_changes)
    complete_dataframe = general_changes.dataframe
    """
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
    corrected_unknowns_df = handler.get_corrected_unknowns(corrected_unknowns_file)
    handler.correct_unknowns(corrected_unknowns_df)
    handler.detect_unknowns()
    complete_dataframe = handler.dataframe
    util.store_dataframe(complete_dataframe, 'complete')
    handler.detect_unknowns()
    print('Handling unknowns DONE')

    # Import customer data
    if customer_data_file:
        customerdata_df = pd.read_excel(customer_data_file, header=None)
        customerdata_df = ELT.Transform.customer_data().columns_and_dates(customerdata_df)
        print('Importing customer data DONE')
    else:
        customerdata_df = None
        print('No customer data file provided')

    # Generate cards.xlsx file
    if customerdata_df is not None:
        should_generate_cards = generate_cards
    else:
        should_generate_cards = None
    if should_generate_cards:
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
    ask_pdf_generation = generate_pdf
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
        print('No PDF export')

    # Run diagnostics
    if (corrected_unknowns_file is not None and customerdata_df is not None):
        try:
            print('Generating diagnostics [...]')
            ext_diag = Diagnostics.ExternalDiagnostics()
            ext_diag.check_phenotype_shape()
            ext_diag.check_genotype_shape()
            ext_diag.compare_sex(customerdata_df, sex_check_df)
            ext_diag.check_deviation_percentage()
            if customerdata_df is not None:
                ext_diag.check_customerdata_available_to_reports(customerdata_df)
            ext_diag.check_batch_size()
            print('Generating diagnostics DONE')
        except Exception as e:
            print('ERROR ENCOUNTERED:\n'
                  f'{e}\n'
                  'Zeer waarschijnlijk missen er genotypes en/of fenotypes uit de unknown file. Hierboven de error voor meer informatie.')
    else:
        print('Not enough data available for full diagnostics. None generated.')
        if os.path.exists('Output/Diagnostics/diagnostics.txt'):
            os.remove('Output/Diagnostics/diagnostics.txt')

    print('\nAll tasks successfully executed. You may now close this window.')