# ルービックキューブを描画するPythonスクリプト
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import argparse

# 完成状態の値。上からcp, co, ep, eo
solved = (
    [0, 1, 2, 3, 4, 5, 6, 7],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
)
# if __name__ == "__main__": にあるdraw_cube()に値を入れる。
# R2した状態
test_value = (
    [0, 6, 5, 3, 4, 2, 1, 7],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 2, 1, 3, 4, 9, 6, 7, 8, 5, 10, 11],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
)

# 顔の順序: U, D, R, L, F, B
FACE_NAMES = ["U", "D", "R", "L", "F", "B"]
# 標準色マップ（Matplotlib名またはRGBタプル）
STANDARD_COLORS = {
    "U": "white",
    "D": "yellow",
    "R": "red",
    "L": "orange",
    "F": "green",
    "B": "blue",
}


def _make_solved_facelets():
    """
    完成状態のステッカー配列（6 faces x 3 x 3）を作成して返す。
    return
    type f<class 'list'>
    [[['white', 'white', 'white'], ['white', 'white', 'white'], ['white', 'white', 'white']],
    [['yellow', 'yellow', 'yellow'], ['yellow', 'yellow', 'yellow'], ['yellow', 'yellow', 'yellow']],
    [['red', 'red', 'red'], ['red', 'red', 'red'], ['red', 'red', 'red']],
    [['orange', 'orange', 'orange'], ['orange', 'orange', 'orange'], ['orange', 'orange', 'orange']],
    [['green', 'green', 'green'], ['green', 'green', 'green'], ['green', 'green', 'green']],
    [['blue', 'blue', 'blue'], ['blue', 'blue', 'blue'], ['blue', 'blue', 'blue']]]
    """
    faces = []
    for name in FACE_NAMES:
        color = STANDARD_COLORS[name]
        faces.append([[color for _ in range(3)] for _ in range(3)])
    return faces


def state_to_facelets(cp, co, ep, eo):
    """
    cp/co/ep/eo から faces (6 x 3 x 3) のステッカー配列に変換する。

    入力:
      cp: list length 8
      co: list length 8
      ep: list length 12
      eo: list length 12
    出力:
      faces: list of 6 faces, each is 3x3 list of色名またはインデックス
    """
    # ベースは完成図の facelets（色名）を使用して、各コーナー/エッジが持つ "固有色" を取得する
    # 立体の完成図を取得
    base_faces = _make_solved_facelets()

    # ヘルパ: faces を mutable に作る
    # 描画用の配列 , 初期化
    faces = [[ [None for _ in range(3)] for _ in range(3)] for _ in range(6)]

    # README に合わせたコーナー -> (face, r, c) の対応（各 corner の orientation=0 の時に
    # U/D 側の色が最初に来るように (UD, other1, other2) の順で指定）
    """
    コーナーピースの各インデックスに対応するシール座標 (corner_facelet_pos) を定義
    - 0〜7 番コーナーそれぞれについて (faceIndex, row, col) のタプルを3つずつ持つ。
    - 配列順は (U/D 方向の色, その他1, その他2) になるよう並べている。これは向き計算（回転）を簡単にするため。
    
    最初の数字は色の番号
    # 顔の順序: U, D, R, L, F, B
    FACE_NAMES = ["U", "D", "R", "L", "F", "B"]
    
    (row, col)
    その面の正面から見て上か下か
    row = 0 上段
    row = 1 中段
    row = 2 下段
    
    その面を正面から見たときに左か右か
    col = 0 左列
    col = 1 
    col = 2 右列
    """
    corner_facelet_pos = [
        ((0, 0, 0), (3, 0, 0), (5, 0, 2)),
        ((0, 0, 2), (5, 0, 0), (2, 0, 2)),
        ((0, 2, 2), (2, 0, 0), (4, 0, 2)),
        ((0, 2, 0), (4, 0, 0), (3, 0, 2)),
        ((1, 2, 0), (5, 2, 2), (3, 2, 0)),
        ((1, 2, 2), (2, 2, 2), (5, 2, 0)),
        ((1, 0, 2), (4, 2, 2), (2, 2, 0)),
        ((1, 0, 0), (3, 2, 2), (4, 2, 0)),
    ]

    """
    エッジピースの各インデックスに対応するシール座標 (edge_facelet_pos) を定義
    - 0〜11 番エッジそれぞれについて (faceIndex, row, col) のタプルを2つ。
    - 定義順が内部ロジックの“エッジ番号”になる（README との対応に注意が必要）。
    
    (row, col)
    その面を正面から見て上中下のどこか
    row = 0 上段
    row = 1 中段
    row = 2 下段
    
    その面を正面から見たときに左か中央か右か
    col = 0 左列
    col = 1 中央列
    col = 2 右列
    """
    # エッジ -> (face, r, c) の対応（2要素）
    edge_facelet_pos = [
        # 0: U - B (UB)
        ((0, 0, 1), (5, 0, 1)),
        # 1: U - R (UR)
        ((0, 1, 2), (2, 0, 1)),
        # 2: U - F (UF)
        ((0, 2, 1), (4, 0, 1)),
        # 3: U - L (UL)
        ((0, 1, 0), (3, 0, 1)),
        # 4: F - R (FR)
        ((4, 1, 2), (2, 1, 0)),
        # 5: R - B (RB)
        ((2, 1, 2), (5, 1, 0)),
        # 6: B - L (BL)
        ((5, 1, 2), (3, 1, 0)),
        # 7: L - F (LF)
        ((3, 1, 2), (4, 1, 0)),
        # 8: D - F (DF)
        ((1, 2, 1), (4, 2, 1)),
        # 9: D - R (DR)
        ((1, 1, 2), (2, 2, 1)),
        # 10: D - B (DB)
        ((1, 0, 1), (5, 2, 1)),
        # 11: D - L (DL)
        ((1, 1, 0), (3, 2, 1)),
    ]

    # solved (home) colors for each corner/edge index (取っておく)
    corner_home_colors = []
    for ci in range(8):
        # 完成状態のコーナー情報を取得
        trip = corner_facelet_pos[ci]
        # その3つの位置から色を取得
        """
        変数としてはこの部分 (関数の最初の方に定義されている)
        base_faces = _make_solved_facelets()
        
        corner 0 の trip = ((0,0,0), (5,0,2), (3,0,0))
        → colors = [ base_faces[0][0][0], base_faces[5][0][2], base_faces[3][0][0] ] 
        → 例えば STANDARD_COLORS の設定なら ['white', 'blue', 'orange']
        """
        colors = [ base_faces[f][r][c] for (f,r,c) in trip ]
        # corner_home_colorsに追加
        corner_home_colors.append(colors)

    edge_home_colors = []
    for ei in range(12):
        # コーナーと似たことしている
        a,b = edge_facelet_pos[ei]
        colors = [ base_faces[a[0]][a[1]][a[2]], base_faces[b[0]][b[1]][b[2]] ]
        edge_home_colors.append(colors)

    # corners を配置
    for pos in range(8):
        cubie = cp[pos]
        orient = co[pos] % 3
        home_colors = corner_home_colors[cubie]
        placed_colors = [ home_colors[(i - orient) % 3] for i in range(3) ]
        # 置く位置の facelets
        trip = corner_facelet_pos[pos]
        for (idx, (f,r,c)) in enumerate(trip):
            faces[f][r][c] = placed_colors[idx]

    # edges を配置
    """
    エッジの配置ループ
    for pos in range(12):
    - cubie = ep[pos] でその位置にあるエッジピース番号。
    - home = edge_home_colors[cubie] → 2色セット。
    - flip = eo[pos] % 2 → 反転なら順番を入れ替える。
    - placed = [home[0], home[1]] if flip==0 else [home[1], home[0]]
    - edge_facelet_pos[pos] の2座標へ書き込む。    
    """
    for pos in range(12):
        cubie = ep[pos]
        flip = eo[pos] % 2
        home = edge_home_colors[cubie]
        if flip == 0:
            placed = [ home[0], home[1] ]
        else:
            placed = [ home[1], home[0] ]
        a,b = edge_facelet_pos[pos]
        faces[a[0]][a[1]][a[2]] = placed[0]
        faces[b[0]][b[1]][b[2]] = placed[1]

    # 中央は各面センターの色（変わらない）を埋める
    for fi, name in enumerate(FACE_NAMES):
        faces[fi][1][1] = STANDARD_COLORS[name]

    return faces


def draw_cube(value=None, figsize=(6, 6), save_path=None):
    """
    ルービックキューブを3Dで描画する。

    引数:
    - value: 6要素のリストまたはタプル。各要素は3x3の配列（色名または色インデックス）。
             None の場合は完成状態を描画する。
             (cp, co, ep, eo) のような状態タプルは自動で facelets に変換して描画する。
    - figsize: matplotlib figure サイズ
    - save_path: 指定すると画像を保存し、show は行わない（ヘッドレス実行向け）。

    返り値: matplotlib.figure.Figure
    """
    # value の解釈
    if value is None:
        faces = _make_solved_facelets()
    else:
        # もしタプル長4なら cp/co/ep/eo が渡された可能性が高い
        if isinstance(value, (list, tuple)) and len(value) == 4 and all(isinstance(v, list) for v in value):
            cp, co, ep, eo = value
            faces = state_to_facelets(cp, co, ep, eo)
        else:
            # 想定: value == list/tuple of 6 faces, each face is 3x3 list
            if not (isinstance(value, (list, tuple)) and len(value) == 6):
                raise ValueError("value は None か、6 要素のステッカー配列である必要があります")
            faces = value

    # 各ステッカーを 3D の平面上に配置する準備
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection="3d")

    # 軸の表示を整える
    ax.set_box_aspect([1, 1, 1])
    ax.axis("off")

    sticker_size = 2.0 / 3.0  # キューブの一辺を [-1,1] としたときのステッカーサイズ

    # 各面ごとの中心位置と平面上の基底ベクトル（右方向, 下方向）を定義
    # 座標系: x 右, y 上, z 前
    face_def = {
        "U": (np.array([0, 1.0, 0]), np.array([1.0, 0, 0]), np.array([0, 0, -1.0])),  # top: right=x, down=-z
        "D": (np.array([0, -1.0, 0]), np.array([1.0, 0, 0]), np.array([0, 0, 1.0])),  # bottom: right=x, down=+z
        "F": (np.array([0, 0, 1.0]), np.array([1.0, 0, 0]), np.array([0, -1.0, 0])),  # front: right=x, down=-y
        "B": (np.array([0, 0, -1.0]), np.array([-1.0, 0, 0]), np.array([0, -1.0, 0])), # back: right=-x to keep orientation
        "R": (np.array([1.0, 0, 0]), np.array([0, 0, -1.0]), np.array([0, -1.0, 0])),  # right: right=-z, down=-y
        "L": (np.array([-1.0, 0, 0]), np.array([0, 0, 1.0]), np.array([0, -1.0, 0])),  # left: right=+z, down=-y
    }

    patches = []
    colors = []

    for fi, name in enumerate(FACE_NAMES):
        center, right_vec, down_vec = face_def[name]
        face = faces[fi]
        # 各 face が 3x3 であることを期待
        for r in range(3):
            for c in range(3):
                # row r: 0..2 (top..bottom), col c: 0..2 (left..right)
                # 紙面上の中心オフセットを計算
                offset = ((c - 1) * sticker_size * 1.0) * right_vec + ((r - 1) * sticker_size * 1.0) * down_vec
                sticker_center = center + offset

                # 四隅を求める
                half = sticker_size / 2.0
                corners = [
                    sticker_center - half * right_vec - half * down_vec,
                    sticker_center + half * right_vec - half * down_vec,
                    sticker_center + half * right_vec + half * down_vec,
                    sticker_center - half * right_vec + half * down_vec,
                ]
                patches.append(corners)
                col = face[r][c]
                # カラーがインデックス（0..5）の場合には FACE_NAMES にマップ
                if isinstance(col, int):
                    col = STANDARD_COLORS[FACE_NAMES[col]]
                colors.append(col)

    poly = Poly3DCollection(patches, linewidths=0.5, edgecolors="black")
    poly.set_facecolor(colors)
    ax.add_collection3d(poly)

    # 軸範囲を揃える
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_zlim(-1.2, 1.2)

    # 軸の向きを見やすくするための初期ビュー
    ax.view_init(elev=20, azim=30)

    if save_path:
        fig.savefig(save_path, dpi=200)
        plt.close(fig)
    return fig


if __name__ == "__main__":
    # 完成状態からR
    test_R = (
        [0, 2, 6, 3, 4, 1, 5, 7],
        [0, 1, 2, 0, 0, 2, 1, 0],
        [0, 5, 9, 3, 4, 2, 6, 7, 8, 1, 10, 11],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    )

    # コマンドライン引数: デフォルトで GUI を表示 (plt.show)。
    # --save / -s を指定するとファイルに保存して GUI は表示しない。
    parser = argparse.ArgumentParser(description="3D ルービックキューブ描画デモ")
    parser.add_argument("--save", "-s", help="出力ファイルパス。指定しない場合は GUI を表示します。")
    args = parser.parse_args()

    faces = _make_solved_facelets()

    if args.save:
        draw_cube(faces, save_path=args.save)
        print(f"Saved demo image to {args.save}")
    else:
        draw_cube(value=test_R)
        plt.show()
