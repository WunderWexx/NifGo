import json
import os
import tkinter as tk
from tkinter import filedialog
import multiprocessing as mp

def launch_gui():
    OUTPUT_DIR = os.path.join(os.getcwd(), "Output")
    CONFIG_FILE = os.path.join(OUTPUT_DIR, "last_run_config.json")

    # --- Edit the help text here ---
    INFO_TEXT = (
        "Welcome to the Run Configuration! Here you can choose the necessary files and options for your preferred run. "
        "If you check 'Persist configuration', your current configuration will be saved for the next run."
    )

    # ----------------- helpers -----------------
    def ensure_output_dir():
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def gather_config():
        return {
            "persist_configuration": persist_config_var.get(),
            "delete_reports": delete_reports_var.get(),
            "rpt_file": rpt_path_var.get(),
            "txt_file": txt_path_var.get(),
            "unknowns_file": unknowns_path_var.get(),
            "customer_data_file": customer_data_path_var.get(),
            "generate_cards": generate_cards_var.get(),
            "generate_pdf": generate_pdf_var.get(),
        }

    def apply_config(cfg):
        persist_config_var.set(bool(cfg.get("persist_configuration", False)))
        delete_reports_var.set(bool(cfg.get("delete_reports", False)))
        rpt_path_var.set(cfg.get("rpt_file", ""))
        txt_path_var.set(cfg.get("txt_file", ""))
        unknowns_path_var.set(cfg.get("unknowns_file", ""))
        customer_data_path_var.set(cfg.get("customer_data_file", ""))
        generate_cards_var.set(bool(cfg.get("generate_cards", False)))
        generate_pdf_var.set(bool(cfg.get("generate_pdf", False)))
        update_cards_visibility()

    def save_config_if_persist():
        """Save the configuration iff persistence is enabled. Otherwise, delete any old config."""
        if persist_config_var.get():
            ensure_output_dir()
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(gather_config(), f, indent=2)
        else:
            try:
                if os.path.exists(CONFIG_FILE):
                    os.remove(CONFIG_FILE)
            except Exception:
                pass  # silent

    def load_last_persisted_config_if_any():
        if not os.path.exists(CONFIG_FILE):
            return
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            if cfg.get("persist_configuration"):
                apply_config(cfg)
        except Exception:
            pass

    def choose_file(var: tk.StringVar, title, filetypes=None):
        filetypes = filetypes or [("All files", "*.*")]
        path = filedialog.askopenfilename(title=title, filetypes=filetypes)
        if path:
            var.set(path)
            update_cards_visibility()

    def entry_row(parent, label_text, text_var: tk.StringVar, browse_cmd):
        row = tk.Frame(parent)
        row.pack(fill="x", pady=4)
        tk.Label(row, text=label_text, width=24, anchor="w").pack(side="left")
        e = tk.Entry(row, textvariable=text_var, state="readonly")
        e.pack(side="left", fill="x", expand=True, padx=(4,8))
        tk.Button(row, text="Browse…", command=browse_cmd).pack(side="left")
        return row

    def update_cards_visibility():
        has_customer = bool(customer_data_path_var.get())
        if has_customer and not cards_row.winfo_manager():
            cards_row.pack(fill="x")
        elif not has_customer and cards_row.winfo_manager():
            generate_cards_var.set(False)
            cards_row.pack_forget()

    def clear_all():
        persist_config_var.set(False)
        delete_reports_var.set(False)
        rpt_path_var.set("")
        txt_path_var.set("")
        unknowns_path_var.set("")
        customer_data_path_var.set("")
        generate_cards_var.set(False)
        generate_pdf_var.set(False)
        update_cards_visibility()

    # ----------------- GUI -----------------
    root = tk.Tk()
    root.title('Run Configuration')
    root.geometry('1000x400')

    # Variables
    persist_config_var = tk.BooleanVar(value=False)
    delete_reports_var = tk.BooleanVar(value=False)
    rpt_path_var = tk.StringVar(value="")
    txt_path_var = tk.StringVar(value="")
    unknowns_path_var = tk.StringVar(value="")
    customer_data_path_var = tk.StringVar(value="")
    generate_cards_var = tk.BooleanVar(value=False)
    generate_pdf_var = tk.BooleanVar(value=False)

    # Header (title on left, info icon on right)
    header = tk.Frame(root)
    header.pack(fill="x", padx=10, pady=(8,0))
    tk.Label(header, text="Run Configuration", font=("Segoe UI", 12, "bold")).pack(side="left")

    def draw_info_icon(canvas):
        w, h = 22, 22
        canvas.configure(width=w, height=h, highlightthickness=0, bg=header.cget("bg"))
        r = 10
        cx, cy = w//2, h//2
        canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="#1e90ff", outline="#1e90ff")
        canvas.create_text(cx, cy+1, text="i", fill="white", font=("Segoe UI", 11, "bold"))

    # Info icon
    info_canvas = tk.Canvas(header, cursor="hand2")
    draw_info_icon(info_canvas)
    info_canvas.pack(side="right")

    # Collapsible info panel (uses a Canvas to animate height)
    info_container = tk.Frame(root)
    info_container.pack(fill="x", padx=10, pady=(0,6))

    info_canvas_panel = tk.Canvas(info_container, height=0, highlightthickness=0, bd=0)
    info_canvas_panel.pack(fill="x")

    # Inner panel content
    panel_frame = tk.Frame(info_canvas_panel, bg="#fff4c2", bd=1, relief="solid")
    panel_text = tk.Label(panel_frame, text=INFO_TEXT, bg="#fff4c2", justify="left", wraplength=640)
    panel_text.pack(side="left", padx=10, pady=10, fill="x", expand=True)

    panel_window = info_canvas_panel.create_window(0, 0, anchor="nw", window=panel_frame)
    info_expanded = False

    def layout_info_panel():
        info_canvas_panel.update_idletasks()
        req_w = info_canvas_panel.winfo_width()
        info_canvas_panel.itemconfig(panel_window, width=req_w)
        panel_frame.update_idletasks()

    info_container.bind("<Configure>", lambda e: layout_info_panel())

    def animate_info(expand=True, step=12):
        nonlocal_vars = {"target": 0}
        layout_info_panel()
        target_h = panel_frame.winfo_reqheight()
        current_h = info_canvas_panel.winfo_height()
        if expand:
            nonlocal_vars["target"] = target_h
            new_h = min(current_h + step, target_h)
        else:
            nonlocal_vars["target"] = 0
            new_h = max(current_h - step, 0)
        info_canvas_panel.configure(height=new_h)
        if (expand and new_h < target_h) or ((not expand) and new_h > 0):
            root.after(10, lambda: animate_info(expand, step))
        else:
            global info_expanded
            info_expanded = expand

    def toggle_info(_event=None):
        animate_info(not info_expanded)

    info_canvas.bind("<Button-1>", toggle_info)

    # Main form area
    frm = tk.Frame(root)
    frm.pack(fill="x", padx=10, pady=10)

    # Persist + Delete
    top_opts = tk.Frame(frm)
    top_opts.pack(fill="x", pady=(0,6))
    tk.Checkbutton(top_opts, text='Persist configuration', variable=persist_config_var).pack(anchor="w")
    tk.Checkbutton(top_opts, text='Delete all current reports', variable=delete_reports_var).pack(anchor="w")

    # File rows
    entry_row(frm, "Phenotype (.rpt):",
              rpt_path_var,
              lambda: choose_file(rpt_path_var, "Select phenotype (.rpt) file",
                                  [("RPT files", "*.rpt"), ("All files", "*.*")]))

    entry_row(frm, "Genotype (.txt):",
              txt_path_var,
              lambda: choose_file(txt_path_var, "Select genotype (.txt) file",
                                  [("Text files", "*.txt"), ("All files", "*.*")]))

    entry_row(frm, "Corrected Unknowns (.xlsx):",
              unknowns_path_var,
              lambda: choose_file(unknowns_path_var, "Select Corrected Unknowns (.xlsx) file",
                                  [("Excel Workbook", "*.xlsx")]))

    entry_row(frm, "Customer Data (.xlsx):",
              customer_data_path_var,
              lambda: choose_file(customer_data_path_var, "Select Customer Data (.xlsx) file",
                                  [("Excel Workbook", "*.xlsx")]))

    # Placeholder directly below Customer Data for 'Generate cards.xlsx'
    after_customer_placeholder = tk.Frame(frm)
    after_customer_placeholder.pack(fill="x", padx=0, pady=(0,0))

    # Generate cards row (child of the placeholder; initially hidden)
    cards_row = tk.Frame(after_customer_placeholder, padx=0, pady=0)
    tk.Checkbutton(cards_row, text='Generate cards.xlsx', variable=generate_cards_var).pack(anchor="w")

    # Options: PDF + warning
    opts = tk.Frame(root)
    opts.pack(fill="x", padx=10, pady=(0,6))
    tk.Checkbutton(opts, text="Generate PDF's", variable=generate_pdf_var).pack(anchor="w")
    tk.Label(opts, text="(Warning! Generating PDF's may take up to 15 minutes.\nYou cannot open Word (.docx) files during this time.)",
             fg='red', justify="left").pack(anchor="w", pady=(2,0))

    # Buttons
    btns = tk.Frame(root)
    btns.pack(fill="x", padx=10, pady=(0,10))

    def do_run():
        # Perform work here, then handle persistence/delete.
        from Main import generation_script
        save_config_if_persist()
        generation_script(
            delete_reports = delete_reports_var.get(),
            phenotype_file = rpt_path_var.get(),
            genotype_file = txt_path_var.get(),
            corrected_unknowns_file = unknowns_path_var.get(),
            customer_data_file = customer_data_path_var.get(),
            generate_cards = generate_cards_var.get(),
            generate_pdf = generate_pdf_var.get()
        )

    def do_clear_all():
        clear_all()

    tk.Button(btns, text="Run", width=12, command=do_run).pack(side="left")
    tk.Button(btns, text="Clear all", width=12, command=do_clear_all).pack(side="left", padx=6)

    # Startup: load persisted + update vis
    load_last_persisted_config_if_any()
    update_cards_visibility()

    root.mainloop()

if __name__ == '__main__':
    mp.freeze_support()
    launch_gui()