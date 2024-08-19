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

def choose_file(entry_widget, path_var):
    file_path = filedialog.askopenfilename()
    if file_path:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, file_path)
        path_var.set(file_path)

# Define main window
root  = tk.Tk()
root.title('Configuratiescherm')
root.geometry('1024x768')

# Declare variables used in GUI
phenotype_path = tk.StringVar()
genotype_path = tk.StringVar()
unknowns_correction_path = tk.StringVar()
customer_data_path = tk.StringVar()
pdf_check = tk.BooleanVar()
delete_check = tk.BooleanVar()
openall_check = tk.BooleanVar()

# Static text in main window
starting_text = tk.Label(root,
                         text='Configureer hier hoe je het programma wil draaien',
                         font=('Arial',14))
starting_text.grid(row=0,column=0)

# Choose phenotype file
phenotype_text = tk.Label(root, text='Fenotype:', font=('Arial',12))
phenotype_text.grid(row=1,column=0,padx=35,pady=10,sticky='w')
phenotype_entry = tk.Entry(root,
                           textvariable=phenotype_path,
                           font=('Arial',14))
phenotype_entry.grid(row=1,column=1,padx=10,pady=10,sticky='w')
choose_phenotype_button = tk.Button(root,
                                    text='Bestand kiezen',
                                    font=('Arial',12),
                                    command=lambda: choose_file(phenotype_entry, phenotype_path)
                                    )
choose_phenotype_button.grid(row=1,column=2,padx=10,pady=10,sticky='w')

# Choose genotype file
genotype_text = tk.Label(root, text='Genotype:', font=('Arial',12))
genotype_text.grid(row=2,column=0,padx=35,pady=10,sticky='w')
genotype_entry = tk.Entry(root,
                          textvariable=genotype_path,
                          font=('Arial',14))
genotype_entry.grid(row=2,column=1,padx=10,pady=10,sticky='w')
choose_genotype_button = tk.Button(root,
                                   text='Bestand kiezen',
                                   font=('Arial',12),
                                   command=lambda: choose_file(genotype_entry, genotype_path)
                                   )
choose_genotype_button.grid(row=2,column=2,padx=10,pady=10,sticky='w')

# Choose corrected unknowns file
unknowns_text = tk.Label(root, text='Unknowns:', font=('Arial',12))
unknowns_text.grid(row=3,column=0,padx=35,pady=10,sticky='w')
unknowns_entry = tk.Entry(root,
                          textvariable=unknowns_correction_path,
                          font=('Arial',14))
unknowns_entry.grid(row=3,column=1,padx=10,pady=10,sticky='w')
choose_unknowns_button = tk.Button(root,
                                   text='Bestand kiezen',
                                   font=('Arial',12),
                                   command=lambda: choose_file(unknowns_entry, unknowns_correction_path)
                                   )
choose_unknowns_button.grid(row=3,column=2,padx=10,pady=10,sticky='w')

# Choose customer_data file
customer_data_text = tk.Label(root, text='Klantgegevens:', font=('Arial',12))
customer_data_text.grid(row=4,column=0,padx=35,pady=10,sticky='w')
customer_data_entry = tk.Entry(root,
                          textvariable=customer_data_path,
                          font=('Arial',14))
customer_data_entry.grid(row=4,column=1,padx=10,pady=10,sticky='w')
choose_customer_data_button = tk.Button(root,
                                   text='Bestand kiezen',
                                   font=('Arial',12),
                                   command=lambda: choose_file(customer_data_entry, customer_data_path)
                                   )
choose_customer_data_button.grid(row=4,column=2,padx=10,pady=10,sticky='w')

# Check generate PDF
pdf_checkbox = tk.Checkbutton(
    root
    ,text='PDF bestanden genereren'
    ,variable=pdf_check
    ,font=('Arial',12)
)
pdf_checkbox.grid(row=5,column=0,padx=10,pady=10,sticky='w')

# Check delete existing reports
delete_checkbox = tk.Checkbutton(
    root
    ,text='Alle bestaande rapporten verwijderen'
    ,variable=delete_check
    ,font=('Arial',12)
)
delete_checkbox.grid(row=6,column=0,padx=10,pady=10,sticky='w')

# Check open all reports
openall_checkbox = tk.Checkbutton(
    root
    ,text='Alle rapporten openen'
    ,variable=openall_check
    ,font=('Arial',12)
)
openall_checkbox.grid(row=7,column=0,padx=10,pady=10,sticky='w')

root.mainloop()