import pyxel
import random

#スクリーン幅・高の設定
SCREEN_WIDTH = 240
SCREEN_HEIGHT = 200

#色の設定
COLOR_BACKGROUND = 7
COLOR_PLAYER = 0
COLOR_ENEMY = 8      
COLOR_PLAYER_BULLET = 0
COLOR_ENEMY_BULLET = 8
COLOR_BARRIER_FULL = 11
COLOR_BARRIER_MID = 10
COLOR_BARRIER_LOW = 9
COLOR_TEXT = 0
COLOR_GAMEOVER_TEXT = 8
COLOR_WIN_TEXT = 11

#各オブジェクトのサイズ設定。各クラスのinitで呼び出し。
PLAYER_WIDTH = 12
PLAYER_HEIGHT = 8
PLAYER_SPEED = 2
BULLET_WIDTH = 2
BULLET_HEIGHT = 5
BULLET_SPEED = 3
ENEMY_BULLET_SPEED = 2
ENEMY_WIDTH = 10
ENEMY_HEIGHT = 8
ENEMY_SPEED = 0.5

#動作で使用する変数、リストの初期設定値。
player = None
enemies = []
player_bullets = []
enemy_bullets = []
barriers = []

score = 0
level = 1
game_state = "playing"

enemy_move_direction = 1
enemy_move_down_timer_max = 30
enemy_move_down_timer = 0
enemy_shoot_chance = 0.01

class GameObject:
    def __init__(self, x, y, w, h, col):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.col = col
        self.is_active = True

    def draw(self):
        if self.is_active:
            pyxel.rect(self.x, self.y, self.w, self.h, self.col)

    def collides_with(self, other):
        if not self.is_active or not other.is_active:
            return False
        return (self.x < other.x + other.w and
                self.x + self.w > other.x and
                self.y < other.y + other.h and
                self.y + self.h > other.y)

class Player(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_WIDTH, PLAYER_HEIGHT, COLOR_PLAYER)
        self.shoot_cooldown = 0 #連射制限初期値（0で発射可能）
        self.shoot_cooldown_max = 15 #連射制限

    def update(self):
        if self.shoot_cooldown > 0: 
            self.shoot_cooldown -= 1 #毎フレーム、15から1カウントダウン。

        if pyxel.btn(pyxel.KEY_LEFT) and self.x > 0: #左への移動
            self.x -= PLAYER_SPEED
        if pyxel.btn(pyxel.KEY_RIGHT) and self.x < SCREEN_WIDTH - self.w: #右への移動
            self.x += PLAYER_SPEED

        if pyxel.btnp(pyxel.KEY_SPACE) and self.shoot_cooldown == 0: #敵への攻撃（Bulletの発射）
            player_bullets.append(Bullet(self.x + self.w // 2 - BULLET_WIDTH // 2, self.y - BULLET_HEIGHT, -BULLET_SPEED, COLOR_PLAYER_BULLET)) #-BULLET_SPEEDでY軸の進行方向を制御。呼び出しは218行で敵の弾とコンバイン。
            self.shoot_cooldown = self.shoot_cooldown_max #発射後、クールダウンを最大（15）に設定。self.shoot_cooldownへ（77行）。
            pyxel.play(0, 0)

    def draw(self):
        super().draw()
        pyxel.rect(self.x + self.w // 2 - 1, self.y - 2, 2, 2, self.col)


class Enemy(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, ENEMY_WIDTH, ENEMY_HEIGHT, COLOR_ENEMY)
        self.speed_x = ENEMY_SPEED * level #レベルによって、敵のスピードを変化（レベルは41行で定義）

    def update(self):
        global enemy_move_direction
        self.x += self.speed_x * enemy_move_direction #e_m_dは、基本的に正の値を取る（右方向に進行）

        if random.random() < enemy_shoot_chance * (1 + level * 0.1):
            enemy_bullets.append(Bullet(self.x + self.w // 2 - BULLET_WIDTH // 2, self.y + self.h, ENEMY_BULLET_SPEED, COLOR_ENEMY_BULLET))

    def draw(self):
        super().draw()


class Bullet(GameObject):
    def __init__(self, x, y, speed_y, col):
        super().__init__(x, y, BULLET_WIDTH, BULLET_HEIGHT, col)
        self.speed_y = speed_y

    def update(self):
        self.y += self.speed_y
        if self.y + self.h < 0 or self.y > SCREEN_HEIGHT:
            self.is_active = False

class BarrierBlock(GameObject):
    def __init__(self, x, y, w=4, h=4):
        super().__init__(x, y, w, h, COLOR_BARRIER_FULL)
        self.health = 3

    def hit(self):
        self.health -= 1
        if self.health <= 0:
            self.is_active = False
            pyxel.play(0,3)
        elif self.health == 2:
            self.col = COLOR_BARRIER_MID
            pyxel.play(0,2)
        elif self.health == 1:
            self.col = COLOR_BARRIER_LOW
            pyxel.play(0,2)

    def draw(self):
        if self.is_active:
            pyxel.rect(self.x, self.y, self.w, self.h, self.col)

def init_game():
    global player, enemies, player_bullets, enemy_bullets, barriers, score, level, game_state, enemy_move_direction, ENEMY_SPEED
    global enemy_shoot_chance

    player = Player(SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2, SCREEN_HEIGHT - PLAYER_HEIGHT - 10)

    enemies.clear()
    player_bullets.clear()
    enemy_bullets.clear()
    barriers.clear()

    score = 0
    game_state = "playing"
    enemy_move_direction = 1
    
    current_enemy_speed = ENEMY_SPEED * (1 + (level -1) * 0.2)
    current_enemy_shoot_chance = enemy_shoot_chance * (1 + (level -1) * 0.005)

    num_enemy_rows = 3
    num_enemy_cols = 8
    enemy_start_x = 20
    enemy_start_y = 20
    enemy_spacing_x = (ENEMY_WIDTH + 8)
    enemy_spacing_y = (ENEMY_HEIGHT + 8)
    for r in range(num_enemy_rows):
        for c in range(num_enemy_cols):
            ex = enemy_start_x + c * enemy_spacing_x
            ey = enemy_start_y + r * enemy_spacing_y
            enemy = Enemy(ex, ey)
            enemy.speed_x = current_enemy_speed
            enemies.append(enemy)

    num_barriers_group = 4
    barrier_block_size = 4
    barrier_blocks_w = 5
    barrier_blocks_h = 4
    barrier_group_width = barrier_blocks_w * barrier_block_size
    barrier_spacing = (SCREEN_WIDTH - (num_barriers_group * barrier_group_width)) // (num_barriers_group + 1)
    barrier_y_pos = SCREEN_HEIGHT - 60

    for i in range(num_barriers_group):
        bx_start = barrier_spacing * (i + 1) + barrier_group_width * i
        for r in range(barrier_blocks_h):
            for c in range(barrier_blocks_w):
                if not (r < 2 and (c == barrier_blocks_w // 2)):
                     block = BarrierBlock(bx_start + c * barrier_block_size,
                                         barrier_y_pos + r * barrier_block_size,
                                         barrier_block_size, barrier_block_size)
                     barriers.append(block)

def update():
    global game_state, score, enemy_move_direction, enemy_move_down_timer, level

    if game_state == "playing":
        player.update()
        move_down_flag = False
        if enemy_move_down_timer > 0:
            enemy_move_down_timer -=1
            if enemy_move_down_timer == 0:
                for enemy in enemies:
                    enemy.y += ENEMY_HEIGHT // 2
                    if enemy.y + enemy.h >= player.y - PLAYER_HEIGHT:
                        game_state = "gameover"
                        pyxel.play(1, 5)
                        return
                enemy_move_direction *= -1
        else:
            for enemy in enemies:
                if not enemy.is_active: continue
                enemy.update()
                if (enemy.x + enemy.w > SCREEN_WIDTH and enemy_move_direction == 1) or \
                   (enemy.x < 0 and enemy_move_direction == -1):
                    move_down_flag = True
            if move_down_flag:
                enemy_move_down_timer = enemy_move_down_timer_max

        for b in player_bullets + enemy_bullets:
            b.update()
        for pb in player_bullets:
            if not pb.is_active: continue
            for e in enemies:
                if not e.is_active: continue
                if pb.collides_with(e):
                    pb.is_active = False
                    e.is_active = False
                    score += 10 * level
                    pyxel.play(0, 4)
                    break

        for eb in enemy_bullets:
            if not eb.is_active: continue
            if eb.collides_with(player):
                eb.is_active = False
                game_state = "gameover"
                pyxel.play(1, 5)
                return
            
        for bullet in player_bullets + enemy_bullets:
            if not bullet.is_active: continue
            for block in barriers:
                if not block.is_active: continue
                if bullet.collides_with(block):
                    bullet.is_active = False
                    block.hit()
                    break

        for enemy in enemies:
            if not enemy.is_active: continue
            for block in barriers:
                if not block.is_active: continue
                if enemy.collides_with(block):
                    block.is_active = False
                    pyxel.play(0,3)

        enemies[:] = [e for e in enemies if e.is_active]
        player_bullets[:] = [pb for pb in player_bullets if pb.is_active]
        enemy_bullets[:] = [eb for eb in enemy_bullets if eb.is_active]
        barriers[:] = [b for b in barriers if b.is_active]

        for enemy in enemies:
            if enemy.y + enemy.h >= player.y:
                game_state = "gameover"
                pyxel.play(1, 5)
                return

        if not enemies:
            level += 1
            if level > 5:
                game_state = "win"
                pyxel.play(1, 6)
            else:
                init_game()

    elif game_state == "gameover" or game_state == "win":
        if pyxel.btnp(pyxel.KEY_R):
            level = 1
            init_game()
        elif pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()


def draw():
    pyxel.cls(COLOR_BACKGROUND)

    if game_state == "playing":
        player.draw()
        for obj_list in [enemies, player_bullets, enemy_bullets, barriers]:
            for obj in obj_list:
                obj.draw()

        pyxel.text(5, 5, f"SCORE: {score}", COLOR_TEXT)
        pyxel.text(SCREEN_WIDTH - 40, 5, f"LEVEL: {level}", COLOR_TEXT)

    elif game_state == "gameover":
        msg = "GAME OVER"
        msg_x = (SCREEN_WIDTH - len(msg) * pyxel.FONT_WIDTH) // 2
        pyxel.text(msg_x, SCREEN_HEIGHT // 2 - 20, msg, COLOR_GAMEOVER_TEXT)
        help_msg = "PRESS R TO RESTART / Q TO QUIT"
        help_x = (SCREEN_WIDTH - len(help_msg) * pyxel.FONT_WIDTH) // 2
        pyxel.text(help_x, SCREEN_HEIGHT // 2 + 10, help_msg, COLOR_TEXT)

    elif game_state == "win":
        msg = "YOU WIN!"
        msg_x = (SCREEN_WIDTH - len(msg) * pyxel.FONT_WIDTH) // 2
        pyxel.text(msg_x, SCREEN_HEIGHT // 2 - 20, msg, COLOR_WIN_TEXT)
        help_msg = "PRESS R TO RESTART / Q TO QUIT"
        help_x = (SCREEN_WIDTH - len(help_msg) * pyxel.FONT_WIDTH) // 2
        pyxel.text(help_x, SCREEN_HEIGHT // 2 + 10, help_msg, COLOR_TEXT)

pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Pyxel Invaders", fps=30)

pyxel.sound(0).set("c3", "p", "6", "n", 10)
pyxel.sound(1).set("a2", "s", "5", "f", 12)
pyxel.sound(2).set("e2", "n", "4", "f", 8) 
pyxel.sound(3).set("c2", "n", "7", "f", 15)
pyxel.sound(4).set("g3", "t", "6", "f", 10)
pyxel.sound(5).set("c2g1c1", "t", "7", "f", 25)
pyxel.sound(6).set("c3e3g3c4", "p", "7", "n", 20)

init_game()
pyxel.run(update, draw)