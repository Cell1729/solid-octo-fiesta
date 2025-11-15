from state import RubiksCubeState
from typing import Tuple, Dict, List, Optional

# 完成状態
SOLVED_STATE = RubiksCubeState(
    [0, 1, 2, 3, 4, 5, 6, 7],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
)

def build_moves() -> Tuple[Dict[str, RubiksCubeState], List[str]]:
    """
    18種類の1手操作を生成して返す。
    戻り値: (moves_dict, move_names_list)
      - moves_dict: {move_name: RubiksCubeState, ...}
      - move_names_list: ['U','U2','U\'', 'D', ...]
    """
    moves = {
        'U': RubiksCubeState([3, 0, 1, 2, 4, 5, 6, 7],
                   [0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 1, 2, 3, 7, 4, 5, 6, 8, 9, 10, 11],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
        'D': RubiksCubeState([0, 1, 2, 3, 5, 6, 7, 4],
                   [0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 8],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
        'L': RubiksCubeState([4, 1, 2, 0, 7, 5, 6, 3],
                   [2, 0, 0, 1, 1, 0, 0, 2],
                   [11, 1, 2, 7, 4, 5, 6, 0, 8, 9, 10, 3],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
        'R': RubiksCubeState([0, 2, 6, 3, 4, 1, 5, 7],
                   [0, 1, 2, 0, 0, 2, 1, 0],
                   [0, 5, 9, 3, 4, 2, 6, 7, 8, 1, 10, 11],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
        'F': RubiksCubeState([0, 1, 3, 7, 4, 5, 2, 6],
                   [0, 0, 1, 2, 0, 0, 2, 1],
                   [0, 1, 6, 10, 4, 5, 3, 7, 8, 9, 2, 11],
                   [0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0]),
        'B': RubiksCubeState([1, 5, 2, 3, 0, 4, 6, 7],
                   [1, 2, 0, 0, 2, 1, 0, 0],
                   [4, 8, 2, 3, 1, 5, 6, 7, 0, 9, 10, 11],
                   [1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
                   )
    }

    move_names: List[str] = []
    faces = list(moves.keys())
    for face_name in faces:
        move_names += [face_name, face_name + '2', face_name + "'"]
        # X2 は X を 2 回合成
        moves[face_name + '2'] = moves[face_name].apply_move(moves[face_name])
        # X' は X を 3 回合成 (X^3 == X^-1)
        moves[face_name + "'"] = moves[face_name].apply_move(moves[face_name]).apply_move(moves[face_name])

    return moves, move_names


def apply_single_move(state: RubiksCubeState, move_name: str, moves: Optional[Dict[str, RubiksCubeState]] = None) -> RubiksCubeState:
    """
    指定した1手を state に適用して新しい state を返す。
    moves を渡さなければ内部で build_moves() を呼ぶ。
    """
    if moves is None:
        moves, _ = build_moves()
    if move_name not in moves:
        raise KeyError(f"Unknown move name: {move_name}")
    move_state = moves[move_name]
    return state.apply_move(move_state)


def scramble2state(scramble: str, base_state: Optional[RubiksCubeState] = None, moves: Optional[Dict[str, RubiksCubeState]] = None) -> RubiksCubeState:
    """
    スクランブル文字列（例: "R U R' U'"）を base_state に適用した state を返す。
    空文字列を渡すと base_state をそのまま返す。
    """
    if base_state is None:
        base_state = SOLVED_STATE
    if moves is None:
        moves, _ = build_moves()

    state = base_state
    if scramble.strip() == "":
        return state

    for move_name in scramble.split():
        if move_name == "":
            continue
        if move_name not in moves:
            raise KeyError(f"Unknown move in scramble: {move_name}")
        state = state.apply_move(moves[move_name])
    return state

# 互換性のための旧関数名エイリアス（typo の修正）
scamble2state = scramble2state


if __name__ == '__main__':
    # スクリプトとして実行したときのデモ
    moves, move_names = build_moves()
    print("available moves:", move_names)

    # 完成状態を表示
    print('\nSOLVED_STATE:')
    print('cp =', SOLVED_STATE.cp)
    print('co =', SOLVED_STATE.co)
    print('ep =', SOLVED_STATE.ep)
    print('eo =', SOLVED_STATE.eo)

    # 例: 'U' のみを適用する
    after_u = apply_single_move(SOLVED_STATE, 'U', moves)
    print('\nAfter applying U:')
    print('cp =', after_u.cp)
    print('co =', after_u.co)
    print('ep =', after_u.ep)
    print('eo =', after_u.eo)

    # 例: 'U2' と 'U\'' の確認
    after_u2 = apply_single_move(SOLVED_STATE, 'U2', moves)
    after_umin = apply_single_move(SOLVED_STATE, "U'", moves)
    print('\nU2 cp =', after_u2.cp)
    print("U' cp =", after_umin.cp)
