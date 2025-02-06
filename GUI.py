import tkinter as tk
from tkinter import filedialog

# Create the main window
root = tk.Tk()
root.title('Main')
root.geometry('400x200')

# Add delete reports checkbox
delete_reports_var = tk.BooleanVar()
delete_reports_checkbox = tk.Checkbutton(root, text='Delete all current reports', variable=delete_reports_var)
delete_reports_checkbox.pack()

# Add customer data select field
file_label = tk.Label(root, text="No file selected")
file_label.pack()
def select_file():
    file_path = filedialog.askopenfilename(title="Select Customer Data File")
    file_label.config(text=file_path)  # Update label with the file path
file_button = tk.Button(root, text="Choose Customer Data File", command=select_file)
file_button.pack()

# Add generate PDF checkbox
generate_pdf_var = tk.BooleanVar()
generate_pdf_checkbox = tk.Checkbutton(root, text='Generate PDF\'s', variable=generate_pdf_var)
generate_pdf_checkbox.pack()

# Run the GUI
root.mainloop()
