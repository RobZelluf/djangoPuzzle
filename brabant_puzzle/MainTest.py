from brabant_puzzle.solve_puzzle import Solver


def test_check_stuck():
    solver = Solver()
    S = solver.start_S

    S[32] = solver.all_options.index("Met ie")
    S[55] = solver.all_options.index("Theater")

    assert solver.check_stuck(S, 32)
    assert solver.check_stuck(S, 55)

    S[51] = solver.all_options.index("040 (Eindhoven")
    S[53] = solver.all_options.index("076 (Breda)")

    assert solver.check_stuck(S, 51)
    assert solver.check_stuck(S, 53)

    S[11] = solver.all_options.index("Hilvarenbeek")

    assert not solver.check_stuck(S, 11)


test_check_stuck()