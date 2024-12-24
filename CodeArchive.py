"""Unused and non-executable code, that might be useful in the future"""

def generate_medication_report(id, dataframe):
    medrep = MedicationReport(sample_id=id, dataframe=dataframe)
    medrep.medrep_intro_text()
    medrep.medrep_core_exec()
    medrep.save()

# Medication report generation
    print('Generating medication reports [...]')
    timer_start = timer()
    partial_generate_medication_report = partial(generate_medication_report, dataframe=complete_dataframe)
    with Pool(cpu_count()) as pool:
        pool.map(partial_generate_medication_report, unique_sample_id_list)
    timer_end = timer()
    medication_generation_time = timer_end - timer_start
    print('Generating medication reports [DONE]')

# Filling in customer data
    file_is_present = sg.popup_yes_no("Heeft u het bestand met de klantdata?")
    if file_is_present == 'Yes':
        print('Filling in customer data [...]')
        CustomerData().fill_customer_data()
        print('Filling in customer data [DONE]')