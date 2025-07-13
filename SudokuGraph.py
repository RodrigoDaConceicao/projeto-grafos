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

    def print_graph(self):
        for key, vertex in self.vertices.items():
            print(f"{key}: color={vertex.color}, neighbors={len(vertex.neighbors)}")

