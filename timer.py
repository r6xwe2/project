import pygame
import os
import time
import math

pygame.init()

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("10초를 맞춰라!")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (150, 150, 150)

font_path = "C:/font.ttf"
try:
    title_font = pygame.font.Font(font_path, 70)
    menu_font = pygame.font.Font(font_path, 40)
    instruction_font = pygame.font.Font(font_path, 35)
    result_font = pygame.font.Font(font_path, 50)
    small_font = pygame.font.Font(font_path, 25)
    timer_font = pygame.font.Font(font_path, 100)
except FileNotFoundError:
    print("지정된 한글 폰트 파일을 찾을 수 없습니다. 시스템 기본 폰트로 대체합니다.")
    print("한글이 깨져 보일 수 있습니다. 'font_path' 변수를 수정해주세요.")
    title_font = pygame.font.Font(None, 70)
    menu_font = pygame.font.Font(None, 40)
    instruction_font = pygame.font.Font(None, 35)
    result_font = pygame.font.Font(None, 50)
    small_font = pygame.font.Font(None, 25)
    timer_font = pygame.font.Font(None, 100)

GAME_STATE_MENU = "MENU"
GAME_STATE_PLAYING = "PLAYING"
GAME_STATE_RESULT = "RESULT"

game_state = GAME_STATE_MENU

start_time = 0.0
current_time_display = 0.0
elapsed_time_final = 0.0
target_time = 10.0 # 목표 시간 설정
difference = 0.0
best_score_diff = float('inf')

best_score_text = ""

def start_new_game_round():
    global game_state, start_time, current_time_display, elapsed_time_final, difference
    
    start_time = time.time()
    current_time_display = 0.0
    elapsed_time_final = 0.0
    difference = 0.0
    game_state = GAME_STATE_PLAYING

running = True
clock = pygame.time.Clock()
FPS = 60

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if game_state == GAME_STATE_MENU:
                    start_new_game_round()
                elif game_state == GAME_STATE_PLAYING:
                    end_time = time.time()
                    elapsed_time_final = end_time - start_time
                    difference = abs(elapsed_time_final - target_time)
                    
                    if difference < best_score_diff:
                        best_score_diff = difference
                        best_score_text = f"최고 기록: {best_score_diff:05.2f}초 차이" # 최고 기록 포맷 변경
                    
                    game_state = GAME_STATE_RESULT
                elif game_state == GAME_STATE_RESULT:
                    start_new_game_round()

    screen.fill(BLACK)

    if game_state == GAME_STATE_MENU:
        title_surface = title_font.render("10초를 맞춰라!", True, WHITE)
        title_rect = title_surface.get_rect(center=(screen_width // 2, screen_height // 3))
        screen.blit(title_surface, title_rect)

        instruction_surface = menu_font.render("시작하려면 Enter 키를 누르세요!", True, GREEN)
        instruction_rect = instruction_surface.get_rect(center=(screen_width // 2, screen_height // 2))
        screen.blit(instruction_surface, instruction_rect)

        if best_score_diff != float('inf'):
            best_score_surface = small_font.render(best_score_text, True, YELLOW)
            best_score_rect = best_score_surface.get_rect(center=(screen_width // 2, screen_height * 2 // 3))
            screen.blit(best_score_surface, best_score_rect)

    elif game_state == GAME_STATE_PLAYING:
        current_time_display = time.time() - start_time

        timer_text_color = WHITE
        if current_time_display > target_time + 1 or current_time_display < target_time - 1:
            timer_text_color = RED
        elif current_time_display > target_time - 1 and current_time_display < target_time + 1:
             timer_text_color = GREEN

        # 타이머 숫자 포맷 변경: 00.00 형식으로
        timer_surface = timer_font.render(f"{current_time_display:05.2f}초", True, timer_text_color)
        timer_rect = timer_surface.get_rect(center=(screen_width // 2, screen_height // 2 - 50))
        screen.blit(timer_surface, timer_rect)

        instruction_surface = instruction_font.render("10초가 되면 Enter 키를 누르세요!", True, GRAY)
        instruction_rect = instruction_surface.get_rect(center=(screen_width // 2, screen_height // 2 + 50))
        screen.blit(instruction_surface, instruction_rect)

    elif game_state == GAME_STATE_RESULT:
        result_title_surface = title_font.render("결과!", True, WHITE)
        result_title_rect = result_title_surface.get_rect(center=(screen_width // 2, screen_height // 4))
        screen.blit(result_title_surface, result_title_rect)

        # 결과 시간 포맷 변경: 00.00 형식으로
        time_counted_surface = result_font.render(f"당신이 센 시간: {elapsed_time_final:05.2f}초", True, BLUE)
        time_counted_rect = time_counted_surface.get_rect(center=(screen_width // 2, screen_height // 2 - 50))
        screen.blit(time_counted_surface, time_counted_rect)

        # 차이 시간 포맷 변경: 00.00 형식으로
        difference_surface = result_font.render(f"10초와 {difference:05.2f}초 차이!", True, RED)
        difference_rect = difference_surface.get_rect(center=(screen_width // 2, screen_height // 2 + 20))
        screen.blit(difference_surface, difference_rect)

        best_score_surface = small_font.render(best_score_text, True, YELLOW)
        best_score_rect = best_score_surface.get_rect(center=(screen_width // 2, screen_height // 2 + 100))
        screen.blit(best_score_surface, best_score_rect)

        restart_instruction_surface = small_font.render("다시 플레이하려면 Enter 키를 누르세요.", True, GREEN)
        restart_instruction_rect = restart_instruction_surface.get_rect(center=(screen_width // 2, screen_height - 50))
        screen.blit(restart_instruction_surface, restart_instruction_rect)
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()