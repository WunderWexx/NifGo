# TO DO
"""
Add functionality
Add formatting
Add configuration storage
"""

import tkinter as tk
from tkinter import filedialog
from tkinter import scrolledtext

# Functions
def write_to_terminal(text):
    output_terminal.config(state='normal')
    output_terminal.insert(tk.END, text + '\n')
    output_terminal.see(tk.END)  # Auto-scroll to the bottom
    output_terminal.config(state='disabled')

# Create the main window
root = tk.Tk()
root.title('Run Configuration')
root.geometry('400x400')

# Add delete reports checkbox
delete_reports_var = tk.BooleanVar()
delete_reports_checkbox = tk.Checkbutton(root, text='Delete all current reports', variable=delete_reports_var)
delete_reports_checkbox.pack()

# Add rpt file select field
rpt_file_label = tk.Label(root, text="No file selected")
rpt_file_label.pack()
def select_file():
    file_path = filedialog.askopenfilename(title="Select phenotype (.rpt) File")
    rpt_file_label.config(text=file_path)  # Update label with the file path
file_button = tk.Button(root, text="Choose phenotype (.rpt) File", command=select_file)
file_button.pack()

# Add txt file select field
txt_file_label = tk.Label(root, text="No file selected")
txt_file_label.pack()
def select_file():
    file_path = filedialog.askopenfilename(title="Select Genotype (.txt) File")
    txt_file_label.config(text=file_path)  # Update label with the file path
file_button = tk.Button(root, text="Choose genotype (.txt) File", command=select_file)
file_button.pack()

# Add unknowns file select field
unknowns_file_label = tk.Label(root, text="No file selected")
unknowns_file_label.pack()
def select_file():
    file_path = filedialog.askopenfilename(title="Select Corrected Unknowns File")
    unknowns_file_label.config(text=file_path)  # Update label with the file path
file_button = tk.Button(root, text="Select Corrected Unknowns File", command=select_file)
file_button.pack()

# Add customer data select field
customer_data_file_label = tk.Label(root, text="No file selected")
customer_data_file_label.pack()
def select_file():
    file_path = filedialog.askopenfilename(title="Select Customer Data File")
    customer_data_file_label.config(text=file_path)  # Update label with the file path
file_button = tk.Button(root, text="Choose Customer Data File", command=select_file)
file_button.pack()

# Add generate cards.xlsx checkbox
generate_cards_var = tk.BooleanVar()
generate_cards_checkbox = tk.Checkbutton(root, text='Generate cards.xlsx', variable=generate_cards_var)
generate_cards_checkbox.pack()


# Add generate PDF checkbox
generate_pdf_var = tk.BooleanVar()
generate_pdf_checkbox = tk.Checkbutton(
    root,
    text="Generate PDF's",
    variable=generate_pdf_var
)
generate_pdf_checkbox.pack()
pdf_warning_label = tk.Label(
    root,
    text="(Warning! Generating PDF's may take up to 15 minutes.\n"
         "You cannot open Word (.docx) files during this time.",
    fg='red'
)
pdf_warning_label.pack()


# Output terminal at the bottom
output_terminal = scrolledtext.ScrolledText(root, height=8, wrap=tk.WORD, state='disabled')
output_terminal.pack(fill='both', expand=True)

# Run the GUI
root.mainloop()
