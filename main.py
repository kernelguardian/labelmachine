import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
import sys
import threading
from gserver import run_flask

from utils import (
    get_data_by_barcodes,
    clear_scans_data,
    get_scanned_barcodes,
    get_all_tree_data,
    generate_barcode_labels_pdf,
    get_ip_address,
)

try:
    wd = sys._MEIPASS
except AttributeError:
    wd = os.getcwd()

df = pd.DataFrame()
server_process = None
original_df = pd.DataFrame()


def upload_file():
    global df, original_df
    filetypes = [("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv")]
    filepath = filedialog.askopenfilename(filetypes=filetypes)

    if filepath:
        try:
            if filepath.endswith(".xlsx"):
                df = pd.read_excel(filepath, engine="openpyxl")
            elif filepath.endswith(".xls"):
                df = pd.read_excel(filepath, engine="xlrd")
            elif filepath.endswith(".csv"):
                df = pd.read_csv(filepath)
            else:
                raise ValueError(
                    "Unsupported file format. Please select an Excel or CSV file."
                )

            if df.empty:
                raise ValueError(
                    "The selected file is empty or not a valid Excel/CSV file."
                )

            original_df = df.copy()  # Store a copy of the original DataFrame
            display_data(df)
        except ValueError as ve:
            messagebox.showerror("File Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Could not read the file:\n{e}")
    else:
        messagebox.showwarning("No File", "No file was selected")


def display_data(dataframe):
    for widget in root.winfo_children():
        widget.destroy()

    top_frame = tk.Frame(root, height=50)
    top_frame.pack(fill=tk.X, padx=5, pady=5)

    search_label = tk.Label(top_frame, text="Search:")
    search_label.pack(side=tk.LEFT, padx=5)

    search_entry = tk.Entry(top_frame)
    search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

    search_button = tk.Button(
        top_frame,
        text="Search",
        command=lambda: search_data(search_entry.get(), dataframe),
    )
    search_button.pack(side=tk.LEFT, padx=5)

    reset_button = tk.Button(
        top_frame,
        text="Reset",
        command=lambda: reset_search(search_entry),
    )
    reset_button.pack(side=tk.LEFT, padx=5)

    label_button = tk.Button(
        top_frame, text="Start Labeling", command=lambda: start_labeling(dataframe)
    )
    label_button.pack(side=tk.LEFT, padx=5)

    start_server_button = tk.Button(
        top_frame,
        text="Start Server",
        command=lambda: toggle_server(start_server_button),
    )
    start_server_button.pack(side=tk.LEFT, padx=5)

    clear_scans_button = tk.Button(top_frame, text="Clear Scans", command=clear_scans)
    clear_scans_button.pack(side=tk.LEFT, padx=5)

    tree_frame = tk.Frame(root)
    tree_frame.pack(fill=tk.BOTH, expand=True)

    tree = ttk.Treeview(tree_frame)
    tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

    y_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
    y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.config(yscrollcommand=y_scrollbar.set)

    x_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=tree.xview)
    x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    tree.config(xscrollcommand=x_scrollbar.set)

    if not dataframe.empty:
        tree["column"] = list(dataframe.columns)
        tree["show"] = "headings"

        for column in tree["column"]:
            tree.heading(column, text=column)
            tree.column(column, width=100, minwidth=100, anchor=tk.W)

        for row in dataframe.itertuples(index=False):
            tree.insert("", tk.END, values=row)


def search_data(query, dataframe):
    queries = query.split()
    filtered_df = dataframe[
        dataframe.apply(
            lambda row: any(
                all(keyword.lower() in str(value).lower() for keyword in queries)
                for value in row
            ),
            axis=1,
        )
    ]
    highlight_matches(filtered_df, query)
    display_data(filtered_df)


def reset_search(search_entry):
    search_entry.delete(0, tk.END)
    display_data(original_df)


def highlight_matches(dataframe, query):
    queries = query.split()
    for i, row in dataframe.iterrows():
        for column in dataframe.columns:
            for keyword in queries:
                if keyword.lower() in str(row[column]).lower():
                    # Add your logic to highlight the cell or row
                    # This can be done using tags or custom styling
                    pass


def on_print_labels_button_click(tree):
    tree_data = get_all_tree_data(tree)
    output_filename = "product_list.pdf"

    file_path = filedialog.asksaveasfilename(
        initialfile=output_filename,
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
    )

    if file_path:
        try:
            generate_barcode_labels_pdf(tree_data, file_path)
            messagebox.showinfo(
                "Save Successful", f"PDF saved successfully to:\n{file_path}"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save PDF:\n{e}")


def start_labeling(dataframe):
    labeling_window = tk.Toplevel(root)
    labeling_window.title("Start Labeling")
    labeling_window.geometry("1200x600")

    barcode_frame = tk.Frame(labeling_window)
    barcode_frame.pack(fill=tk.X, padx=5, pady=5)

    barcode_label = tk.Label(barcode_frame, text="Barcode:")
    barcode_label.pack(side=tk.LEFT, padx=5)

    barcode_entry = tk.Entry(barcode_frame)
    barcode_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

    print_labels_button = tk.Button(
        barcode_frame,
        text="Print Labels",
        command=lambda: on_print_labels_button_click(tree),
    )
    print_labels_button.pack(side=tk.LEFT, padx=5)

    tree_frame = tk.Frame(labeling_window)
    tree_frame.pack(fill=tk.BOTH, expand=True)

    columns = ["ID", "Name", "Sale price", "Barcode", "Stock Count"]
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
    tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

    tree.heading("ID", text="ID")
    tree.column("ID", width=50, anchor=tk.CENTER)

    y_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
    y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.config(yscrollcommand=y_scrollbar.set)

    for column in columns:
        tree.heading(column, text=column)
        tree.column(column, anchor=tk.W)

    scanned_barcodes = get_data_by_barcodes(dataframe, get_scanned_barcodes())

    for item in scanned_barcodes:
        tree.insert("", tk.END, values=item)


def start_server():
    global server_process
    try:
        flask_thread = threading.Thread(target=run_flask)
        flask_thread.daemon = True
        flask_thread.start()

        ip_address = get_ip_address()

        if ip_address:
            messagebox.showinfo(
                "Server Started",
                "Flask server started successfully!\n" + ip_address + ":5001/scans",
            )

    except Exception as e:
        messagebox.showerror("Error", f"Failed to start server: {e}")


def stop_server():
    global server_process
    if server_process:
        server_process.terminate()
        server_process = None
        messagebox.showinfo("Server Stopped", "Flask server stopped successfully!")


def toggle_server(button):
    if button["text"] == "Start Server":
        start_server()
        button["text"] = "Stop Server"
    else:
        stop_server()
        button["text"] = "Start Server"


def clear_scans():
    clear_scans_data()
    messagebox.showinfo("Clear Scans", "Scans data cleared successfully!")


root = tk.Tk()
root.title("Grocerhut Label Gen")
root.geometry("800x600")
root.state("zoomed")

upload_button = tk.Button(root, text="Upload Excel or CSV File", command=upload_file)
upload_button.pack(expand=True)

root.mainloop()
