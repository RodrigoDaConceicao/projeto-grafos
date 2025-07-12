import tkinter as tk
from tkinter import ttk

class Window:
    def __init__(self, sudoku_graph):
        self.graph = sudoku_graph
        self.dimension = sudoku_graph.dimension
        self.size = sudoku_graph.size
        self.root = tk.Tk()
        self.root.title("Sudoku Viewer")
        self.entries = {}
        self.locked = True

        self._build_interface()

    def _build_interface(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0)

        # Grid
        self._build_grid(main_frame)

        # Side panel
        side_panel = ttk.Frame(self.root, padding="10")
        side_panel.grid(row=0, column=1, sticky="N")

        ttk.Button(side_panel, text="Solve", command=self._on_solve).pack(fill='x', pady=5)
        self.lock_button = ttk.Button(side_panel, text="Unlock", command=self._on_toggle_lock)
        self.lock_button.pack(fill='x', pady=5)
        ttk.Button(side_panel, text="Clear", command=self._on_clear).pack(fill='x', pady=5)

    def _build_grid(self, parent):

        for row in range(self.size):
            for col in range(self.size):
                value = self.graph.get_vertex(row, col).color
                entry = tk.Entry(parent, width=2, font=('Arial', 18), justify='center')
                entry.grid(row=row, column=col, padx=1, pady=1, ipadx=5, ipady=5)
                if value != 0:
                    entry.insert(0, str(value))
                    entry.config(state='disabled', cursor='arrow')
                else:
                    entry.insert(0, "")

                entry.bind("<FocusIn>", self._on_focus)
                entry.bind("<Key>", lambda e, ent=entry: self._on_keypress(e, ent))
                entry.bind("<FocusOut>", lambda e, r=row, c=col: self._on_value_changed(e, r, c))
                # Highlight block borders
                entry.config(highlightthickness=2)
                if col % self.dimension == 0:
                    entry.grid_configure(padx=(4, 1))
                if row % self.dimension == 0:
                    entry.grid_configure(pady=(4, 1))
                entry.config(insertbackground=entry.cget("bg"))
                self.entries[(row, col)] = entry
    
    def _on_focus(self, event):
        widget = event.widget
        widget._typed = False  # Flag to indicate whether user has typed after focus

    def _on_keypress(self, event, entry):
        char = event.char
        keysym = event.keysym
        max_value = self.size

        if keysym == 'BackSpace':
            entry.delete(0, tk.END)
            return "break"  # Prevent default backspace behavior
        if not char.isdigit() or (char == '0' and entry.get() == ""):
            return "break"  # Ignore non-digit or '0'
        
        current_text = entry.get()

        # If this is the first typed character after focus, treat as a fresh value
        if not getattr(entry, '_typed', False):
            new_text = char
        else:
            new_text = current_text + char

        # Check if new value exceeds max allowed
        try:
            if int(new_text) > max_value:
                return "break"
        except ValueError:
            return "break"

        if not getattr(entry, '_typed', False):
            entry.delete(0, tk.END)
            entry._typed = True  # Now mark as typed

    def _on_solve(self):
        print("Solve button pressed (logic not implemented yet)")

    def _on_toggle_lock(self):
        self.locked = not self.locked
        self.lock_button.config(text="Unlock" if self.locked else "Lock")

        for (row, col), entry in self.entries.items():
            if self.graph.get_vertex(row, col).color != 0:
                if self.locked:
                    entry.config(state='disabled', cursor='arrow')
                else:
                    entry.config(state='normal', cursor='xterm')

    def _on_clear(self):
        for (row, col), entry in self.entries.items():
            if self.graph.get_vertex(row, col).color != 0:
                entry.config(state='normal')  # Temporarily unlock to clear
                entry.delete(0, tk.END)
                if self.locked:
                    entry.config(state='disabled')

    def _on_value_changed(self, event, row, col):
        entry = event.widget
        text = entry.get().strip()

        if text == "":
            self.graph.set_color(row, col, 0)
        else:
            try:
                value = int(text)
                if 1 <= value <= self.size:
                    self.graph.set_color(row, col, value)
                else:
                    entry.delete(0, tk.END)
                    self.graph.set_color(row, col, 0)
            except ValueError:
                entry.delete(0, tk.END)
                self.graph.set_color(row, col, 0)

    def run(self):
        self.root.mainloop()
