"""
Wat moet de GUI kunnen?

1. Alle benodigde files moeten op scherm 1 gekozen kunnen worden [DONE]
2. Alle opties moeten op scherm 1 gekozen kunnen worden [DONE]
3. Alle opties moeten, waar mogelijk, onafhankelijk van elkaar uitgevoerd kunnen worden [ACTIVE]
4. De GUI moet aangeven wat het programma heeft gedaan en aan het doen is [DONE]
5. De GUI moet je instellingen herinneren [READY]
6. De GUI moet mooi zijn / dynamisch gevormd zijn [READY]
7. Errors moeten worden weergegeven [READY]
8. Er moet een exit knop komen [READY]
9. Stotteren moet gefixt worden [READY]
"""

import tkinter as tk
from tkinter import filedialog
import MainInFunctions as mif
import Utilities as util

# Models
class Model:
    phenotypes_df = None
    genotypes_df = None
    complete_dataframe = None
    generation_times = {
        'pharmacogenetic':None,
        'infosheet':None,
        'nutrinomics':None
    }

    def __init__(self):
        self.phenotype_path = tk.StringVar()
        self.genotype_path = tk.StringVar()
        self.unknowns_correction_path = tk.StringVar()
        self.customer_data_path = tk.StringVar()
        self.pdf_check = tk.BooleanVar()
        self.delete_check = tk.BooleanVar()
        self.openall_check = tk.BooleanVar()

    def get_config(self):
        return {
            "phenotype_path": self.phenotype_path,
            "genotype_path": self.genotype_path,
            "unknowns_correction_path": self.unknowns_correction_path,
            "customer_data_path": self.customer_data_path,
            "pdf_check": self.pdf_check,
            "delete_check": self.delete_check,
            "openall_check": self.openall_check
        }


# Views
class ConfigurationView:
    def __init__(self, root, controller, model):
        self.root = root
        self.controller = controller
        self.model = model
        self.create_widgets()

    def create_widgets(self):
        starting_text = tk.Label(self.root,
                                 text='Configureer hier hoe je het programma wil draaien',
                                 font=('Arial', 14))
        starting_text.grid(row=0, column=0)

        # Phenotype file selection
        self.create_file_selector("Fenotype:", self.model.phenotype_path, 1)
        self.create_file_selector("Genotype:", self.model.genotype_path, 2)
        self.create_file_selector("Unknowns:", self.model.unknowns_correction_path, 3)
        self.create_file_selector("Klantgegevens:", self.model.customer_data_path, 4)

        # Checkboxes
        self.create_checkbox("PDF bestanden genereren", self.model.pdf_check, 5)
        self.create_checkbox("Alle bestaande rapporten verwijderen", self.model.delete_check, 6)
        self.create_checkbox("Alle rapporten openen", self.model.openall_check, 7)

        execute_button = tk.Button(self.root,
                                   text='Uitvoeren',
                                   font=('Arial', 12),
                                   command=self.controller.general_execution)
        execute_button.grid(row=8, column=0, padx=10, pady=10, sticky='w')

    def create_file_selector(self, label_text, path_var, row):
        label = tk.Label(self.root, text=label_text, font=('Arial', 12))
        label.grid(row=row, column=0, padx=35, pady=10, sticky='w')
        entry = tk.Entry(self.root, textvariable=path_var, font=('Arial', 14))
        entry.grid(row=row, column=1, padx=10, pady=10, sticky='w')
        button = tk.Button(self.root,
                           text='Bestand kiezen',
                           font=('Arial', 12),
                           command=lambda: self.controller.choose_file(entry, path_var))
        button.grid(row=row, column=2, padx=10, pady=10, sticky='w')

    def create_checkbox(self, text, variable, row):
        checkbox = tk.Checkbutton(self.root, text=text, variable=variable, font=('Arial', 12))
        checkbox.grid(row=row, column=0, padx=10, pady=10, sticky='w')

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_output(self, output_text):
        self.clear()
        output_label = tk.Label(self.root, text="Output:", font=("Arial", 14))
        output_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')

        output_display = tk.Text(self.root, wrap=tk.WORD, font=("Arial", 12))
        output_display.grid(row=2, column=0, padx=10, pady=10, sticky='w')
        output_display.insert(tk.END, output_text)
        output_display.config(state=tk.DISABLED)

        back_button = tk.Button(self.root, text="Back", command=self.controller.back_to_configuration, font=("Arial", 12))
        back_button.grid(row=3, column=0, padx=10, pady=10, sticky='w')

# Controllers
class Controller:

    # ----- GUI related controls -----

    def __init__(self, root):
        self.model = Model()
        self.view = ConfigurationView(root, self, self.model)

    def choose_file(self, entry_widget, path_var):
        file_path = filedialog.askopenfilename()
        if file_path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, file_path)
            path_var.set(file_path)

    def back_to_configuration(self):
        self.view.clear()
        self.view.create_widgets()

    # ----- Execution related controls -----

    def delete_existing_reports(self):
        util.empty_folder('Output/Reports')
        util.empty_folder('Output/Reports/PDF')

    def phenotypes_import(self):
        config = self.model.get_config()
        phenotype_path = config['phenotype_path'].get()
        self.model.phenotypes_df = mif.phenotypes_import(phenotype_path)

    def genotypes_import(self):
        config = self.model.get_config()
        genotype_path = config['genotype_path'].get()
        self.model.genotypes_df = mif.genotypes_import(genotype_path)

    def data_preparation(self):
        phenotypes_df = self.model.phenotypes_df
        genotypes_df = self.model.genotypes_df
        self.model.complete_dataframe = mif.data_preparation(genotypes_df, phenotypes_df)

    def handling_unknowns(self):
        self.model.complete_dataframe = mif.handling_unknowns(self.model.complete_dataframe,
                                                              self.model.unknowns_correction_path.get())

    def generating_pharmacogenetic(self):
        self.model.generation_times['pharmacogenetic'] = mif.generating_pharmacogenetic(self.model.complete_dataframe)

    def generating_infosheet(self):
        self.model.generation_times['infosheet'] = mif.generating_infosheet(self.model.complete_dataframe)

    def generating_nutrinomics(self):
        self.model.generation_times['nutrinomics'] = mif.generating_nutrinomics(self.model.complete_dataframe)

    def enter_customer_data(self):
        config = self.model.get_config()
        customer_data_path = config['customer_data_path'].get()
        mif.enter_customer_data(customer_data_path)

    def exporting_to_pdf(self):
        missed_conversions = mif.export_to_pdf()
        return missed_conversions

    def diagnostics(self):
        times = tuple(self.model.generation_times.values())
        mif.diagnostics(times, self.model.complete_dataframe)

    def open_all_reports(self):
        util.open_all_reports()

    def general_execution(self):
        output = []

        config = self.model.get_config()
        for option in config:
            output.append(f'{option}: {config[option].get()}')
        self.view.show_output('\n'.join(output))
        self.view.root.update_idletasks()

        if config['delete_check'].get():
            self.delete_existing_reports()
            output.append('Rapporten verwijderd')
            self.view.show_output('\n'.join(output))
            self.view.root.update_idletasks()

        output.append('Bestanden importeren...')
        self.view.show_output('\n'.join(output))
        self.view.root.update_idletasks()
        self.phenotypes_import()
        self.genotypes_import()
        self.data_preparation()
        output.append('Bestanden geïmporteerd')
        self.view.show_output('\n'.join(output))
        self.view.root.update_idletasks()

        self.handling_unknowns()
        output.append('Unknowns verwerkt')
        self.view.show_output('\n'.join(output))
        self.view.root.update_idletasks()

        output.append('Rapporten genereren...')
        self.view.show_output('\n'.join(output))
        self.view.root.update_idletasks()
        self.generating_pharmacogenetic()
        output.append('Farmacogenetische rapporten gegenereerd...')
        self.view.show_output('\n'.join(output))
        self.view.root.update_idletasks()
        self.generating_infosheet()
        output.append('Infosheets gegenereerd...')
        self.view.show_output('\n'.join(output))
        self.view.root.update_idletasks()
        self.generating_nutrinomics()
        output.append('Nutrinomics rapporten gegenereerd...')
        self.view.show_output('\n'.join(output))
        output.append('Alle rapporten gegenereerd')
        self.view.show_output('\n'.join(output))
        self.view.root.update_idletasks()

        if len(self.model.get_config()['customer_data_path'].get()) > 0:
            self.enter_customer_data()
            output.append('Klantgegevens ingevoerd')
            self.view.show_output('\n'.join(output))
            self.view.root.update_idletasks()

        if config['pdf_check'].get():
            output.append('Bestanden worden geëxporteerd naar PDF...')
            self.view.show_output('\n'.join(output))
            self.view.root.update_idletasks()
            missed_conversions = self.exporting_to_pdf()
            output.append('Alle bestanden geëxporteerd')
            if missed_conversions is not None:
                output.append('----- ERROR: GEMISTE BESTANDEN -----\n{}'.format('\n'.join(missed_conversions)))
            self.view.show_output('\n'.join(output))
            self.view.root.update_idletasks()

        output.append('Diagnostiek genereren...')
        self.view.show_output('\n'.join(output))
        self.view.root.update_idletasks()
        self.diagnostics()
        output.append('Diagnostiek gegenereerd')
        self.view.show_output('\n'.join(output))
        self.view.root.update_idletasks()

        if config['openall_check'].get():
            self.open_all_reports()
            output.append('Alle rapporten geopend')
            self.view.show_output('\n'.join(output))
            self.view.root.update_idletasks()

        output.append('Programma succesvol uitgevoerd')
        self.view.show_output('\n'.join(output))
        self.view.root.update_idletasks()


# Main application window
def main():
    root = tk.Tk()
    root.title('Configuratiescherm')
    root.geometry('1024x768')
    Controller(root)
    root.mainloop()

if __name__ == "__main__":
    main()
