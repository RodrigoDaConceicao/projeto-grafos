import time
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
        self.edit = False

        self._build_interface()

        self.update_lock()

    def _build_interface(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0)

        # Grid
        self._build_grid(main_frame)

        # Side panel
        side_panel = ttk.Frame(self.root, padding="10")
        side_panel.grid(row=0, column=1, sticky="N")

        # Solver mapping and dropdown
        solver_options = self.graph.get_solver_options()
        self.solver_map = {display: name for display, name in solver_options}
        solver_display_names = list(self.solver_map.keys())

        ttk.Label(side_panel, text="Solver Algorithm:").pack(fill='x')
        self.solver_var = tk.StringVar()
        self.solver_combo = ttk.Combobox(side_panel, textvariable=self.solver_var, state="readonly")
        self.solver_combo['values'] = solver_display_names
        if solver_display_names:
            self.solver_var.set(solver_display_names[0])
        self.solver_combo.pack(fill='x', pady=(0, 10))

        ttk.Button(side_panel, text="Solve", command=self._on_solve).pack(fill='x', pady=5)
        self.edit_button = ttk.Button(side_panel, text="Save" if self.edit else "Edit", command=self._on_toggle_edit)
        self.edit_button.pack(fill='x', pady=5)
        ttk.Button(side_panel, text="Clear", command=self._on_clear).pack(fill='x', pady=5)

        # Status label (below buttons)
        self.status_label = ttk.Label(side_panel, text="", wraplength=180, anchor="center", justify="center")
        self.status_label.pack(fill='x', pady=10)

    def _build_grid(self, parent):
        for row in range(self.size):
            for col in range(self.size):
                value = self.graph.get_vertex(row, col).color
                entry = tk.Entry(parent, width=2, font=('Arial', 18), justify='center')
                entry.grid(row=row, column=col, padx=1, pady=1, ipadx=5, ipady=5)
                if value != 0:
                    entry.insert(0, str(value))
                else:
                    entry.insert(0, "")

                entry.bind("<FocusIn>", self._on_focus)
                entry.bind("<Key>", lambda e, ent=entry: self._on_keypress(e, ent))
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
            self._update_graph_from_entry(entry)
            return "break"  # Prevent default backspace behavior
        if not char.isdigit() or (char == '0' and entry.get() == ""):
            return "break"  # Ignore non-digit or '0'
        
        current_text = entry.get()

        # If this is the first typed character after focus, treat as a fresh value
        new_text = char if not getattr(entry, '_typed', False) else current_text + char

        # Check if new value exceeds max allowed
        try:
            if int(new_text) > max_value:
                return "break"
        except ValueError:
            return "break"

        if not getattr(entry, '_typed', False):
            entry.delete(0, tk.END)
            entry._typed = True  # Now mark as typed
        
        # Insert char manually since we're overriding default behavior
        entry.insert(tk.END, char)
        if self.edit: 
            entry.config(fg='black')
        else:
            entry.config(fg='blue')
        self._update_graph_from_entry(entry)

        return "break"  # Stop default event so it doesn't double type

    def _on_solve(self):

        # Get selected solver method
        display_name = self.solver_var.get()
        method_name = self.solver_map.get(display_name)
        solver_func = getattr(self.graph, method_name, None)
        if not callable(solver_func):
            self.status_label.config(text=f"Invalid solver: {method_name}")
            return

        start_time = time.time()
        solved = solver_func()
        elapsed = time.time() - start_time

        if solved:
            self.status_label.config(text=f"{display_name} solved in {elapsed:.4f} sec")
            for (row, col), entry in self.entries.items():
                vertex = self.graph.get_vertex(row, col)
                if not vertex.locked:
                    entry.delete(0, tk.END)
                    entry.insert(0, str(vertex.color))
                    entry.config(fg='blue')  # User-filled / solver-filled
        else:
            self.status_label.config(text=f"{display_name} failed\n{elapsed:.4f} sec")

    def _on_toggle_edit(self):
        self.edit = not self.edit
        self.edit_button.config(text="Save" if self.edit else "Edit")

        self.update_lock()

    def update_lock(self):
        for (row, col), entry in self.entries.items():
            if self.graph.get_vertex(row, col).locked:
                if self.edit:
                    entry.config(state='normal', cursor='xterm')
                else:
                    entry.config(state='disabled', cursor='arrow')

    def _on_clear(self):
        for (row, col), entry in self.entries.items():
            if not self.graph.get_vertex(row, col).locked or self.edit:
                entry.config(state='normal')  # Temporarily unlock to clear
                entry.delete(0, tk.END)
                self.graph.set_color(row, col, 0)

    def _update_graph_from_entry(self, entry):
        for (row, col), e in self.entries.items():
            if e == entry:
                text = entry.get().strip()
                if text == "":
                    self.graph.set_color(row, col, 0, self.edit)
                else:
                    try:
                        val = int(text)
                        if 1 <= val <= self.size:
                            self.graph.set_color(row, col, val, self.edit)
                            if not self.graph.is_cell_valid(row, col):
                                entry.config(fg="red")
                        else:
                            self.graph.set_color(row, col, 0, self.edit)
                    except ValueError:
                        self.graph.set_color(row, col, 0, self.edit)
                break

    def run(self):
        self.root.mainloop()
