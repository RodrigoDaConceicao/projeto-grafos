import math
import time

from scipy.stats import norm
from SudokuGraph import SudokuGraph  # Assuming this class is in SudokuGraph.py

easy_boards = [
    "080090040009000700106470803000000600803000501002000000601082409005000300090040050",
    "516407000000150000090006000804200097050000020170005304000600040000049000000801932",
    "600000000020316040000090015010040050083000270050020090190070000070461020000000001",
    "001090200060700030079000610000078020800905007090360000082000790050007040004050100",
    "906701000053000000008005900500060008002307100001090300009003681000000050000602009",
]

medium_boards = [
    "103700809090860070700001003002000097030000020410000300200100005040052010801007602",
    "000103020350040100000605000501000307090080050704000201000408000009010038040906000",
    "059300640700506002600200009010000238000000000827000010100009003400805007078002590",
    "093010680200007005000480000050000400804000203002000050000096000100800004069040520",
    "820000007500030000030508000006741200050609040004325600000807010000050004200000076",
]

hard_boards = [
    "000005410000409300003010006200050840400708003058040001120090600300506000004002000",
    "040300508008000200100502003205070800000000060800600005000000007003406000600800009",
    "000900170000003000342080000506000002800090010000300600200000000063000090090240700",
    "300107049200600000000000100047090010000000400620700030070060000000280005800400000",
    "030008470000001200002007000500600020007000100004090000008006700000005003105400000",
]

very_hard_boards = [
    "090700000000000350400000097034000070020901000000008140060090010040050200200607000",
    "400500000006180500005030090009000800530000019072000340020070960003620000000900002",
    "080000000000001503030000706072003004800500001400800900000105000009000007206000040",
    "009080070006490000004001003005000702023000004000000010000040200030079605000030001",
    "000100040020037900030020017006000500000000000283000796010080000907012860008300000",
]

expert_boards = [
    "000900407000054100000013820800030700060205080001080003056370000009520000203001000",
    "103520000007000001540000000900040710070203040065010003000000097000000300090071502",
    "005008600010400030004000900200034008030861070000570000002000800050100060007009500",
    "900060700000003050060700041600000007020941030090000080500100000076009200009070003",
    "005003800780009054200800003370208600000000000009107082500001009910500048006300500",
]

all_difficulties = {
    "Easy": easy_boards,
    "Medium": medium_boards,
    "Hard": hard_boards,
    "Very Hard": very_hard_boards,
    "Expert": expert_boards,
}

def z_test_series(values):
    if len(values) <= 1:
        return [(0, 1.0)] * len(values)
    
    mean = sum(values) / len(values)
    std_dev = math.sqrt(sum((x - mean) ** 2 for x in values) / (len(values) - 1))
    
    results = []
    for x in values:
        if std_dev == 0:
            z = 0
            p = 1.0
        else:
            z = (x - mean) / std_dev
            p = 2 * (1 - norm.cdf(abs(z)))
        results.append((z, p))
    return results

def run_tests():
    graph = SudokuGraph()
    solver_options = graph.get_solver_options()

    for display_name, method_name in solver_options:
        print(f"\n=== Testing Solver: {display_name} ===")
        for difficulty, boards in all_difficulties.items():
            print(f"\n--- Difficulty: {difficulty} ---")
            for i, board in enumerate(boards):
                times = []
                print(f"\nBoard {i + 1}")
                for attempt in range(10):
                    graph.load_from_string(board)
                    start = time.perf_counter()
                    result = getattr(graph, method_name)()
                    end = time.perf_counter()
                    elapsed = end - start
                    if not result:
                        print(f"[!] Attempt {attempt + 1}: Failed to solve")
                    times.append(elapsed)

                z_p_results = z_test_series(times)
                for attempt_idx, (elapsed, (z, p)) in enumerate(zip(times, z_p_results), start=1):
                    print(f"Attempt {attempt_idx}: {elapsed:.6f}s | Z = {z:+.2f}, p = {p:.4f}")
                
                if times:
                    avg = sum(times) / len(times)
                    min_time = min(times)
                    max_time = max(times)
                    print(f"\nStats for Board {i + 1}:")
                    print(f"Avg Time = {avg:.6f}s, Min = {min_time:.6f}s, Max = {max_time:.6f}s")

if __name__ == "__main__":
    run_tests()
