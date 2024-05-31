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

        for collection_name in collections:
            collection = db[collection_name]

            # Check if the collection is empty
            if collection.count_documents({}) > 0:
                progress_label.config(text=f"Exporting: {collection_name}.json")
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

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# URI
ttk.Label(frame, text="MongoDB URI:").grid(row=0, column=0, sticky=tk.W)
uri_entry = ttk.Entry(frame, width=50)
uri_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

# Database Name
ttk.Label(frame, text="Database Name:").grid(row=1, column=0, sticky=tk.W)
db_name_entry = ttk.Entry(frame, width=50)
db_name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))

# Output Directory
ttk.Label(frame, text="Output Directory:").grid(row=2, column=0, sticky=tk.W)
output_dir_entry = ttk.Entry(frame, width=50)
output_dir_entry.grid(row=2, column=1, sticky=(tk.W, tk.E))

# Browse Button
browse_button = ttk.Button(frame, text="Browse", command=browse_output_dir)
browse_button.grid(row=2, column=2, sticky=tk.W)

# Export Button
export_button = ttk.Button(frame, text="Export", command=start_export)
export_button.grid(row=3, column=1, pady=10, sticky=tk.E)

# Progress Label
progress_label = ttk.Label(frame, text="Progress: ")
progress_label.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E))

# Adjust column weights for resizing
frame.columnconfigure(1, weight=1)

# Run the GUI event loop
root.mainloop()
