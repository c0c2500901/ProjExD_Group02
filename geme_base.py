import os
import random
import sys
import math
import pygame

# ワーキングディレクトリを作業ファイルの場所に設定
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 定数定義
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60
TIME_LIMIT = 120  # 制限時間（秒）

# 色の定義 (RGB)
COLOR_BG = (50, 160, 50)       # 緑色（フィールド）
COLOR_PLAYER = (0, 100, 255)   # 青色（プレイヤー）
COLOR_ENEMY = (255, 50, 50)    # 赤色（敵）
COLOR_WHITE = (255, 255, 255)  # 白色
COLOR_RED = (200, 0, 0)        # 強調用赤
COLOR_YELLOW = (255, 255, 0)   # ボム表示用黄色
COLOR_HEAL = (0, 255, 0)       # 回復アイテム
COLOR_ITEM_SCORE = (255, 255, 0)  # スコアアイテム
COLOR_STAMINA = (255, 255, 0)  # 黄色（スタミナバー用）
COLOR_SHIELD = (0, 230, 255)   # シールド用シアン


class Player:
    """プレイヤーの移動、HP、シールド（バリア）、描画を管理するクラス"""
    def __init__(self, x: float, y: float) -> None:
        """初期位置とステータスの設定"""
        self.x: float = x
        self.y: float = y
        self.radius: int = 15
        self.normal_speed: float = 4.0
        self.dash_speed: float = 7.0
        self.speed: float = self.normal_speed
        
        self.hp: int = 100
        self.max_hp: int = 100
        self.invincible_timer: int = 0  # 被弾後の無敵タイマー

        # Eキーで展開するシールド（無敵バリア）関連変数
        self.shield_timer: int = 0     # シールド展開時間（フレーム）
        self.shield_cooldown: int = 0  # クールダウン時間（フレーム）

        # ダッシュ機能用のスタミナ関連変数（最大100、使用で減少し、不使用で回復）
        self.max_stamina: float = 100.0
        self.stamina: float = 100.0
        self.is_dashing: bool = False

    def update(self, keys: pygame.key.ScancodeWrapper) -> None:

        """キー入力を受けて移動処理（ダッシュ含む）を行い、画面外への逸脱を防ぐ"""
        """移動入力とシールドタイマーの更新"""
        dx: float = 0.0
        dy: float = 0.0

        # WASDキー入力
        if keys[pygame.K_w]:
            dy -= 1.0
        if keys[pygame.K_s]:
            dy += 1.0
        if keys[pygame.K_a]:
            dx -= 1.0
        if keys[pygame.K_d]:
            dx += 1.0

        # Eキー入力でシールド発動（クールダウン中でない場合）
        if keys[pygame.K_e] and self.shield_cooldown == 0:
            self.shield_timer = 120      # 2秒間（120フレーム）無敵
            self.shield_cooldown = 1800  # 再使用まで30秒間（1800フレーム）のクールダウン

        # 斜め移動時の速度補正
        if dx != 0.0 and dy != 0.0:
            dx *= 0.7071
            dy *= 0.7071

        # SHIFTキーが押されていて、かつ移動中かつスタミナがある場合はダッシュ
        is_shift_pressed = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        if is_shift_pressed and (dx != 0.0 or dy != 0.0) and self.stamina > 5.0:
            self.speed = self.dash_speed
            self.is_dashing = True
            self.stamina -= 1.5  # ダッシュ中のスタミナ消費
            if self.stamina < 0.0:
                self.stamina = 0.0
        else:
            self.speed = self.normal_speed
            self.is_dashing = False
            # ダッシュしていない時はスタミナを回復
            if self.stamina < self.max_stamina:
                self.stamina += 0.8
                if self.stamina > self.max_stamina:
                    self.stamina = self.max_stamina

        # 位置の更新

        # 座標の更新

        self.x += dx * self.speed
        self.y += dy * self.speed

        # 画面外逸脱防止
        if self.x - self.radius < 0:
            self.x = self.radius
        elif self.x + self.radius > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.radius

        if self.y - self.radius < 0:
            self.y = self.radius
        elif self.y + self.radius > SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT - self.radius

        # タイマーの減算処理
        if self.shield_timer > 0:
            self.shield_timer -= 1
        if self.shield_cooldown > 0:
            self.shield_cooldown -= 1
        if self.invincible_timer > 0:
            self.invincible_timer -= 1

    def draw(self, screen: pygame.Surface) -> None:

        """プレイヤーを描画する（ダッシュ中は残像・色変化、無敵中は点滅）"""
        # 無敵時間中は点滅させる（5フレームごとに表示・非表示を切り替え）

        """プレイヤーとシールドの描画"""
        # シールド展開中のエフェクト描画（水色の円枠）
        if self.shield_timer > 0:
            pygame.draw.circle(screen, COLOR_SHIELD, (int(self.x), int(self.y)), self.radius + 8, 3)

        # 被弾無敵時間中の点滅処理

        if self.invincible_timer > 0 and (self.invincible_timer // 5) % 2 == 0:
            return

        # ダッシュ中はプレイヤーの色を少し水色っぽく（または外周を強調）変化させる
        body_color = (0, 200, 255) if self.is_dashing else COLOR_PLAYER

        pygame.draw.circle(screen, body_color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, COLOR_WHITE, (int(self.x), int(self.y)), self.radius, 2)

    def get_pos(self) -> tuple[float, float]:
        """現在座標の取得"""
        return (self.x, self.y)

    def get_hp(self) -> int:
        """現在HPの取得"""
        return self.hp

    def get_stamina(self) -> float:
        """プレイヤーの現在のスタミナを返す"""
        return self.stamina

    def take_damage(self, amount: int) -> None:
        """ダメージ処理（シールド展開中は無効化）"""
        # シールド展開中はダメージを受けない
        if self.shield_timer > 0:
            return

        if self.invincible_timer == 0:
            self.hp -= amount
            if self.hp < 0:
                self.hp = 0
            self.invincible_timer = 60  # 被弾後1秒間の無敵

    def heal(self, amount: int) -> None:
        """HPを回復する（最大HPを超えない）"""
        self.hp = min(self.max_hp, self.hp + amount)        

        


class Enemy:
    """敵キャラクターの移動と描画を管理するクラス"""

    def __init__(self, x: float, y: float) -> None:
        self.x: float = x
        self.y: float = y
        self.radius: int = 12
        self.speed: float = 2.2

    def update(self, player_x: float, player_y: float) -> None:
        """プレイヤーに向かって追従移動"""
        dx: float = player_x - self.x
        dy: float = player_y - self.y
        distance: float = math.hypot(dx, dy)

        if distance > 0:
            dx /= distance
            dy /= distance
            self.x += dx * self.speed
            self.y += dy * self.speed

    def draw(self, screen: pygame.Surface) -> None:
        """敵の描画"""
        pygame.draw.circle(screen, COLOR_ENEMY, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, COLOR_WHITE, (int(self.x), int(self.y)), self.radius, 2)

    def get_pos(self) -> tuple[float, float]:
        return (self.x, self.y)


class Item:
    """アイテムの種類、位置、描画を管理するクラス"""

    def __init__(self, x: float, y: float, item_type: str) -> None:
        self.x: float = x
        self.y: float = y
        self.radius: int = 10
        self.item_type: str = item_type

    def draw(self, screen: pygame.Surface) -> None:
        """アイテムを種類に応じた色で描画する"""
        if self.item_type == "HEAL":
            color = COLOR_HEAL
        else:
            color = COLOR_ITEM_SCORE

        pygame.draw.circle(
            screen, color,
            (int(self.x), int(self.y)), self.radius
        )

    def get_pos(self) -> tuple[float, float]:
        """アイテムの座標を返す"""
        return (self.x, self.y)



class Game:
    """ゲーム全体の管理クラス"""

    def __init__(self) -> None:
        pygame.init()
        self.screen: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("SURVIVAL ARENA - Dash Feature")
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.font: pygame.font.Font = pygame.font.SysFont(None, 36)
        self.large_font: pygame.font.Font = pygame.font.SysFont(None, 64)

        self.reset_game()

    def reset_game(self) -> None:
        """ゲーム状態のリセット"""
        self.player: Player = Player(float(SCREEN_WIDTH / 2), float(SCREEN_HEIGHT / 2))
        self.enemies: list[Enemy] = []
        self.items: list[Item] = []
        self.item_spawn_timer: int = 0
        self.item_score: int = 0
        self.elapsed_frames: int = 0
        self.spawn_timer: int = 0
        self.bombs: int = 3  # 初期所持爆弾数（3回まで使用可能）
        self.game_state: str = "PLAYING"  # "PLAYING", "GAME_OVER", "CLEAR"
        self.game_state: str = "PLAYING"

    def use_bomb(self) -> None:
        """爆弾を発動して画面内の敵を一括排除する"""
        if self.bombs > 0 and self.game_state == "PLAYING" and self.enemies:
            self.enemies.clear()
            self.bombs -= 1

    def run(self) -> None:
        """メインループ"""
        running: bool = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        # SPACEキーで爆弾発動
                        self.use_bomb()
                    elif event.key == pygame.K_r:
                        if self.game_state in ["GAME_OVER", "CLEAR"]:
                            self.reset_game()

            keys = pygame.key.get_pressed()

            if self.game_state == "PLAYING":
                self.player.update(keys)

                # アイテムの出現処理（約10秒ごと）
                self.item_spawn_timer += 1
                if self.item_spawn_timer >= 600:
                    self.item_spawn_timer = 0
                    self.spawn_item()

                self.elapsed_frames += 1
                survived_seconds = self.elapsed_frames // FPS
                if survived_seconds >= TIME_LIMIT:
                    self.game_state = "CLEAR"

                # 一定時間ごと（約1.5秒ごと）に敵を出現させる

                # 一定時間ごと（約1.5秒ごと）に敵を出現させる


                self.spawn_timer += 1
                if self.spawn_timer >= 90:
                    self.spawn_timer = 0
                    self.spawn_enemy()

                px, py = self.player.get_pos()
                for enemy in self.enemies:
                    enemy.update(px, py)

                # アイテムの取得判定
                self.check_item_collisions()

                self.check_collisions()

                if self.player.get_hp() <= 0:
                    self.game_state = "GAME_OVER"

            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def spawn_enemy(self) -> None:
        """画面端からの敵の生成"""
        side = random.randint(0, 3)
        if side == 0:
            x = random.randint(0, SCREEN_WIDTH)
            y = -20
        elif side == 1:
            x = random.randint(0, SCREEN_WIDTH)
            y = SCREEN_HEIGHT + 20
        elif side == 2:
            x = -20
            y = random.randint(0, SCREEN_HEIGHT)
        else:
            x = SCREEN_WIDTH + 20
            y = random.randint(0, SCREEN_HEIGHT)

        self.enemies.append(Enemy(float(x), float(y)))

    def spawn_item(self) -> None:
        """フィールド上にランダムなアイテムを生成する"""
        x = random.randint(30, SCREEN_WIDTH - 30)
        y = random.randint(50, SCREEN_HEIGHT - 30)

        item_type = random.choice(["HEAL", "SCORE"])
        self.items.append(Item(float(x), float(y), item_type))

    def check_item_collisions(self) -> None:
        """プレイヤーとアイテムの接触判定・取得処理"""
        px, py = self.player.get_pos()

        for item in self.items[:]:
            ix, iy = item.get_pos()
            distance = math.hypot(px - ix, py - iy)

            if distance < self.player.radius + item.radius:
                if item.item_type == "HEAL":
                    self.player.heal(30)
                elif item.item_type == "SCORE":
                    self.item_score += 100

                self.items.remove(item)

    def check_collisions(self) -> None:
        """当たり判定"""
        px, py = self.player.get_pos()
        p_radius = self.player.radius

        for enemy in self.enemies:
            ex, ey = enemy.get_pos()
            e_radius = enemy.radius
            distance = math.hypot(px - ex, py - ey)

            if distance < p_radius + e_radius:
                self.player.take_damage(20)

    def draw(self) -> None:
        """画面描画"""
        self.screen.fill(COLOR_BG)

        self.player.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # UI（HP、ボム残数、スコア、残り時間）の描画
        hp_text = self.font.render(f"HP: {self.player.get_hp()}/{self.player.max_hp}", True, COLOR_WHITE)
        self.screen.blit(hp_text, (20, 20))

        bomb_text = self.font.render(f"Bomb: {self.bombs}", True, COLOR_YELLOW)
        self.screen.blit(bomb_text, (200, 20))

        survived_seconds = self.elapsed_frames // FPS
        score_text = self.font.render(f"Score (Time): {survived_seconds}s", True, COLOR_WHITE)
        self.screen.blit(score_text, (380, 20))
        # アイテム描画
        for item in self.items:
            item.draw(self.screen)    


        # UI（HP、スタミナ、スコア、残り時間）の描画
        hp_text = self.font.render(f"HP: {self.player.get_hp()}/{self.player.max_hp}", True, COLOR_WHITE)
        self.screen.blit(hp_text, (20, 20))

        # スタミナ残量の簡易表示（テキスト ＋ バー）
        stamina_val = int(self.player.get_stamina())
        stamina_text = self.font.render(f"Stamina: {stamina_val}", True, COLOR_STAMINA)
        self.screen.blit(stamina_text, (20, 55))

        # UI描画
        hp_text = self.font.render(f"HP: {self.player.get_hp()}/{self.player.max_hp}", True, COLOR_WHITE)
        self.screen.blit(hp_text, (20, 20))

        # シールド機能のUI表示
        if self.player.shield_timer > 0:
            shield_str = f"Shield: ACTIVE ({self.player.shield_timer // FPS + 1}s)"
        elif self.player.shield_cooldown > 0:
            shield_str = f"Shield: CD ({self.player.shield_cooldown // FPS + 1}s)"
        else:
            shield_str = "Shield: READY (Press E)"
        shield_text = self.font.render(shield_str, True, COLOR_SHIELD)
        self.screen.blit(shield_text, (20, 55))


        survived_seconds = self.elapsed_frames // FPS
        total_score = survived_seconds + self.item_score

        score_text = self.font.render(
            f"Score: {total_score}", True, COLOR_WHITE
        )
        self.screen.blit(score_text, (330, 20))

        remaining_seconds = max(0, TIME_LIMIT - survived_seconds)
        time_text = self.font.render(f"Limit: {remaining_seconds}s", True, COLOR_WHITE)
        self.screen.blit(time_text, (750, 20))

        if self.game_state == "GAME_OVER":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.large_font.render("GAME OVER", True, COLOR_RED)
            restart_text = self.font.render("Press R to Restart | Press ESC to Quit", True, COLOR_WHITE)
            
            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

        elif self.game_state == "CLEAR":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))

            clear_text = self.large_font.render("CLEAR!", True, COLOR_YELLOW)
            restart_text = self.font.render("Press R to Restart | Press ESC to Quit", True, COLOR_WHITE)
            
            self.screen.blit(clear_text, (SCREEN_WIDTH // 2 - clear_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

        pygame.display.flip()


if __name__ == "__main__":
    game = Game()
    game.run()