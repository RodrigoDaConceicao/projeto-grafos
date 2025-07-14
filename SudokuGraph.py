import random

class Vertex:
    def __init__(self, row, col, block, color=0, locked=False):
        self.row = row
        self.col = col
        self.block = block
        self.color = color  # 0 means not set
        self.locked = locked
        self.neighbors = set()

    def __repr__(self):
        return f"V({self.row},{self.col}) C:{self.color}"


class SudokuGraph:
    def __init__(self, dimension=3):
        if dimension < 2:
            raise ValueError("Block dimension must be at least 2.")
        self.dimension = dimension
        self.size = dimension ** 2  # Total rows and columns
        self.vertices = {}
        self._build_graph()

    def _get_block_number(self, row, col):
        return (row // self.dimension) * self.dimension + (col // self.dimension)

    def _build_graph(self):
        # Create all vertices
        for row in range(self.size):
            for col in range(self.size):
                block = self._get_block_number(row, col)
                self.vertices[(row, col)] = Vertex(row, col, block)

        # Add edges: neighbors in same row, col or block
        for (r1, c1), v1 in self.vertices.items():
            for (r2, c2), v2 in self.vertices.items():
                if (r1, c1) != (r2, c2):
                    same_row = r1 == r2
                    same_col = c1 == c2
                    same_block = v1.block == v2.block
                    if same_row or same_col or same_block:
                        v1.neighbors.add((r2, c2))

    def get_vertex(self, row, col):
        return self.vertices.get((row, col))

    def set_color(self, row, col, color, locked=False):
        if not (0 <= color <= self.size):
            raise ValueError(f"Color must be between 0 and {self.size}")
        self.vertices[(row, col)].color = color
        self.vertices[(row, col)].locked = locked

    def is_cell_valid(self, row, col):
        vertex = self.get_vertex(row, col)
        return self.is_vertex_valid(vertex)
        
    def is_vertex_valid(self, vertex):
        if vertex.color == 0:
            return True  # Empty cells are considered valid

        for n_row, n_col in vertex.neighbors:
            neighbor = self.get_vertex(n_row, n_col)
            if neighbor.color == vertex.color:
                return False  # Conflict found

        return True  # No conflicts
    
    def is_valid_coloring(self):
        for (row, col), vertex in self.vertices.items():
            if not self.is_vertex_valid(vertex):
                return False
        return True
    
    def get_solver_options(self):
        """Returns a list of (display_name, method_name) tuples."""
        solvers = []
        for name in dir(self):
            if callable(getattr(self, name)) and name.startswith("solve_"):
                display = name[6:]  # remove 'solve_'
                display = ' '.join(word.capitalize() for word in display.split('_'))
                solvers.append((display, name))
        return solvers

    def solve_brute_force(self):
        # Find the next empty cell
        for (row, col), vertex in self.vertices.items():
            if vertex.color == 0:
                for num in range(1, self.size + 1):
                    self.set_color(row, col, num)
                    if self.is_vertex_valid(vertex):
                        if self.solve_brute_force():
                            return True
                    self.set_color(row, col, 0)  # Backtrack
                return False  # No valid number found
        return True  # All cells filled

    def solve_dsatur_backtracking(self):
        
        # --- Parte 1: Encontrar o próximo vértice para colorir usando a lógica DSATUR ---
        
        # Encontra todos os vértices não coloridos
        uncolored_vertices = [v for v in self.vertices.values() if v.color == 0]

        # Caso base da recursão: se não há vértices para colorir, o puzzle está resolvido!
        if not uncolored_vertices:
            return True

        # Lógica de seleção DSATUR para escolher o vértice mais restrito
        best_vertex_to_color = None
        max_saturation = -1
        max_degree = -1

        for vertex in uncolored_vertices:
            # Calcula o grau de saturação
            neighbor_colors = {self.get_vertex(r,c).color for r,c in vertex.neighbors if self.get_vertex(r,c).color != 0}
            current_saturation = len(neighbor_colors)
            current_degree = len(vertex.neighbors)
            
            # Aplica critérios de seleção (DSAT, Grau)
            if current_saturation > max_saturation:
                max_saturation = current_saturation
                max_degree = current_degree
                best_vertex_to_color = vertex
            elif current_saturation == max_saturation:
                if current_degree > max_degree:
                    max_degree = current_degree
                    best_vertex_to_color = vertex
        
        # Se todos tiverem a mesma saturação e grau, apenas pega o primeiro
        if best_vertex_to_color is None:
            best_vertex_to_color = uncolored_vertices[0]


        # --- Parte 2: Tentar colorir o vértice escolhido com backtracking ---
        
        # Itera sobre todas as cores possíveis para o vértice escolhido
        for color in range(1, self.size + 1):
            
            # Verifica se a cor é válida para a posição atual
            is_valid_move = True
            for r, c in best_vertex_to_color.neighbors:
                if self.get_vertex(r, c).color == color:
                    is_valid_move = False
                    break
            
            if is_valid_move:
                # Se a cor é válida, aplica-a e chama a recursão
                self.set_color(best_vertex_to_color.row, best_vertex_to_color.col, color)
                
                # Se a chamada recursiva encontrar uma solução, propaga o sucesso
                if self.solve_dsatur_backtracking():
                    return True
                
                # Se não, desfaz a jogada (BACKTRACK) e tenta a próxima cor
                self.set_color(best_vertex_to_color.row, best_vertex_to_color.col, 0)
        
        # Se nenhuma cor funcionou para este vértice, retorna False para a chamada anterior
        return False



    def print_graph(self):
        for key, vertex in self.vertices.items():
            print(f"{key}: color={vertex.color}, neighbors={len(vertex.neighbors)}")

    def clear_board(self):
        """Reseta todas as células para o estado vazio e desbloqueado."""
        for vertex in self.vertices.values():
            vertex.color = 0
            vertex.locked = False

    def load_from_string(self, puzzle_string):
        """Limpa o tabuleiro e carrega um novo puzzle a partir de uma string de 81 caracteres."""
        if len(puzzle_string) != self.size ** 2:
            raise ValueError(f"A string do puzzle deve ter {self.size**2} caracteres.")
        
        self.clear_board()
        
        for i, char in enumerate(puzzle_string):
            if '1' <= char <= '9':
                row = i // self.size
                col = i % self.size
                value = int(char)
                self.set_color(row, col, value, locked=True)        


