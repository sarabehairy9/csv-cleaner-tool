import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import matplotlib.pyplot as plt
import os

def toggle_all():
    new_state = check_all.get()
    for var in all_options:
        var.set(new_state)

def clean_file():
    files = []
    if merge_files.get():
        files = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")])
        if not files:
            return
        df_list = [pd.read_csv(f) for f in files]
        df = pd.concat(df_list, ignore_index=True)
    else:
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        df = pd.read_csv(file_path)

    try:
        if remove_empty_rows.get():
            df.dropna(how='all', inplace=True)
        if remove_empty_cols.get():
            df.dropna(axis=1, how='all', inplace=True)
        if clean_colnames.get():
            df.columns = df.columns.str.strip()
        if trim_text_cells.get():
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].map(lambda x: x.strip() if isinstance(x, str) else x)

        if format_dates.get() or highlight_dates.get() or drop_invalid_dates.get():
            for col in df.columns:
                if df[col].dtype == 'object' and "date" in col.lower():
                    parsed = pd.to_datetime(df[col], errors="coerce")
                    if highlight_dates.get():
                        df["Parsed " + col] = parsed
                    if format_dates.get():
                        df[col] = parsed
                    if drop_invalid_dates.get():
                        df = df[~parsed.isna()]

        if sort_data.get():
            sort_column = simpledialog.askstring("Sort", "Enter column name to sort by:")
            if sort_column and sort_column in df.columns:
                df.sort_values(by=sort_column, inplace=True)

        if generate_chart.get():
            num_cols = df.select_dtypes(include='number').columns.tolist()
            if len(num_cols) >= 2:
                plt.figure(figsize=(8,5))
                plt.plot(df[num_cols[0]], df[num_cols[1]], marker='o')
                plt.title(f"{num_cols[1]} vs {num_cols[0]}")
                plt.xlabel(num_cols[0])
                plt.ylabel(num_cols[1])
                plt.grid(True)
                chart_path = os.path.join(os.path.expanduser("~"), "chart_output.png")
                plt.savefig(chart_path)
                messagebox.showinfo("Chart Saved", f"Chart saved to {chart_path}")

        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if save_path:
            df.to_csv(save_path, index=False)
            messagebox.showinfo("Success", "Cleaned file saved successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong:\n{e}")

# --- GUI ---
root = tk.Tk()
root.title("Excel/CSV Cleaner Tool")
root.geometry("450x650")

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Select cleaning options:", font=("Arial", 12, "bold")).pack(anchor="w")

remove_empty_rows = tk.BooleanVar(value=True)
remove_empty_cols = tk.BooleanVar(value=True)
clean_colnames = tk.BooleanVar(value=True)
trim_text_cells = tk.BooleanVar(value=True)
format_dates = tk.BooleanVar(value=False)
highlight_dates = tk.BooleanVar(value=False)
drop_invalid_dates = tk.BooleanVar(value=False)
merge_files = tk.BooleanVar(value=False)
sort_data = tk.BooleanVar(value=False)
generate_chart = tk.BooleanVar(value=False)

all_options = [
    remove_empty_rows, remove_empty_cols, clean_colnames,
    trim_text_cells, format_dates, highlight_dates,
    drop_invalid_dates, merge_files, sort_data, generate_chart
]

check_all = tk.BooleanVar(value=False)

# Option checkboxes

checkbuttons = [
    ("Remove empty rows", remove_empty_rows),
    ("Remove empty columns", remove_empty_cols),
    ("Trim spaces from column names", clean_colnames),
    ("Trim spaces in text cells", trim_text_cells),
    ("Format date columns", format_dates),
    ("Highlight parsed date column", highlight_dates),
    ("Remove rows with invalid dates", drop_invalid_dates),
    ("Merge multiple CSV files", merge_files),
    ("Sort data by column", sort_data),
    ("Auto-generate chart (1st 2 numeric columns)", generate_chart)
]

for text, var in checkbuttons:
    tk.Checkbutton(frame, text=text, variable=var).pack(anchor="w")

# Check/Uncheck All at the end

tk.Checkbutton(frame, text="Check/Uncheck All", variable=check_all, command=toggle_all).pack(anchor="w")

tk.Button(root, text="Select CSV and Clean", command=clean_file, font=("Arial", 12), bg="#4CAF50", fg="white").pack(pady=20)

root.mainloop()
