import pygame
import sys
from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien

def run_game():
    pygame.init()
    ai_settings = Settings()
    screen = pygame.display.set_mode((ai_settings.screen_width, ai_settings.screen_height))
    pygame.display.set_caption("Alien Invasion")

    # Создание экземпляра корабля, пуль и пришельцев
    ship = Ship(ai_settings, screen)
    bullets = pygame.sprite.Group()
    aliens = pygame.sprite.Group()

    # Количество рядов
    rows = 5  # Начальное количество рядов

    # Создание флота пришельцев
    create_fleet(ai_settings, screen, ship, aliens, rows)

    # Основной цикл игры
    while True:
        check_events(ai_settings, screen, ship, bullets)
        ship.update()
        update_bullets(ai_settings, screen, ship, aliens, bullets)
        update_aliens(ai_settings, screen, ship, aliens, bullets)

        # Очистка экрана и отрисовка объектов
        screen.fill(ai_settings.bg_color)
        ship.blitme()
        for bullet in bullets.sprites():
            bullet.draw_bullet()
        aliens.draw(screen)

        # Обновление экрана
        pygame.display.flip()

        if len(aliens) == 0:
            bullets.empty()
            rows -= 1  # Уменьшить количество рядов
            if rows == 0:
                display_win_message(screen)
                pygame.time.wait(2000)
                break
            create_fleet(ai_settings, screen, ship, aliens, rows)

def check_events(ai_settings, screen, ship, bullets):
    """Обрабатывает нажатия клавиш и события мыши."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, screen, ship, bullets)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)

def check_keydown_events(event, ai_settings, screen, ship, bullets):
    """Реагирует на нажатия клавиш."""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key == pygame.K_SPACE:
        fire_bullet(ai_settings, screen, ship, bullets)

def check_keyup_events(event, ship):
    """Реагирует на отпускание клавиш."""
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False

def fire_bullet(ai_settings, screen, ship, bullets):
    """Выпускает пулю, если максимум ещё не достигнут."""
    if len(bullets) < ai_settings.bullets_allowed:
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)

def update_bullets(ai_settings, screen, ship, aliens, bullets):
    """Обновляет позиции пуль и удаляет старые пули."""
    bullets.update()
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)
    check_bullet_alien_collisions(ai_settings, screen, ship, aliens, bullets)

def check_bullet_alien_collisions(ai_settings, screen, ship, aliens, bullets):
    """Обрабатывает столкновения пуль с пришельцами."""
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)
    if len(aliens) == 0:
        bullets.empty()

def update_aliens(ai_settings, screen, ship, aliens, bullets):
    """Проверяет, достиг ли флот края экрана, и обновляет позиции всех пришельцев во флоте."""
    check_fleet_edges(ai_settings, aliens)
    aliens.update()
    if pygame.sprite.spritecollideany(ship, aliens):
        ship_hit(ai_settings, screen, ship, aliens, bullets)
    check_aliens_bottom(ai_settings, screen, ship, aliens, bullets)

def check_fleet_edges(ai_settings, aliens):
    """Реагирует на достижение пришельцем края экрана."""
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings, aliens)
            break

def change_fleet_direction(ai_settings, aliens):
    """Опускает весь флот и меняет направление флота."""
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1

def ship_hit(ai_settings, screen, ship, aliens, bullets):
    """Обрабатывает столкновение корабля с пришельцем."""
    pass

def check_aliens_bottom(ai_settings, screen, ship, aliens, bullets):
    """Проверяет, достигли ли пришельцы нижнего края экрана."""
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            ship_hit(ai_settings, screen, ship, aliens, bullets)
            break

def create_fleet(ai_settings, screen, ship, aliens, rows):
    """Создает флот пришельцев."""
    alien = Alien(ai_settings, screen)
    number_aliens_x = get_number_aliens_x(ai_settings, alien.rect.width)
    number_rows = get_number_rows(ai_settings, ship.rect.height, alien.rect.height, rows)
    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            create_alien(ai_settings, screen, aliens, alien_number, row_number)

def get_number_aliens_x(ai_settings, alien_width):
    """Вычисляет количество пришельцев в ряду."""
    available_space_x = ai_settings.screen_width - 2 * alien_width
    number_aliens_x = available_space_x // (2 * alien_width)
    return number_aliens_x

def get_number_rows(ai_settings, ship_height, alien_height, rows):
    """Определяет количество рядов, помещающихся на экране."""
    available_space_y = (ai_settings.screen_height -
                         (3 * alien_height) - ship_height)
    number_rows = available_space_y // (2 * alien_height)
    return min(rows, number_rows)

def create_alien(ai_settings, screen, aliens, alien_number, row_number):
    """Создает пришельца и размещает его в ряду."""
    alien = Alien(ai_settings, screen)
    alien_width = alien.rect.width
    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.x = alien.x
    alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
    aliens.add(alien)

def display_win_message(screen):
    """Отображает сообщение о победе."""
    font = pygame.font.SysFont(None, 55)
    win_message = font.render("Congratulations! You are the winner!!!", True, (0, 255, 0))
    screen_rect = screen.get_rect()
    win_message_rect = win_message.get_rect()
    win_message_rect.center = screen_rect.center
    screen.blit(win_message, win_message_rect)
    pygame.display.flip()

run_game()
