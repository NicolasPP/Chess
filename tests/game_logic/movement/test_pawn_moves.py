from chess import game as GAME


def test_first_turn_double_move(pawn_test_fen):
    from_index = 50
    assert len(GAME.get_available_moves('PAWN', from_index, pawn_test_fen, True)) is 2


def test_first_turn_double_move_and_possible_take(pawn_test_fen):
    from_index = 53
    assert len(GAME.get_available_moves('PAWN', from_index, pawn_test_fen, True)) is 3


def test_regular_move(pawn_test_fen):
    from_index = 41
    assert len(GAME.get_available_moves('PAWN', from_index, pawn_test_fen, True)) is 1


def test_blocked_by_piece(pawn_test_fen):
    from_index = 26
    assert len(GAME.get_available_moves('PAWN', from_index, pawn_test_fen, True)) is 0


def test_blocked_by_piece_and_possible_take(pawn_test_fen):
    from_index = 21
    assert len(GAME.get_available_moves('PAWN', from_index, pawn_test_fen, True)) is 1


def test_first_turn_double_move_blocked(pawn_test_fen):
    from_index = 55
    assert len(GAME.get_available_moves('PAWN', from_index, pawn_test_fen, True)) is 1


def test_first_turn_blocked(pawn_test_fen):
    from_index = 52
    assert len(GAME.get_available_moves('PAWN', from_index, pawn_test_fen, True)) is 0
