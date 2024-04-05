import sys, random
import pygame
from pygame.locals import *
from tkinter import messagebox
import networkx as nx

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
move_speed = 0.5

#色を定義
black = (0, 0, 0)
red = (255, 0, 0)
white = (255, 255, 255)
brown = (115, 66, 41)
orange = (233, 168, 38)
item_color = (0, 255, 0)
maze_color = [white, brown, orange, item_color]

#迷路を自動生成する
def make_maze():
    global maze, px, py, total_score, ex, ey #グローバル変数
    px = 1
    py = 1
    ex = maze_w - 2
    ey = maze_h - 2
    tbl = [[0,-1],[1,0],[0,1],[-1,0]] # 上下左右の移動方向リスト（インデックス0から順に、上右下左）
    
    #迷路の各セルを0（通路）で初期化
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
    for i in range(30):#引数がアイテム個数
        item_x = random.randint(1, maze_w-2)
        item_y = random.randint(1, maze_h-2)
        if maze[item_y][item_x] == 0:
            maze[item_y][item_x] = 3

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

# プレイヤーまでの最短経路計算
def calculate_shortest_path(start_x, start_y, goal_x, goal_y):
    # グラフを作成
    G = nx.Graph()
    # ノードを追加
    for y in range(maze_h):
        for x in range(maze_w):
            if maze[y][x] != 1: # 壁でない場合
                G.add_node((x, y))

    # 辺を追加
    for y in range(maze_h):
        for x in range(maze_w):
            if maze[y][x] != 1:
                neighbors = [(x+dx, y+dy) for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]
                             if 0 <= x+dx < maze_w and 0 <= y+dy < maze_h and maze[y+dy][x+dx] != 1]
                for neighbor in neighbors:
                    G.add_edge((x, y), neighbor)

    # A*アルゴリズムで最短経路を計算
    shortest_path = nx.astar_path(G, (start_x, start_y), (goal_x, goal_y))

    return shortest_path

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
def check_key():
    global px, py, total_score, start_time, ex, ey

    move_left = False
    move_right = False
    move_up = False
    move_down = False

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN: # キーが押されたとき
            old_x, old_y = px, py
            
            if event.key == K_LEFT:
                move_left = True
            elif event.key == K_RIGHT:
                move_right = True
            elif event.key == K_UP:
                move_up = True
            elif event.key == K_DOWN:
                move_down = True
                
    if move_left:
        while px > 1 and maze[int(py)][int(px - move_speed)] != 1:
            px -= move_speed
    elif move_right:
        while px < maze_w - 2 and maze[int(py)][int(px + move_speed)] != 1:
            px += move_speed

    elif move_up:
        while py > 1 and maze[int(py - move_speed)][int(px)] != 1:
            py -= move_speed
    elif move_down:
        while py < maze_h - 2 and maze[int(py + move_speed)][int(px)] != 1:
            py += move_speed
            
            # ゴール
            if maze[int(py)][int(px)] == 2: #ゴール座標
                end_time = pygame.time.get_ticks()
                elapsed_time = (end_time - start_time) // 1000
                messagebox.showinfo("GOAL!", f"Score: {total_score}, Clear Time: {elapsed_time}seconds")
                restart()

            # アイテム
            elif maze[int(py)][int(px)] == 3:
                total_score += 10
                maze[int(py)][int(px)] = 0
        
            # 壁の中へ移動しないようにする
            else:
                px, py = old_x, old_y

        
def main():
    global px, py, total_score, start_time
    pygame.init()
    pygame.display.set_caption("Maze Game")
    screen = pygame.display.set_mode((tile_w * maze_w + 200,tile_w * maze_h))
    make_maze()

    #タイマーの開始時間
    start_time = pygame.time.get_ticks() #ミリ秒単位で現在の時間を取得
    reset_positions()
    
    # ゲームのメインループ
    clock = pygame.time.Clock()
    while True:
        screen.fill(black)       
        for y in range(0,maze_h):
            for x in range(0, maze_w):
                v = maze[y][x]
                xx = tile_w * x
                yy = tile_w * y
                pygame.draw.rect(screen, maze_color[v],
                                 (xx,yy,xx+tile_w,yy+tile_w))

        #プレイヤーと敵の位置を描画
        draw_positions(screen)

        check_key()

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
        
        pygame.display.update()
                
        # イベントを処理する
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            # ゴール
            elif event.type == KEYDOWN and event.key == K_RETURN:
                if maze[int(py)][int(px)] == 2: #ゴール座標
                    end_time = pygame.time.get_ticks()
                    elapsed_time = (end_time - start_time) // 1000
                    messagebox.showinfo("GOAL!", f"Score: {total_score}, Clear Time: {elapsed_time}seconds")
                    restart()

            # アイテム
            elif maze[int(py)][int(px)] == 3:
                total_score += 10
                maze[int(py)][int(px)] = 0

        clock.tick(50) # FPS

pygame.init()

if __name__ == "__main__":
    main()
