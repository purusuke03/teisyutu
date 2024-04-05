import sys, random
import pygame
from pygame.locals import *
from tkinter import messagebox
import networkx as nx
import matplotlib.pyplot as plt

#変数の初期化
maze_w = 31 #迷路の列数
maze_h = 23 #迷路の行数
maze = [] #迷路データ
tile_w = 16 #１ブロックのサイズ
px = 1 #プレイヤーの初期座標
py = 1
ex = 0 #敵の初期座標
ey = 0
total_score = 0
enemy_moving = True

#色を定義
black = (0, 0, 0)
red = (255, 0, 0)
white = (255, 255, 255)
brown = (115, 66, 41)
orange = (233, 168, 38)
item_color = (0, 255, 0)
maze_color = [white, brown, orange, item_color]

# プレイヤーまでの最短経路計算
def calculate_shortest_path(start_x, start_y, goal_x, goal_y):
    # グラフを生成
    G = nx.Graph()

    # ノードを追加
    for y in range(len(maze)):
        for x in range(len(maze[0])):
            if maze[y][x] != 1:  # 壁でない場合
                G.add_node((x, y))

    # 辺を追加
    for y in range(len(maze)):
        for x in range(len(maze[0])):
            if maze[y][x] != 1:
                neighbors = [(x + dx, y + dy) for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]
                             if 0 <= x + dx < len(maze[0]) and 0 <= y + dy < len(maze) and maze[y + dy][x + dx] != 1]
                for neighbor in neighbors:
                    G.add_edge((x, y), neighbor)

    # A*アルゴリズムで最短経路を計算
    shortest_path = nx.astar_path(G, (start_x, start_y), (goal_x, goal_y))

    return shortest_path

def visualize_shortest_path(screen, maze, shortest_path):
    for i in range(len(shortest_path) - 1):
        # 現在のセルと次のセルの中心座標を取得
        x1, y1 = shortest_path[i]
        x2, y2 = shortest_path[i + 1]
        x1 = x1 * tile_w + tile_w // 2
        y1 = y1 * tile_w + tile_w // 2
        x2 = x2 * tile_w + tile_w // 2
        y2 = y2 * tile_w + tile_w // 2
        
        # 線を描画
        pygame.draw.line(screen, (255, 0, 0), (x1, y1), (x2, y2), 2)

    # Pygameウィンドウを更新
    pygame.display.update()


def draw_nodes(screen):
    for y in range(maze_h):
        for x in range(maze_w):
            if maze[y][x] != 1:  # 壁でない場合
                pygame.draw.circle(screen, (0, 255, 0),
                                   (x * tile_w + tile_w // 2, y * tile_w + tile_w // 2), 2)
                
#迷路を自動生成する
def make_maze():
    global maze, px, py, total_score, ex, ey #グローバル変数
    px = 1
    py = 1
    ex = maze_w - 2
    ey = maze_h - 2
    tbl = [[0,-1],[1,0],[0,1],[-1,0]] # 上下左右の移動方向リスト（インデックス0から順に、上右下左）
    
    #迷路の各マス目（通路(0)、壁）を初期化
    maze = []
    for y in range(0, maze_h):
        row = []
        for x in range(0, maze_w):
            row.append(0)
        maze.append(row)
        
    #周囲を壁（1）で囲む
    for x in range(0, maze_w):
        maze[0][x] = 1
        maze[maze_h - 1][x] = 1
    for y in range(0, maze_h):
        maze[y][0] = 1
        maze[y][maze_w - 1] = 1
        
    #棒倒し法で迷路を生成
    for y in range(2, maze_h - 2):
        for x in range(2, maze_w - 2):
            if x % 2 == 0 and y % 2 == 0:
                r = random.randint(0, 3)
                maze[y][x] = 1
                maze[y + tbl[r][1]][x + tbl[r][0]] = 1
                
    #ゴールを右下に設定
    maze[maze_h-2][maze_w-2] = 2

    #アイテムの配置
    for i in range(20): # 引数がアイテム配置を行う回数
        item_x = random.randint(1, maze_w-2)
        item_y = random.randint(1, maze_h-2)
        if maze[item_y][item_x] == 0: # 0(通路)である場合
            maze[item_y][item_x] = 3 # 3(アイテム)を配置

# 各ステータスをリセット
def restart():
    global total_score, start_time
    total_score = 0
    reset_positions()
    make_maze()
    start_time = pygame.time.get_ticks()

# プレイヤーと敵の初期位置
def reset_positions():
    global px, py, ex, ey
    px, py = 1, 1
    ex, ey = maze_w - 2, maze_h - 2

# プレイヤーと敵を描画
def draw_positions(screen):
    t2 = tile_w / 2
    pygame.draw.circle(screen, red, (px * tile_w + t2, py * tile_w + t2), t2) #プレイヤー
    pygame.draw.rect(screen, black, (ex * tile_w, ey * tile_w, tile_w, tile_w)) #敵

# 敵の追跡処理
def enemy_chase():
    global px, py, ex, ey, enemy_moving

    # 敵が停止するかどうかランダムで決定（数値が大きいほど動く頻度が増える）
    if random.random() < 0.05:
        enemy_moving = True # 動く
    else:
        enemy_moving = False # 停止
        return

    # 敵が動く場合、追跡処理を行う
    if enemy_moving:
        shortest_path = calculate_shortest_path(int(ex), int(ey), int(px), int(py))
        if len(shortest_path) > 1:
            next_x, next_y = shortest_path[1]
            ex, ey = next_x, next_y

    # 接触判定、ゲームオーバー処理
    if abs(px - ex) < 1 and abs(py - ey) < 1:
        messagebox.showinfo("GAME OVER", "RESTART?")
        restart()
    
#プレイヤーの移動確認
def check_key(key):
    global px, py, total_score, start_time, ex, ey
    old_x, old_y = px, py
    
    if key == K_LEFT:
        px -= 1
    elif key == K_RIGHT:
        px += 1
    elif key == K_UP:
        py -= 1
    elif key == K_DOWN:
        py += 1

    if maze[py][px] == 0 or maze[py][px] == 2 or maze[py][px] == 3:
    
        # ゴール
        if maze[py][px] == 2: #ゴール座標
            end_time = pygame.time.get_ticks()
            elapsed_time = (end_time - start_time) // 1000
            messagebox.showinfo("GOAL!", f"Score: {total_score}, Clear Time: {elapsed_time}seconds")
            restart()

        # アイテム
        elif maze[py][px] == 3:
            total_score += 10
            maze[py][px] = 0
        pass
        
    # 壁の中へ移動しないようにする
    else:
        px, py = old_x, old_y

        
def main():
    global px, py, total_score, start_time
    pygame.init()
    pygame.display.set_caption("Maze Game")
    screen = pygame.display.set_mode((tile_w * maze_w + 200, tile_w * maze_h))
    make_maze()

    #タイマーの開始時間
    start_time = pygame.time.get_ticks() #ミリ秒単位で現在の時間を取得
    reset_positions()
    
    # ゲームのメインループ
    clock = pygame.time.Clock()
    while True:
        screen.fill(black)       
        for y in range(maze_h):
            for x in range(maze_w):
                v = maze[y][x]
                xx = tile_w * x
                yy = tile_w * y
                pygame.draw.rect(screen, maze_color[v],
                                 (xx, yy, xx + tile_w, yy + tile_w))

        #プレイヤーと敵の位置を描画
        draw_positions(screen)

        enemy_chase()

        #スコアを表示
        font = pygame.font.Font(None, 36)
        text = font.render(f"SCORE: {total_score}", True, white)
        screen.blit(text, (tile_w * maze_w, 10))

        #経過時間を計算して表示
        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - start_time) // 1000
        timer_text = font.render(f"TIME: {elapsed_time}seconds", True, white)
        screen.blit(timer_text, (tile_w * maze_w, 50))
        
        # 最短経路を計算
        shortest_path = calculate_shortest_path(px, py, ex, ey)
        
        # 最短経路とノードを描画
        visualize_shortest_path(screen, maze, shortest_path)
        draw_nodes(screen)

        pygame.display.update()
                
        # イベントを処理する
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                check_key(event.key)

        clock.tick(50) # FPS

if __name__ == "__main__":
    make_maze()
    shortest_path = calculate_shortest_path(px, py, ex, ey)  # 最短経路を計算
    main()
