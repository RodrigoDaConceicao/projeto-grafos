import time
import tkinter as tk
from tkinter import ttk
from puzzles import PUZZLES, get_puzzle

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
        self._on_new_game()  

    def _build_interface(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        self._build_grid(main_frame)

        side_panel = ttk.Frame(self.root, padding="10")
        side_panel.grid(row=0, column=1, sticky="N")

        ttk.Label(side_panel, text="Dificuldade:").pack(fill='x', pady=(0, 2))
        self.difficulty_var = tk.StringVar()
        difficulty_combo = ttk.Combobox(side_panel, textvariable=self.difficulty_var, state="readonly")
        difficulty_combo['values'] = [key.capitalize() for key in PUZZLES.keys()]
        self.difficulty_var.set("Facil")
        difficulty_combo.pack(fill='x', pady=(0, 10))
        
        ttk.Button(side_panel, text="Novo Jogo", command=self._on_new_game).pack(fill='x', pady=5)
        
        ttk.Separator(side_panel, orient='horizontal').pack(fill='x', pady=10)

        solver_options = self.graph.get_solver_options()
        self.solver_map = {display: name for display, name in solver_options}
        solver_display_names = list(self.solver_map.keys())

        ttk.Label(side_panel, text="Solver Algorithm:").pack(fill='x')
        self.solver_var = tk.StringVar()
        solver_combo = ttk.Combobox(side_panel, textvariable=self.solver_var, state="readonly")
        solver_combo['values'] = solver_display_names
        if solver_display_names:
            self.solver_var.set(solver_display_names[-1]) 
        solver_combo.pack(fill='x', pady=(0, 10))

        ttk.Button(side_panel, text="Solve", command=self._on_solve).pack(fill='x', pady=5)
        self.edit_button = ttk.Button(side_panel, text="Edit", command=self._on_toggle_edit)
        self.edit_button.pack(fill='x', pady=5)
        ttk.Button(side_panel, text="Clear", command=self._on_clear).pack(fill='x', pady=5)

        self.status_label = ttk.Label(side_panel, text="", wraplength=180, anchor="center", justify="center")
        self.status_label.pack(fill='x', pady=10)

    def _build_grid(self, parent):
        for row in range(self.size):
            for col in range(self.size):
                entry = tk.Entry(parent, width=2, font=('Arial', 18), justify='center')
                entry.grid(row=row, column=col, padx=1, pady=1, ipadx=5, ipady=5)
                
                entry.bind("<FocusIn>", self._on_focus)
                entry.bind("<Key>", lambda e, ent=entry: self._on_keypress(e, ent))
                
                padx, pady = (1, 1), (1, 1)
                if col % self.dimension == 0: padx = (4, 1)
                if row % self.dimension == 0: pady = (4, 1)
                entry.grid_configure(padx=padx, pady=pady)
                
                self.entries[(row, col)] = entry

    def _on_focus(self, event):
        event.widget._typed = False

    def _on_keypress(self, event, entry):
        if entry['state'] == 'disabled':
            return "break"

        if event.keysym == 'BackSpace':
            entry.delete(0, tk.END)
            self._update_graph_from_entry(entry)
            return "break"
        
        if not event.char.isdigit() or event.char == '0':
            return "break"

        if not getattr(entry, '_typed', False):
            entry.delete(0, tk.END)
            entry._typed = True

        entry.insert(tk.END, event.char)
        self._update_graph_from_entry(entry)
        return "break"

    def _on_new_game(self):
        difficulty = self.difficulty_var.get().lower()
        puzzle_string = get_puzzle(difficulty)
        self.graph.load_from_string(puzzle_string)
        self._update_grid_from_graph()
        self.status_label.config(text=f"Novo jogo {difficulty.capitalize()} carregado.")

    def _on_solve(self):
        display_name = self.solver_var.get()
        method_name = self.solver_map.get(display_name)
        solver_func = getattr(self.graph, method_name, None)

        if not callable(solver_func):
            self.status_label.config(text=f"Erro: Solver '{method_name}' não encontrado.")
            return

        start_time = time.time()
        solved = solver_func()
        elapsed = time.time() - start_time

        if solved:
            self.status_label.config(text=f"'{display_name}'\nresolvido em {elapsed:.4f} sec.")
        else:
            self.status_label.config(text=f"'{display_name}' falhou.\nTempo: {elapsed:.4f} sec.")
        
        self._update_grid_from_graph()

    def _on_clear(self):
        for (row, col), vertex in self.graph.vertices.items():
            if not vertex.locked:
                self.graph.set_color(row, col, 0)
        self._update_grid_from_graph()
        self.status_label.config(text="Células do usuário limpas.")

    def _on_toggle_edit(self):
        self.edit = not self.edit
        self.edit_button.config(text="Save" if self.edit else "Edit")

    def _update_graph_from_entry(self, entry):
        for (row, col), e in self.entries.items():
            if e == entry:
                text = entry.get().strip()
                val = int(text) if text.isdigit() else 0
                
                self.graph.set_color(row, col, val)
                
                if val != 0 and not self.graph.is_cell_valid(row, col):
                    entry.config(fg="red")
                else:
                    entry.config(fg="blue")
                break

    def _update_grid_from_graph(self):
        for (row, col), entry in self.entries.items():
            vertex = self.graph.get_vertex(row, col)

            entry.config(state='normal')

            entry.delete(0, tk.END)
            if vertex.color != 0:
                entry.insert(0, str(vertex.color))

            if vertex.locked:
                entry.config(fg='black', state='disabled', disabledbackground="#D3D3D3", disabledforeground='black')
            else:
                if vertex.color == 0:
                    entry.config(fg='blue')
                else:
                    if self.graph.is_cell_valid(row, col):
                        entry.config(fg='blue')
                    else:
                        entry.config(fg='red')

        self.root.update_idletasks()

    def run(self):
        """Inicia o loop principal da aplicação tkinter."""
        self.root.mainloop()