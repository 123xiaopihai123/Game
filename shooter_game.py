import random
import sys
from dataclasses import dataclass

import pygame

# ---------------------------
# Config
# ---------------------------
WIDTH, HEIGHT = 900, 600
FPS = 60
PLAYER_SPEED = 6
BULLET_SPEED = 10
ENEMY_MIN_SPEED = 2
ENEMY_MAX_SPEED = 5
ENEMY_SPAWN_EVERY_MS = 650
MAX_LIVES = 3


@dataclass
class Bullet:
    x: int
    y: int
    radius: int = 4

    def update(self) -> None:
        self.y -= BULLET_SPEED

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, (255, 220, 80), (self.x, self.y), self.radius)

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)


@dataclass
class Enemy:
    x: int
    y: int
    w: int
    h: int
    speed: int

    def update(self) -> None:
        self.y += self.speed

    def draw(self, surface: pygame.Surface) -> None:
        body = pygame.Rect(self.x, self.y, self.w, self.h)
        pygame.draw.rect(surface, (210, 50, 50), body, border_radius=6)
        pygame.draw.rect(surface, (255, 120, 120), body, 2, border_radius=6)

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.w, self.h)


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Python 射击小游戏")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("Microsoft YaHei", 28)
        self.big_font = pygame.font.SysFont("Microsoft YaHei", 46)

        self.reset()

    def reset(self) -> None:
        self.player_w, self.player_h = 60, 28
        self.player_x = WIDTH // 2 - self.player_w // 2
        self.player_y = HEIGHT - 50

        self.bullets: list[Bullet] = []
        self.enemies: list[Enemy] = []

        self.score = 0
        self.lives = MAX_LIVES
        self.game_over = False

        self.last_spawn = pygame.time.get_ticks()

    def spawn_enemy(self) -> None:
        w = random.randint(36, 62)
        h = random.randint(24, 40)
        x = random.randint(0, WIDTH - w)
        y = -h
        speed = random.randint(ENEMY_MIN_SPEED, ENEMY_MAX_SPEED)
        self.enemies.append(Enemy(x, y, w, h, speed))

    def handle_input(self) -> None:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player_x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player_x += PLAYER_SPEED

        self.player_x = max(0, min(WIDTH - self.player_w, self.player_x))

    def shoot(self) -> None:
        bullet_x = self.player_x + self.player_w // 2
        bullet_y = self.player_y
        self.bullets.append(Bullet(bullet_x, bullet_y))

    def update(self) -> None:
        now = pygame.time.get_ticks()
        if now - self.last_spawn >= ENEMY_SPAWN_EVERY_MS:
            self.spawn_enemy()
            self.last_spawn = now

        for bullet in self.bullets:
            bullet.update()
        self.bullets = [b for b in self.bullets if b.y > -10]

        for enemy in self.enemies:
            enemy.update()

        # 敌机越界 -> 扣血
        active_enemies: list[Enemy] = []
        for enemy in self.enemies:
            if enemy.y > HEIGHT:
                self.lives -= 1
            else:
                active_enemies.append(enemy)
        self.enemies = active_enemies

        # 子弹碰撞敌机
        new_bullets: list[Bullet] = []
        for bullet in self.bullets:
            hit = False
            survivors: list[Enemy] = []
            for enemy in self.enemies:
                if bullet.rect.colliderect(enemy.rect):
                    hit = True
                    self.score += 10
                else:
                    survivors.append(enemy)
            self.enemies = survivors
            if not hit:
                new_bullets.append(bullet)
        self.bullets = new_bullets

        # 敌机撞到玩家 -> 直接结束
        player_rect = pygame.Rect(self.player_x, self.player_y, self.player_w, self.player_h)
        for enemy in self.enemies:
            if enemy.rect.colliderect(player_rect):
                self.lives = 0
                break

        if self.lives <= 0:
            self.game_over = True

    def draw_background(self) -> None:
        self.screen.fill((12, 18, 35))

        # 简单星空背景
        for i in range(0, WIDTH, 45):
            pygame.draw.circle(self.screen, (45, 55, 90), ((i * 31) % WIDTH, (i * 17) % HEIGHT), 2)

    def draw_player(self) -> None:
        body = pygame.Rect(self.player_x, self.player_y, self.player_w, self.player_h)
        nose = [(self.player_x + self.player_w // 2, self.player_y - 12), (self.player_x + 10, self.player_y + 6), (self.player_x + self.player_w - 10, self.player_y + 6)]

        pygame.draw.rect(self.screen, (70, 170, 255), body, border_radius=7)
        pygame.draw.polygon(self.screen, (120, 210, 255), nose)

    def draw_hud(self) -> None:
        score_text = self.font.render(f"得分: {self.score}", True, (240, 240, 240))
        lives_text = self.font.render(f"生命: {self.lives}", True, (240, 240, 240))
        tip_text = self.font.render("操作: A/D 或 ←/→ 移动，空格射击", True, (190, 205, 240))

        self.screen.blit(score_text, (18, 10))
        self.screen.blit(lives_text, (18, 42))
        self.screen.blit(tip_text, (18, HEIGHT - 40))

    def draw_game_over(self) -> None:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        title = self.big_font.render("游戏结束", True, (255, 230, 230))
        score = self.font.render(f"最终得分: {self.score}", True, (255, 255, 255))
        hint = self.font.render("按 R 重新开始，按 ESC 退出", True, (255, 255, 255))

        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 90))
        self.screen.blit(score, (WIDTH // 2 - score.get_width() // 2, HEIGHT // 2 - 25))
        self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 18))

    def draw(self) -> None:
        self.draw_background()
        self.draw_player()

        for bullet in self.bullets:
            bullet.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)

        self.draw_hud()

        if self.game_over:
            self.draw_game_over()

        pygame.display.flip()

    def run(self) -> None:
        while True:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit(0)

                    if self.game_over:
                        if event.key == pygame.K_r:
                            self.reset()
                    elif event.key == pygame.K_SPACE:
                        self.shoot()

            if not self.game_over:
                self.handle_input()
                self.update()

            self.draw()


if __name__ == "__main__":
    Game().run()
