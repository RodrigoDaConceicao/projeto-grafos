from SudokuGraph import SudokuGraph
from Window import Window



graph = SudokuGraph(dimension=3)
# Set some sample values to simulate a puzzle
graph.set_color(0, 0, 5, True)
graph.set_color(1, 3, 8, True)
graph.set_color(4, 4, 3, True)
graph.set_color(8, 8, 9, True)

window = Window(graph)
window.run()