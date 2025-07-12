class Vertex:
    def __init__(self, row, col, block, color=0):
        self.row = row
        self.col = col
        self.block = block
        self.color = color  # 0 means not set
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

    def set_color(self, row, col, color):
        if not (0 <= color <= self.size):
            raise ValueError(f"Color must be between 0 and {self.size}")
        self.vertices[(row, col)].color = color

    def print_graph(self):
        for key, vertex in self.vertices.items():
            print(f"{key}: color={vertex.color}, neighbors={len(vertex.neighbors)}")

