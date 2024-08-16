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

def choose_file(entry_widget):
    # Open file dialog and allow user to select a file
    file_path = filedialog.askopenfilename()

    # Display the file path in the provided entry widget
    if file_path:  # Check if a file was selected
        entry_widget.delete(0, tk.END)  # Clear the entry box
        entry_widget.insert(0, file_path)  # Insert the file path into the entry box

root  = tk.Tk()
root.title('Configuratiescherm')
root.geometry('1024x768')

starting_text = tk.Label(root,text='Configureer hier hoe je het programma wil draaien', font=('Arial',14))
starting_text.grid(row=0,column=0)

phenotype_entry = tk.Entry(root, font=('Arial',14))
phenotype_entry.grid(row=1,column=0)
choose_phenotype_button = tk.Button(root,
                                    text='Bestand kiezen',
                                    font=('Arial',12),
                                    command=lambda: choose_file(phenotype_entry)
                                    )
choose_phenotype_button.grid(row=1,column=1)

genotype_entry = tk.Entry(root, font=('Arial',14))
genotype_entry.grid(row=2,column=0)
choose_genotype_button = tk.Button(root,
                                   text='Bestand kiezen',
                                   font=('Arial',12),
                                   command=lambda: choose_file(genotype_entry)
                                   )
choose_genotype_button.grid(row=2,column=1)

root.mainloop()

# Variable bruikbaar maken
"""
import tkinter as tk
from tkinter import filedialog

def choose_file(entry_widget, file_var):
    # Open file dialog and allow user to select a file
    file_path = filedialog.askopenfilename()
    
    # Display the file path in the provided entry widget and store it in the variable
    if file_path:  # Check if a file was selected
        entry_widget.delete(0, tk.END)  # Clear the entry box
        entry_widget.insert(0, file_path)  # Insert the file path into the entry box
        file_var.set(file_path)  # Store the file path in the variable

# Create the main window
root = tk.Tk()
root.title("File Chooser")
root.geometry("500x200")

# Variables to store the file paths
file1_path = tk.StringVar()
file2_path = tk.StringVar()

# Create the first entry widget for the first file
entry1 = tk.Entry(root, textvariable=file1_path, width=50, font=("Arial", 14))
entry1.pack(pady=10)

# Create the first button to open the file dialog for the first file
button1 = tk.Button(root, text="Choose First File", command=lambda: choose_file(entry1, file1_path), font=("Arial", 12))
button1.pack(pady=5)

# Create the second entry widget for the second file
entry2 = tk.Entry(root, textvariable=file2_path, width=50, font=("Arial", 14))
entry2.pack(pady=10)

# Create the second button to open the file dialog for the second file
button2 = tk.Button(root, text="Choose Second File", command=lambda: choose_file(entry2, file2_path), font=("Arial", 12))
button2.pack(pady=5)

# Function to display the stored file paths
def print_file_paths():
    print(f"First file path: {file1_path.get()}")
    print(f"Second file path: {file2_path.get()}")

# Add a button to print the stored file paths
print_button = tk.Button(root, text="Print File Paths", command=print_file_paths, font=("Arial", 12))
print_button.pack(pady=20)

# Start the Tkinter event loop
root.mainloop()
"""