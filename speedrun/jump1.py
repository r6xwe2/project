import pygame
import os
import random
import math

pygame.init()

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

font_path = "/home/r6x/바탕화면/project/font.ttf"
try:
    font = pygame.font.Font(font_path, 74)
    menu_font = pygame.font.Font(font_path, 50)
    small_font = pygame.font.Font(font_path, 30)
except FileNotFoundError:
    print("지정된 한글 폰트 파일을 찾을 수 없습니다. 시스템 기본 폰트로 대체합니다.")
    print("한글이 깨져 보일 수 있습니다. 'font_path' 변수를 수정해주세요.")
    font = pygame.font.Font(None, 74)
    menu_font = pygame.font.Font(None, 50)
    small_font = pygame.font.Font(None, 30)

game_state = "MENU"

menu_options = ["플레이", "나가기"]
selected_menu_option = 0

player_width = 40
player_height = 40
player_move_speed = 5
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
    except pygame.error as e:
        print("기본 플레이어 이미지 로드 실패. 기본 캐릭터로 대체합니다.")
    
    try:
        if os.path.exists(player_image_path_fast):
            player_image_fast = pygame.image.load(player_image_path_fast).convert_alpha()
            player_image_fast = pygame.transform.scale(player_image_fast, (player_width, player_height))
    except pygame.error as e:
        print("빠른 플레이어 이미지 로드 실패. 빠른 캐릭터 이미지도 기본으로 대체합니다.")

load_player_images()

background_image = None
try:
    if os.path.exists("background.png"):
        background_image = pygame.image.load("background.png").convert()
        background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
except pygame.error as e:
    print("배경 이미지를 불러올 수 없어요. 배경색으로 대체합니다.")

obstacle_width = 30
obstacle_height = 30
obstacle_min_speed = 3
obstacle_max_speed = 10
fast_obstacle_threshold = 6 

obstacles = [] 

obstacle_spawn_timer = pygame.time.get_ticks()
obstacle_spawn_delay_min = 300 
obstacle_spawn_delay_max = 800
next_spawn_time = pygame.time.get_ticks() + random.randint(obstacle_spawn_delay_min, obstacle_spawn_delay_max)

game_over_start_time = 0
game_over_animation_duration = 3000
game_over_initial_font_size = 10
game_over_final_font_size = 100

clock = pygame.time.Clock()
FPS = 60

pending_game_over = False
game_over_reason = ""


def reset_game():
    global player_x, player_y, player_speed_x, player_speed_y, player_rect, game_state
    global obstacles, obstacle_spawn_timer, next_spawn_time
    global game_over_start_time, pending_game_over, game_over_reason

    player_x = screen_width // 2 - player_width // 2
    player_y = screen_height // 2 - player_height // 2
    player_speed_x = 0
    player_speed_y = 0
    player_rect.topleft = (player_x, player_y)
    
    obstacles = []
    obstacle_spawn_timer = pygame.time.get_ticks()
    next_spawn_time = pygame.time.get_ticks() + random.randint(obstacle_spawn_delay_min, obstacle_spawn_delay_max)
    game_over_start_time = 0
    pending_game_over = False
    game_over_reason = ""

    game_state = "PLAYING"

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if game_state == "MENU":
                if event.key == pygame.K_UP:
                    selected_menu_option = (selected_menu_option - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
                    selected_menu_option = (selected_menu_option + 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:
                    if selected_menu_option == 0:
                        reset_game()
                    elif selected_menu_option == 1:
                        running = False
            
            elif game_state == "PLAYING":
                if event.key == pygame.K_LEFT:
                    player_speed_x = -player_move_speed
                elif event.key == pygame.K_RIGHT:
                    player_speed_x = player_move_speed
                elif event.key == pygame.K_UP:
                    player_speed_y = -player_move_speed
                elif event.key == pygame.K_DOWN:
                    player_speed_y = player_move_speed
            
            elif game_state == "GAME_OVER":
                if pygame.time.get_ticks() - game_over_start_time >= game_over_animation_duration:
                    if event.key == pygame.K_RETURN:
                        reset_game()

        if event.type == pygame.KEYUP and game_state == "PLAYING":
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                player_speed_x = 0
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                player_speed_y = 0

    screen.fill(BLACK)

    if game_state == "MENU":
        title_text = font.render("피해라! 스피드 서바이벌", True, WHITE)
        title_rect = title_text.get_rect(center=(screen_width // 2, screen_height // 4))
        screen.blit(title_text, title_rect)

        for i, option in enumerate(menu_options):
            color = GREEN if i == selected_menu_option else WHITE
            option_text = menu_font.render(option, True, color)
            option_rect = option_text.get_rect(center=(screen_width // 2, screen_height // 2 + i * 70))
            screen.blit(option_text, option_rect)

    elif game_state == "PLAYING":
        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill(SKY_BLUE)
        
        player_rect.x += player_speed_x
        player_rect.y += player_speed_y

        if not (0 <= player_rect.left and player_rect.right <= screen_width and
                0 <= player_rect.top and player_rect.bottom <= screen_height):
            pending_game_over = True
            game_over_reason = "앗! 벽에 부딪혀서 게임 오버!"
        
        player_display_image = player_image_normal
        player_display_image_rect_fallback = False
            
        is_fast_obstacle_on_screen = False

        current_time = pygame.time.get_ticks()
        if current_time >= next_spawn_time:
            spawn_side = random.randint(0, 2)
            main_speed = random.randint(obstacle_min_speed, obstacle_max_speed)
            
            new_obstacle_rect = None
            
            if spawn_side == 0:
                start_x = random.randint(0, screen_width - obstacle_width)
                start_y = -obstacle_height
                new_obstacle_rect = pygame.Rect(start_x, start_y, obstacle_width, obstacle_height)
                obstacles.append({'rect': new_obstacle_rect, 'speed_x': random.uniform(-1.5, 1.5), 'speed_y': main_speed, 'initial_main_speed': main_speed})
            elif spawn_side == 1:
                start_x = -obstacle_width
                start_y = random.randint(0, screen_height - obstacle_height)
                new_obstacle_rect = pygame.Rect(start_x, start_y, obstacle_width, obstacle_height)
                obstacles.append({'rect': new_obstacle_rect, 'speed_x': main_speed, 'speed_y': random.uniform(-1.5, 1.5), 'initial_main_speed': main_speed})
            else:
                start_x = screen_width
                start_y = random.randint(0, screen_height - obstacle_height)
                new_obstacle_rect = pygame.Rect(start_x, start_y, obstacle_width, obstacle_height)
                obstacles.append({'rect': new_obstacle_rect, 'speed_x': -main_speed, 'speed_y': random.uniform(-1.5, 1.5), 'initial_main_speed': main_speed})
            
            next_spawn_time = current_time + random.randint(obstacle_spawn_delay_min, obstacle_spawn_delay_max)

        obstacles_to_keep = []
        for obstacle in obstacles:
            obstacle['rect'].x += obstacle['speed_x']
            obstacle['rect'].y += obstacle['speed_y']
            
            if player_rect.colliderect(obstacle['rect']):
                pending_game_over = True
                game_over_reason = "따끔! 가시에 찔려서 게임 오버!"
            
            if obstacle['initial_main_speed'] >= fast_obstacle_threshold:
                is_fast_obstacle_on_screen = True

            if 0 - obstacle_width * 2 < obstacle['rect'].x < screen_width + obstacle_width * 2 and \
               0 - obstacle_height * 2 < obstacle['rect'].y < screen_height + obstacle_height * 2:
                obstacles_to_keep.append(obstacle)
                pygame.draw.rect(screen, GRAY, obstacle['rect'])
        
        obstacles = obstacles_to_keep

        if is_fast_obstacle_on_screen and player_image_fast:
            player_display_image = player_image_fast
        elif player_image_normal:
            player_display_image = player_image_normal
        else: 
             player_display_image_rect_fallback = True

        if not player_display_image_rect_fallback:
            screen.blit(player_display_image, player_rect)
        else:
            pygame.draw.rect(screen, RED, player_rect)
            
        if pending_game_over:
            game_state = "GAME_OVER"
            game_over_start_time = pygame.time.get_ticks()
            print(game_over_reason)


    elif game_state == "GAME_OVER":
        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill(BLACK)
        
        elapsed_time = pygame.time.get_ticks() - game_over_start_time
        animation_progress = min(elapsed_time / game_over_animation_duration, 1.0)

        current_font_size = int(game_over_initial_font_size + (game_over_final_font_size - game_over_initial_font_size) * animation_progress)
        current_font_size = max(current_font_size, 1) 

        color_time_factor = 0.005 
        
        r = int((math.sin(elapsed_time * color_time_factor + 0) * 127 + 128))
        g = int((math.sin(elapsed_time * color_time_factor + 2 * math.pi / 3) * 127 + 128))
        b = int((math.sin(elapsed_time * color_time_factor + 4 * math.pi / 3) * 127 + 128))
        current_color = (r, g, b)

        try:
            game_over_animated_font = pygame.font.Font(font_path, current_font_size)
            game_over_text = game_over_animated_font.render("게임 오버!", True, current_color)
        except Exception:
            game_over_animated_font = pygame.font.Font(None, current_font_size)
            game_over_text = game_over_animated_font.render("게임 오버!", True, current_color)

        game_over_rect = game_over_text.get_rect(center=(screen_width // 2, screen_height // 3))
        screen.blit(game_over_text, game_over_rect)

        if animation_progress > 0.7:
            restart_text = small_font.render("Enter 키를 눌러 다시 시작", True, WHITE)
            restart_rect = restart_text.get_rect(center=(screen_width // 2, screen_height // 3 + 100))
            screen.blit(restart_text, restart_rect)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
