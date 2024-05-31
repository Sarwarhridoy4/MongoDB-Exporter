import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pymongo import MongoClient
from bson.json_util import dumps

def export_collections_to_json(uri, db_name, output_dir, progress_label):
    try:
        # Create the output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Connect to MongoDB
        client = MongoClient(uri)
        db = client[db_name]

        # List all collections in the database
        collections = db.list_collection_names()
        total_collections = len(collections)

        if total_collections == 0:
            progress_label.config(text="No collections found in the database.")
            return

        for index, collection_name in enumerate(collections):
            collection = db[collection_name]

            # Check if the collection is empty
            if collection.count_documents({}) > 0:
                # Calculate the percentage completed
                percentage = ((index + 1) / total_collections) * 100
                progress_label.config(text=f"Exporting: {collection_name}.json ({percentage:.2f}%)")
                progress_label.update_idletasks()

                # Export collection to JSON
                with open(os.path.join(output_dir, f"{collection_name}.json"), "w") as file:
                    cursor = collection.find()
                    file.write(dumps(cursor, indent=4))

        # Close the connection
        client.close()
        progress_label.config(text="Export completed successfully!")
        messagebox.showinfo("Success", "Export completed successfully!")
    except Exception as e:
        progress_label.config(text="Error occurred!")
        messagebox.showerror("Error", f"An error occurred: {e}")

def browse_output_dir():
    directory = filedialog.askdirectory()
    if directory:
        output_dir_entry.delete(0, tk.END)
        output_dir_entry.insert(0, directory)

def start_export():
    uri = uri_entry.get()
    db_name = db_name_entry.get()
    output_dir = output_dir_entry.get()

    if not uri or not db_name or not output_dir:
        messagebox.showerror("Error", "All fields are required!")
    else:
        export_collections_to_json(uri, db_name, output_dir, progress_label)

# GUI setup
root = tk.Tk()
root.title("MongoDB Exporter")
root.geometry("500x500")

# Apply a modern theme
style = ttk.Style()
style.theme_use('clam')

# Customize styles
style.configure('TLabel', font=('Helvetica', 12))
style.configure('TEntry', font=('Helvetica', 12))
style.configure('TButton', font=('Helvetica', 12), padding=5)
style.configure('TFrame', padding=10)

frame = ttk.Frame(root)
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)

# URI
ttk.Label(frame, text="MongoDB URI:").grid(row=0, column=0, sticky=tk.W, pady=5)
uri_entry = ttk.Entry(frame, width=50)
uri_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

# Database Name
ttk.Label(frame, text="Database Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
db_name_entry = ttk.Entry(frame, width=50)
db_name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))

# Output Directory
ttk.Label(frame, text="Output Directory:").grid(row=2, column=0, sticky=tk.W, pady=5)
output_dir_entry = ttk.Entry(frame, width=50)
output_dir_entry.grid(row=2, column=1, sticky=(tk.W, tk.E))

# Buttons Frame
buttons_frame = ttk.Frame(frame)
buttons_frame.grid(row=3, column=1, sticky=tk.E, pady=10)

# Browse Button
browse_button = ttk.Button(buttons_frame, text="Browse", command=browse_output_dir)
browse_button.grid(row=0, column=0, sticky=tk.W, padx=(0, 5))

# Export Button
export_button = ttk.Button(buttons_frame, text="Export", command=start_export)
export_button.grid(row=0, column=1, sticky=tk.W)

# Progress Label
progress_label = ttk.Label(frame, text="Progress: ")
progress_label.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

# Adjust column weights for resizing
frame.columnconfigure(1, weight=1)

# Run the GUI event loop
root.mainloop()
