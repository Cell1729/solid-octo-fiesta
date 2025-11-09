"""
ルービックキューブの状態を管理する。
"""

class RubiksCubeState:
    """
    ルービックキューブの状態を表すクラス。
    """
    def __init__(self, cp, co, ep, eo):
        """
        ルービックキューブの状態を初期化する。
        :param cp: Corner Permutation コーナーの位置を表す8次元のベクトル(配列)
        :param co: Corner Orientation コーナーの向きを表す8次元のベクトル(配列)
        :param ep: Edge Permutation エッジの位置を表す12次元のベクトル(配列)
        :param eo: Edge Orientation エッジの向きを表す12次元のベクトル(配列)
        """
        self.cp = cp
        self.co = co
        self.ep = ep
        self.eo = eo

    def apply_move(self, move):
        """
        操作を適用し、新しい状態を返す
        """
        new_cp = [self.cp[p] for p in move.cp]
        new_co = [(self.co[p] + move.co[i]) % 3 for i, p in enumerate(move.cp)]
        new_ep = [self.ep[p] for p in move.ep]
        new_eo = [(self.eo[p] + move.eo[i]) % 2 for i, p in enumerate(move.ep)]
        return RubiksCubeState(new_cp, new_co, new_ep, new_eo)