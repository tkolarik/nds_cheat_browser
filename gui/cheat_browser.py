# gui/cheat_browser.py

import sys
import os
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import logging

# Adjust the module search path to include the parent directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.cheat_utils import load_cheats, parse_cheats, search_games, search_cheats
from utils.generate_gameid import generate_gameid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s',
    handlers=[
        logging.FileHandler("cheat_browser.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CheatBrowserGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NDS Cheat Browser GUI")
        self.root.geometry("1000x700")
        
        # Initialize variables
        self.cheat_data = {}
        self.current_gameid = ""
        
        # Setup GUI components
        self.setup_widgets()
        
        # Load and parse cheats data
        self.load_cheats_data()

    def setup_widgets(self):
        """Sets up the GUI components."""
        # Frame for ROM Selection and Loading
        rom_frame = ttk.LabelFrame(self.root, text="ROM Operations")
        rom_frame.pack(pady=10, padx=10, fill='x')
        
        rom_label = ttk.Label(rom_frame, text="Select NDS ROM:")
        rom_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        self.rom_path_var = tk.StringVar()
        rom_entry = ttk.Entry(rom_frame, textvariable=self.rom_path_var, width=70, state='readonly')
        rom_entry.grid(row=0, column=1, padx=5, pady=5)
        
        browse_button = ttk.Button(rom_frame, text="Browse", command=self.browse_rom)
        browse_button.grid(row=0, column=2, padx=5, pady=5)
        
        load_button = ttk.Button(rom_frame, text="Load Cheats", command=self.load_cheats_from_rom)
        load_button.grid(row=0, column=3, padx=5, pady=5)
        
        # Frame for Search Operations
        search_frame = ttk.LabelFrame(self.root, text="Search Operations")
        search_frame.pack(pady=10, padx=10, fill='x')
        
        # Search Games
        game_search_label = ttk.Label(search_frame, text="Search Games:")
        game_search_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        self.game_search_var = tk.StringVar()
        game_search_entry = ttk.Entry(search_frame, textvariable=self.game_search_var, width=50)
        game_search_entry.grid(row=0, column=1, padx=5, pady=5)
        game_search_entry.bind("<KeyRelease>", self.search_games_event)
        
        search_games_button = ttk.Button(search_frame, text="Search Games", command=self.search_games)
        search_games_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Separator
        separator = ttk.Separator(search_frame, orient='horizontal')
        separator.grid(row=1, column=0, columnspan=4, sticky='ew', pady=10)
        
        # Search Cheats
        cheat_search_label = ttk.Label(search_frame, text="Search Cheats:")
        cheat_search_label.grid(row=2, column=0, padx=5, pady=5, sticky='w')
        
        self.cheat_search_var = tk.StringVar()
        cheat_search_entry = ttk.Entry(search_frame, textvariable=self.cheat_search_var, width=50, state='disabled')
        cheat_search_entry.grid(row=2, column=1, padx=5, pady=5)
        cheat_search_entry.bind("<KeyRelease>", self.search_cheats_event)
        
        search_cheats_button = ttk.Button(search_frame, text="Search Cheats", command=self.search_cheats)
        search_cheats_button.grid(row=2, column=2, padx=5, pady=5)
        
        # Frame for Game Information
        game_info_frame = ttk.Frame(self.root)
        game_info_frame.pack(pady=5, padx=10, fill='x')
        
        self.game_info_var = tk.StringVar()
        game_info_label = ttk.Label(game_info_frame, textvariable=self.game_info_var, font=("Helvetica", 12, "bold"))
        game_info_label.pack()
        
        # Frame for Treeview and Details
        display_frame = ttk.Frame(self.root)
        display_frame.pack(pady=10, padx=10, fill='both', expand=True)
        
        # Treeview for displaying cheats
        tree_frame = ttk.Frame(display_frame)
        tree_frame.pack(side='left', fill='both', expand=True)
        
        self.tree = ttk.Treeview(tree_frame, columns=("Notes", "Codes"), show="tree headings")
        self.tree.heading("#0", text="Cheat Name")
        self.tree.heading("Notes", text="Notes")
        self.tree.heading("Codes", text="Codes")
        
        self.tree.column("#0", width=250, anchor='w')
        self.tree.column("Notes", width=300, anchor='w')
        self.tree.column("Codes", width=300, anchor='w')
        
        self.tree.pack(fill='both', expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
        # Scrollbar for Treeview
        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        tree_scroll.pack(side='right', fill='y')
        
        # Frame for Cheat Details
        details_frame = ttk.Frame(display_frame)
        details_frame.pack(side='right', fill='both', expand=True, padx=10)
        
        # Notes
        notes_label = ttk.Label(details_frame, text="Notes:", font=("Helvetica", 10, "bold"))
        notes_label.pack(anchor='w')
        
        self.notes_text = scrolledtext.ScrolledText(details_frame, height=10, wrap=tk.WORD, state='disabled')
        self.notes_text.pack(fill='both', expand=True)
        
        # Codes
        codes_label = ttk.Label(details_frame, text="Codes:", font=("Helvetica", 10, "bold"))
        codes_label.pack(anchor='w', pady=(10,0))
        
        self.codes_text = scrolledtext.ScrolledText(details_frame, height=10, wrap=tk.WORD, state='disabled')
        self.codes_text.pack(fill='both', expand=True)
        
        # Frame for Copy Buttons
        copy_frame = ttk.Frame(self.root)
        copy_frame.pack(pady=10, padx=10, fill='x')
        
        copy_name_button = ttk.Button(copy_frame, text="Copy Cheat Name", command=self.copy_cheat_name)
        copy_name_button.pack(side='left', padx=5)
        
        copy_codes_button = ttk.Button(copy_frame, text="Copy Cheat Codes", command=self.copy_cheat_codes)
        copy_codes_button.pack(side='left', padx=5)
        
    def load_cheats_data(self):
        """Loads and parses the cheats.xml data."""
        cheats_xml_path = os.path.join(parent_dir, 'data', 'cheats.xml')
        self.cheat_data_xml = load_cheats(cheats_xml_path)
        if not self.cheat_data_xml:
            messagebox.showerror("Error", f"Failed to load or parse '{cheats_xml_path}'. Please check the file.")
            logger.error(f"Failed to load or parse '{cheats_xml_path}'.")
            return
        
        self.cheat_data = parse_cheats(self.cheat_data_xml)
        logger.info("Cheat data loaded and parsed successfully.")
    
    def browse_rom(self):
        """Opens a file dialog to select a .nds ROM file."""
        file_path = filedialog.askopenfilename(
            title="Select NDS ROM",
            filetypes=(("NDS files", "*.nds"), ("All files", "*.*"))
        )
        if file_path:
            self.rom_path_var.set(file_path)
            logger.info(f"Selected ROM: {file_path}")
            # Enable the Load Cheats button if needed
            # Already enabled in the current setup
    
    def load_cheats_from_rom(self):
        """Generates GameID from the selected ROM and loads matching cheats."""
        rom_path = self.rom_path_var.get()
        if not rom_path:
            messagebox.showwarning("No ROM Selected", "Please select a .nds ROM file first.")
            return
        
        if not rom_path.lower().endswith('.nds'):
            messagebox.showerror("Invalid File", "Please select a valid .nds ROM file.")
            return
        
        # Generate GameID
        gameid = generate_gameid(rom_path)
        if not gameid:
            messagebox.showerror("Error", "Failed to generate GameID. Ensure 'ndstool' is installed and the ROM is valid.")
            logger.error("Failed to generate GameID.")
            return
        
        self.current_gameid = gameid
        logger.info(f"Generated GameID: {gameid}")
        
        # Update Game Information
        game_info = self.cheat_data.get(gameid, {})
        if game_info:
            game_name = game_info['name']
            self.game_info_var.set(f"Game: {game_name} (GameID: {gameid})")
            self.display_cheats(gameid)
            logger.info(f"Cheats found for GameID: {gameid}")
            # Enable cheat search if applicable
            # Here, cheat_search_entry is disabled unless a game is loaded
            self.cheat_search_var.set("")
            self.enable_cheat_search()
        else:
            self.game_info_var.set(f"No cheats found for GameID: {gameid}")
            self.tree.delete(*self.tree.get_children())
            self.notes_text.configure(state='normal')
            self.notes_text.delete("1.0", tk.END)
            self.notes_text.configure(state='disabled')
            self.codes_text.configure(state='normal')
            self.codes_text.delete("1.0", tk.END)
            self.codes_text.configure(state='disabled')
            messagebox.showinfo("No Cheats Found", f"No cheats found for GameID: {gameid}")
            logger.info(f"No cheats found for GameID: {gameid}")
            self.disable_cheat_search()
    
    def enable_cheat_search(self):
        """Enables the cheat search entry and button."""
        self.cheat_search_entry = self.cheat_search_var.trace_add('write', self.search_cheats_event)
        # In this setup, the cheat search entry is always enabled after loading a ROM
    
    def disable_cheat_search(self):
        """Disables the cheat search entry and button."""
        self.cheat_search_var.set("")
        # Implementation depends on the GUI setup
    
    def search_games_event(self, event):
        """Optional: Can implement real-time search if desired."""
        pass  # For now, searching is triggered by the button
    
    def search_games(self):
        """Searches for games by name or GameID and displays matching cheats."""
        search_term = self.game_search_var.get().strip()
        if not search_term:
            messagebox.showwarning("Empty Search", "Please enter a search term for games.")
            return
        
        filtered_cheats = search_games(self.cheat_data, search_term)
        if not filtered_cheats:
            messagebox.showinfo("No Results", f"No games found matching '{search_term}'.")
            logger.info(f"No games found matching '{search_term}'.")
            self.tree.delete(*self.tree.get_children())
            self.game_info_var.set("")
            self.notes_text.configure(state='normal')
            self.notes_text.delete("1.0", tk.END)
            self.notes_text.configure(state='disabled')
            self.codes_text.configure(state='normal')
            self.codes_text.delete("1.0", tk.END)
            self.codes_text.configure(state='disabled')
            return
        
        self.current_gameid = ""  # Clear any loaded ROM selection
        self.game_info_var.set(f"Search Results for '{search_term}':")
        self.display_cheats(filtered_cheats)
        logger.info(f"Displayed search results for '{search_term}'.")
    
    def search_cheats_event(self, event):
        """Event handler for cheat search input."""
        search_term = self.cheat_search_var.get().strip()
        if not self.current_gameid:
            return  # Only allow cheat search if a ROM is loaded
        
        self.display_cheats(self.current_gameid, search_term)
    
    def search_cheats(self):
        """Searches within the currently loaded game's cheats."""
        search_term = self.cheat_search_var.get().strip()
        if not self.current_gameid:
            messagebox.showwarning("No Game Loaded", "Please load a ROM to search its cheats.")
            return
        
        self.display_cheats(self.current_gameid, search_term)
        logger.info(f"Searched cheats for GameID: {self.current_gameid} with term '{search_term}'.")
    
    def display_cheats(self, data, search_term=""):
        """
        Displays cheats in the Treeview.
        If data is a string (GameID), display cheats for that game.
        If data is a dict (filtered_cheats from search), display multiple games.
        """
        # Clear existing Treeview
        self.tree.delete(*self.tree.get_children())
        
        if isinstance(data, str):
            # Single GameID
            gameid = data
            game_info = self.cheat_data.get(gameid, {})
            if not game_info:
                logger.warning(f"No game information found for GameID: {gameid}")
                return
            
            # Get filtered cheats if search_term is provided
            if search_term:
                filtered_data = search_cheats(self.cheat_data, gameid, search_term)
                folders = filtered_data.get('folders', [])
            else:
                folders = game_info.get('folders', [])
            
            # Populate Treeview
            for folder in folders:
                folder_name = folder['folder_name']
                folder_id = self.tree.insert('', 'end', text=folder_name, open=False)
                
                for cheat in folder['cheats']:
                    cheat_name = cheat['name']
                    cheat_notes = cheat['notes']
                    cheat_codes = cheat['codes']
                    self.tree.insert(folder_id, 'end', text=cheat_name, values=(cheat_notes, cheat_codes))
        
        elif isinstance(data, dict):
            # Multiple Games (from search)
            for gameid, game_info in data.items():
                game_name = game_info['name']
                game_id_display = f"{game_name} ({gameid})"
                game_item = self.tree.insert('', 'end', text=game_id_display, open=False)
                
                folders = game_info.get('folders', [])
                for folder in folders:
                    folder_name = folder['folder_name']
                    folder_id = self.tree.insert(game_item, 'end', text=folder_name, open=False)
                    
                    for cheat in folder['cheats']:
                        cheat_name = cheat['name']
                        cheat_notes = cheat['notes']
                        cheat_codes = cheat['codes']
                        self.tree.insert(folder_id, 'end', text=cheat_name, values=(cheat_notes, cheat_codes))
        
        logger.debug("Cheats displayed successfully.")
    
    def on_tree_select(self, event):
        """Displays cheat notes and codes when a cheat is selected in the Treeview."""
        selected_item = self.tree.focus()
        if not selected_item:
            return
        
        values = self.tree.item(selected_item, 'values')
        if values:
            cheat_notes, cheat_codes = values
            self.notes_text.configure(state='normal')
            self.notes_text.delete("1.0", tk.END)
            self.notes_text.insert(tk.END, cheat_notes)
            self.notes_text.configure(state='disabled')
            
            self.codes_text.configure(state='normal')
            self.codes_text.delete("1.0", tk.END)
            self.codes_text.insert(tk.END, cheat_codes)
            self.codes_text.configure(state='disabled')
        else:
            # If a folder or game is selected, clear the details
            self.notes_text.configure(state='normal')
            self.notes_text.delete("1.0", tk.END)
            self.notes_text.configure(state='disabled')
            
            self.codes_text.configure(state='normal')
            self.codes_text.delete("1.0", tk.END)
            self.codes_text.configure(state='disabled')
    
    def get_selected_cheat(self):
        """Retrieves the currently selected cheat's name and codes."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a cheat to copy.")
            return None, None
        
        values = self.tree.item(selected_item, 'values')
        if values:
            cheat_name = self.tree.item(selected_item, 'text')
            cheat_codes = values[1]
            return cheat_name, cheat_codes
        else:
            messagebox.showwarning("Invalid Selection", "Please select a cheat, not a folder or game.")
            return None, None
    
    def copy_cheat_name(self):
        """Copies the selected cheat's name to the clipboard."""
        cheat_name, _ = self.get_selected_cheat()
        if cheat_name:
            self.copy_to_clipboard(cheat_name)
            messagebox.showinfo("Copied", f"Cheat name '{cheat_name}' copied to clipboard.")
            logger.info(f"Copied cheat name: {cheat_name}")
    
    def copy_cheat_codes(self):
        """Copies the selected cheat's codes to the clipboard."""
        _, cheat_codes = self.get_selected_cheat()
        if cheat_codes:
            self.copy_to_clipboard(cheat_codes)
            messagebox.showinfo("Copied", "Cheat codes copied to clipboard.")
            logger.info("Copied cheat codes.")
    
    def copy_to_clipboard(self, text):
        """Copies the given text to the system clipboard."""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.root.update()  # Now it stays on the clipboard after the window is closed
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy to clipboard: {e}")
            logger.error(f"Failed to copy to clipboard: {e}")

def main():
    root = tk.Tk()
    app = CheatBrowserGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
