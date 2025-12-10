import pygame
import os
import random
import math
import json
from datetime import datetime

pygame.init()

# =========================
# 화면 설정
# =========================
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("피해라! 스피드 서바이벌")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (100, 100, 100)
SKY_BLUE = (135, 206, 235)

font_path = "./font.ttf"
try:
    font = pygame.font.Font(font_path, 74)
    menu_font = pygame.font.Font(font_path, 50)
    small_font = pygame.font.Font(font_path, 30)
except FileNotFoundError:
    font = pygame.font.Font(None, 74)
    menu_font = pygame.font.Font(None, 50)
    small_font = pygame.font.Font(None, 30)

# =========================
# 게임 상태
# =========================
game_state = "MENU"
menu_options = ["플레이", "최고 기록", "옵션", "나가기"]
selected_menu_option = 0

# =========================
# 플레이어 설정
# =========================
player_width = 40
player_height = 40
player_move_speed = 7
player_x = screen_width // 2 - player_width // 2
player_y = screen_height // 2 - player_height // 2
player_speed_x = 0
player_speed_y = 0
player_rect = pygame.Rect(player_x, player_y, player_width, player_height)

player_image_normal = None
player_image_fast = None
player_image_path_normal = "player_character.png"
player_image_path_fast = "player_character_fast.png"

def load_player_images():
    global player_image_normal, player_image_fast
    try:
        if os.path.exists(player_image_path_normal):
            player_image_normal = pygame.image.load(player_image_path_normal).convert_alpha()
            player_image_normal = pygame.transform.scale(player_image_normal, (player_width, player_height))
    except pygame.error:
        pass
    try:
        if os.path.exists(player_image_path_fast):
            player_image_fast = pygame.image.load(player_image_path_fast).convert_alpha()
            player_image_fast = pygame.transform.scale(player_image_fast, (player_width, player_height))
    except pygame.error:
        pass

load_player_images()

# =========================
# 배경
# =========================
background_image = None
try:
    if os.path.exists("background.png"):
        background_image = pygame.image.load("background.png").convert()
        background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
except pygame.error:
    pass

# =========================
# 장애물
# =========================
obstacle_width = 30
obstacle_height = 30
obstacle_min_speed = 6
obstacle_max_speed = 14
fast_obstacle_threshold = 6
obstacles = []
obstacle_spawn_timer = pygame.time.get_ticks()
obstacle_spawn_delay_min = 300
obstacle_spawn_delay_max = 800
next_spawn_time = pygame.time.get_ticks() + random.randint(obstacle_spawn_delay_min, obstacle_spawn_delay_max)

# =========================
# 게임 오버
# =========================
game_over_start_time = 0
game_over_animation_duration = 3000
game_over_initial_font_size = 10
game_over_final_font_size = 100
pending_game_over = False
game_over_reason = ""

# =========================
# 궁극기 시스템
# =========================
ult_charge = 0
ult_charge_max = 100
ult_active = False
ult_duration = 5000  # 5초
ult_start_time = 0
ult_gain_per_second = 15  # 초당 충전량

# =========================
# 옵션: 키 설정
# =========================
use_wasd = True
use_arrows = True

# =========================
# 기록 관리
# =========================
BEST_FILE = "best_times.json"
PLAY_FILE = "play_times.json"
best_times = []
play_times = []

if os.path.exists(BEST_FILE):
    try:
        with open(BEST_FILE, "r") as f:
            best_times = json.load(f)
    except:
        best_times = []

if os.path.exists(PLAY_FILE):
    try:
        with open(PLAY_FILE, "r") as f:
            play_times = json.load(f)
    except:
        play_times = []

# =========================
# 게임 초기화
# =========================
def reset_game():
    global player_x, player_y, player_speed_x, player_speed_y, player_rect
    global obstacles, next_spawn_time
    global pending_game_over, game_over_reason, game_over_start_time
    global ult_charge, ult_active, ult_start_time

    player_x = screen_width // 2 - player_width // 2
    player_y = screen_height // 2 - player_height // 2
    player_speed_x = 0
    player_speed_y = 0
    player_rect.topleft = (player_x, player_y)

    obstacles = []
    next_spawn_time = pygame.time.get_ticks() + random.randint(obstacle_spawn_delay_min, obstacle_spawn_delay_max)
    pending_game_over = False
    game_over_reason = ""
    game_over_start_time = 0

    ult_charge = 0
    ult_active = False
    ult_start_time = 0

# =========================
# 무지개색 그라데이션
# =========================
def rainbow_color(pos):
    r = int((math.sin(pos * math.pi * 2) * 127 + 128) * 0.6 + 100)
    g = int((math.sin(pos * math.pi * 2 + 2) * 127 + 128) * 0.6 + 100)
    b = int((math.sin(pos * math.pi * 2 + 4) * 127 + 128) * 0.6 + 100)
    return (r, g, b)

# =========================
# 기록 표시 페이지 관리
# =========================
best_page = 0
play_page = 0
records_per_page = 8

# =========================
# 메인 루프
# =========================
clock = pygame.time.Clock()
FPS = 60
running = True
start_time = 0

while running:
    dt = clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # =========================
            # 메뉴 조작
            # =========================
            if game_state in ["MENU", "OPTIONS", "BEST_TIMES"]:
                if event.key == pygame.K_UP:
                    selected_menu_option = (selected_menu_option - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
                    selected_menu_option = (selected_menu_option + 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:
                    if game_state == "MENU":
                        if selected_menu_option == 0:
                            reset_game()
                            game_state = "PLAYING"
                            start_time = pygame.time.get_ticks()
                        elif selected_menu_option == 1:
                            game_state = "BEST_TIMES"
                            selected_menu_option = 0
                        elif selected_menu_option == 2:
                            game_state = "OPTIONS"
                            selected_menu_option = 0
                        elif selected_menu_option == 3:
                            running = False
                    elif game_state == "BEST_TIMES":
                        game_state = "MENU"
                    elif game_state == "OPTIONS":
                        if selected_menu_option == 0:
                            use_wasd = True
                            use_arrows = False
                        elif selected_menu_option == 1:
                            use_wasd = False
                            use_arrows = True
                        game_state = "MENU"

                elif event.key == pygame.K_LEFT and game_state == "BEST_TIMES":
                    if selected_menu_option == 0:
                        best_page = max(0, best_page - 1)
                    elif selected_menu_option == 1:
                        play_page = max(0, play_page - 1)
                elif event.key == pygame.K_RIGHT and game_state == "BEST_TIMES":
                    if selected_menu_option == 0:
                        best_page += 1
                    elif selected_menu_option == 1:
                        play_page += 1

            # =========================
            # 게임 플레이 키
            # =========================
            if game_state == "PLAYING":
                if use_arrows:
                    if event.key == pygame.K_LEFT:
                        player_speed_x = -player_move_speed
                    elif event.key == pygame.K_RIGHT:
                        player_speed_x = player_move_speed
                    elif event.key == pygame.K_UP:
                        player_speed_y = -player_move_speed
                    elif event.key == pygame.K_DOWN:
                        player_speed_y = player_move_speed
                if use_wasd:
                    if event.key == pygame.K_a:
                        player_speed_x = -player_move_speed
                    elif event.key == pygame.K_d:
                        player_speed_x = player_move_speed
                    elif event.key == pygame.K_w:
                        player_speed_y = -player_move_speed
                    elif event.key == pygame.K_s:
                        player_speed_y = player_move_speed

            # =========================
            # 게임오버에서 엔터 → 메인 메뉴
            # =========================
            if game_state == "GAME_OVER":
                if pygame.time.get_ticks() - game_over_start_time >= game_over_animation_duration:
                    game_state = "MENU"

        if event.type == pygame.KEYUP and game_state == "PLAYING":
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d]:
                player_speed_x = 0
            if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_w, pygame.K_s]:
                player_speed_y = 0

    # =========================
    # 배경
    # =========================
    if game_state in ["MENU", "OPTIONS", "BEST_TIMES", "GAME_OVER"]:
        screen.fill(BLACK)
    else:
        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill(SKY_BLUE)

    # =========================
    # 메뉴
    # =========================
    if game_state == "MENU":
        title_text = font.render("피해라! 스피드 서바이벌", True, WHITE)
        screen.blit(title_text, title_text.get_rect(center=(screen_width//2, screen_height//4)))
        for i, option in enumerate(menu_options):
            color = GREEN if i == selected_menu_option else WHITE
            option_text = menu_font.render(option, True, color)
            screen.blit(option_text, option_text.get_rect(center=(screen_width//2, screen_height//2 + i*70)))

    elif game_state == "OPTIONS":
        option_list = ["WASD 이동", "방향키 이동"]
        for i, option in enumerate(option_list):
            color = GREEN if i == selected_menu_option else WHITE
            option_text = menu_font.render(option, True, color)
            screen.blit(option_text, option_text.get_rect(center=(screen_width//2, screen_height//3 + i*70)))
        back_text = small_font.render("Enter 키 선택 후 메뉴로 돌아가기", True, WHITE)
        screen.blit(back_text, back_text.get_rect(center=(screen_width//2, screen_height-50)))

    # =========================
    # 기록 확인 화면
    # =========================
    elif game_state == "BEST_TIMES":
        # 화면 제목
        title_text = font.render("기록 확인", True, WHITE)
        screen.blit(title_text, title_text.get_rect(center=(screen_width//2, 60)))

        # 탭 옵션
        option_list = ["최고 기록"]
        tab_start_y = 150
        tab_gap = 60
        for i, option in enumerate(option_list):
            color = GREEN if i == selected_menu_option else WHITE
            screen.blit(menu_font.render(option, True, color), (50, tab_start_y + i * tab_gap))

        # 기록 표시 (최고 기록만 갱신된 기록으로 표시)
        display_list = best_times[-8:]  # 최신 8개의 최고 기록만 표시
        page = best_page
        start_idx = page * records_per_page
        end_idx = start_idx + records_per_page

        record_start_y = tab_start_y + len(option_list) * tab_gap + 20
        for i, record in enumerate(display_list[start_idx:end_idx]):
            t, dt = record
            try:
                t = float(t)
            except:
                t = 0.0
            rec_text = small_font.render(f"{start_idx + i + 1}. {t:.2f}s - {dt}", True, WHITE)
            screen.blit(rec_text, (50, record_start_y + i * 35))

        back_text = small_font.render("Enter 키를 눌러 뒤로", True, WHITE)
        screen.blit(back_text, back_text.get_rect(center=(screen_width//2, screen_height-50)))

    # =========================
    # 게임 플레이
    # =========================
    elif game_state == "PLAYING":
        # 궁극기 충전
        if not ult_active:
            ult_charge += ult_gain_per_second / FPS
            if ult_charge >= ult_charge_max:
                ult_charge = ult_charge_max
                ult_active = True
                ult_start_time = pygame.time.get_ticks()
        if ult_active:
            if pygame.time.get_ticks() - ult_start_time >= ult_duration:
                ult_active = False
                ult_charge = 0

        # 플레이어 이동
        player_rect.x += player_speed_x
        player_rect.y += player_speed_y

        # 벽 충돌
        if not (0 <= player_rect.left <= screen_width - player_width) or not (0 <= player_rect.top <= screen_height - player_height):
            pending_game_over = True
            game_over_reason = "벽에 부딪힘!"

        player_display_image = player_image_normal
        is_fast_obstacle_on_screen = False
        current_time = pygame.time.get_ticks()

        # 장애물 생성
        if current_time >= next_spawn_time:
            spawn_side = random.randint(0, 2)
            main_speed = random.randint(obstacle_min_speed, obstacle_max_speed)
            if spawn_side == 0:
                rect = pygame.Rect(random.randint(0, screen_width - obstacle_width), -obstacle_height, obstacle_width, obstacle_height)
                obstacles.append({'rect': rect, 'speed_x': random.uniform(-1.5, 1.5), 'speed_y': main_speed, 'initial_main_speed': main_speed})
            elif spawn_side == 1:
                rect = pygame.Rect(-obstacle_width, random.randint(0, screen_height - obstacle_height), obstacle_width, obstacle_height)
                obstacles.append({'rect': rect, 'speed_x': main_speed, 'speed_y': random.uniform(-1.5, 1.5), 'initial_main_speed': main_speed})
            else:
                rect = pygame.Rect(screen_width, random.randint(0, screen_height - obstacle_height), obstacle_width, obstacle_height)
                obstacles.append({'rect': rect, 'speed_x': -main_speed, 'speed_y': random.uniform(-1.5, 1.5), 'initial_main_speed': main_speed})
            next_spawn_time = current_time + random.randint(obstacle_spawn_delay_min, obstacle_spawn_delay_max)

        # 장애물 이동 및 충돌
        new_obstacles = []
        for obstacle in obstacles:
            obstacle['rect'].x += obstacle['speed_x']
            obstacle['rect'].y += obstacle['speed_y']

            if player_rect.colliderect(obstacle['rect']):
                if ult_active:
                    continue
                else:
                    pending_game_over = True
                    game_over_reason = "블록에 닿아서 사망!"
                    continue

            if obstacle['initial_main_speed'] >= fast_obstacle_threshold:
                is_fast_obstacle_on_screen = True

            if -50 < obstacle['rect'].x < screen_width + 50 and -50 < obstacle['rect'].y < screen_height + 50:
                new_obstacles.append(obstacle)
                pygame.draw.rect(screen, GRAY, obstacle['rect'])
        obstacles = new_obstacles

        # 플레이어 표시
        if is_fast_obstacle_on_screen and player_image_fast:
            player_display_image = player_image_fast
        if player_display_image:
            screen.blit(player_display_image, player_rect)
        else:
            pygame.draw.rect(screen, RED, player_rect)

        # 궁극기 바
        bar_x, bar_y, bar_w, bar_h = 20, 20, 200, 20
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_w, bar_h), 2)
        for i in range(bar_w):
            color = rainbow_color(i / bar_w)
            if i < int(bar_w * (ult_charge / ult_charge_max)):
                pygame.draw.line(screen, color, (bar_x + i, bar_y), (bar_x + i, bar_y + bar_h))

        # 궁극기 타이머
        if ult_active:
            remain = max(0, (ult_duration - (pygame.time.get_ticks() - ult_start_time)) / 1000)
            timer_text = small_font.render(f"남은 시간: {remain:.1f}s", True, RED)
            screen.blit(timer_text, (bar_x, bar_y + 28))

        # 초시계 표시 (예쁜 UI)
        elapsed_sec = (pygame.time.get_ticks() - start_time) / 1000
        elapsed_text = f"{elapsed_sec:.2f}s"
        # 동그란 테두리 안에 표시
        pygame.draw.circle(screen, WHITE, (screen_width - 80, 40), 50, 3)
        timer_render = small_font.render(elapsed_text, True, WHITE)
        screen.blit(timer_render, timer_render.get_rect(center=(screen_width - 80, 40)))

        # 게임오버 처리
        if pending_game_over:
            game_state = "GAME_OVER"
            game_over_start_time = pygame.time.get_ticks()
            # 기록 저장
            best_times.append((elapsed_sec, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            play_times.append((elapsed_sec, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            with open(BEST_FILE, "w") as f:
                json.dump(best_times, f)
            with open(PLAY_FILE, "w") as f:
                json.dump(play_times, f)

    # =========================
    # 게임 오버
    # =========================
    elif game_state == "GAME_OVER":
        screen.fill(BLACK)
        game_over_text = font.render("게임 오버!", True, RED)
        screen.blit(game_over_text, game_over_text.get_rect(center=(screen_width // 2, screen_height // 2 - 40)))

        game_over_reason_text = small_font.render(game_over_reason, True, WHITE)
        screen.blit(game_over_reason_text, game_over_reason_text.get_rect(center=(screen_width // 2, screen_height // 2 + 20)))

        retry_text = small_font.render("엔터로 메인 메뉴로 돌아가기", True, WHITE)
        screen.blit(retry_text, retry_text.get_rect(center=(screen_width // 2, screen_height // 2 + 70)))

    pygame.display.update()

pygame.quit()
