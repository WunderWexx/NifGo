"""
Wat moet de GUI kunnen?

1. Alle benodigde files moeten op scherm 1 gekozen kunnen worden
2. Alle opties moeten op scherm 1 gekozen kunnen worden
3. Alle opties moeten, waar mogelijk, onafhankelijk van elkaar uitgevoerd kunnen worden
4. De GUI moet aangeven wat het programma heeft gedaan en aan het doen is
5. De GUI moet je instellingen herinneren
6. De GUI moet mooi zijn / dynamisch gevormd zijn
"""

import tkinter as tk
from tkinter import filedialog

# Models
class ConfigurationModel:
    def __init__(self):
        self.phenotype_path = tk.StringVar()
        self.genotype_path = tk.StringVar()
        self.unknowns_correction_path = tk.StringVar()
        self.customer_data_path = tk.StringVar()
        self.pdf_check = tk.BooleanVar()
        self.delete_check = tk.BooleanVar()
        self.openall_check = tk.BooleanVar()

    def get_data(self):
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
                                   command=self.controller.execute_action)
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
class ConfigurationController:
    def __init__(self, root):
        self.model = ConfigurationModel()
        self.view = ConfigurationView(root, self, self.model)

    def choose_file(self, entry_widget, path_var):
        file_path = filedialog.askopenfilename()
        if file_path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, file_path)
            path_var.set(file_path)

    def execute_action(self):
        # Handle the execution logic here
        # For demonstration purposes, we'll just show the model data in the output window
        output_text = "\n".join(f"{key}: {value.get()}" for key, value in self.model.get_data().items())
        self.view.show_output(output_text)

    def back_to_configuration(self):
        self.view.clear()
        self.view.create_widgets()

# Main application window
def main():
    root = tk.Tk()
    root.title('Configuratiescherm')
    root.geometry('1024x768')
    controller = ConfigurationController(root)
    root.mainloop()

if __name__ == "__main__":
    main()
