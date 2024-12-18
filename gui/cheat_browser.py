# gui/cheat_browser.py
import tkinter as tk
from tkinter import ttk, scrolledtext
from utils.cheat_utils import load_cheats, parse_cheats, search_games, search_cheats

def populate_treeview(treeview, cheats_data):
    """Populates the Treeview with game and cheat data."""
    treeview.delete(*treeview.get_children())  # Clear existing items

    for game_id, game_info in cheats_data.items():
        game_name = game_info['name']
        game_item = treeview.insert('', 'end', text=f"{game_name} ({game_id})", open=True)

        for folder in game_info['folders']:
            folder_name = folder['folder_name']
            folder_item = treeview.insert(game_item, 'end', text=folder_name, open=False)

            for cheat in folder['cheats']:
                cheat_name = cheat['name']
                cheat_notes = cheat['notes']
                cheat_codes = cheat['codes']
                treeview.insert(folder_item, 'end', text=cheat_name, values=(cheat_notes, cheat_codes))

def on_treeview_select(event, notes_text, codes_text, treeview):
    """Displays cheat notes and codes when a cheat is selected."""
    try:
        item = treeview.selection()[0]
        values = treeview.item(item)['values']
        if values:  # Check if it's a cheat item (has values)
            notes_text.delete("1.0", tk.END)
            notes_text.insert(tk.END, values[0])
            codes_text.delete("1.0", tk.END)
            codes_text.insert(tk.END, values[1])
        else:
            notes_text.delete("1.0", tk.END)
            codes_text.delete("1.0", tk.END)

    except IndexError:
        pass  # Handles when nothing is selected

# Main application
root = tk.Tk()
root.title("NDS Cheat Database Browser")

# Load and parse cheats
cheat_data_xml = load_cheats("/path/to/your/cheats.xml")  # Update the path accordingly
cheat_data = parse_cheats(cheat_data_xml)

# Treeview widget
treeview = ttk.Treeview(root, columns=("Notes", "Codes"), show="tree headings")
treeview.heading("#0", text="Cheats")
treeview.column("#0", width=300)
treeview.column("Notes", width=200)
treeview.column("Codes", width=200)
treeview.pack(fill=tk.BOTH, expand=True)

# Search Entry and Button
search_var = tk.StringVar()
search_entry = tk.Entry(root, textvariable=search_var)
search_entry.pack()

def search_callback():
    search_term = search_var.get()
    filtered_cheats = search_games(cheat_data, search_term)
    populate_treeview(treeview, filtered_cheats)

search_button = tk.Button(root, text="Search Games", command=search_callback)
search_button.pack()

# Cheat search entry and button
cheat_search_var = tk.StringVar()
cheat_search_entry = tk.Entry(root, textvariable=cheat_search_var)
cheat_search_entry.pack()

def cheat_search_callback():
    selected = treeview.selection()
    if selected:
        item = selected[0]
        # Determine if the selected item is a game
        parent = treeview.parent(item)
        if not parent:  # It's a game
            game_text = treeview.item(item)['text']
            game_id = game_text.split('(')[-1].strip(')')
            search_term = cheat_search_var.get()
            filtered_game = search_cheats(cheat_data, game_id, search_term)
            populate_treeview(treeview, {game_id: filtered_game})
        else:
            # Optionally, handle searches within folders or cheats
            pass

cheat_search_button = tk.Button(root, text="Search Cheats", command=cheat_search_callback)
cheat_search_button.pack()

# Text areas for notes and codes
notes_label = tk.Label(root, text="Notes:")
notes_label.pack()
notes_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=5)
notes_text.pack(fill=tk.X)

codes_label = tk.Label(root, text="Codes:")
codes_label.pack()
codes_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=5)
codes_text.pack(fill=tk.X)

# Bind treeview selection
treeview.bind("<<TreeviewSelect>>", lambda event: on_treeview_select(event, notes_text, codes_text, treeview))

populate_treeview(treeview, cheat_data)

root.mainloop()
