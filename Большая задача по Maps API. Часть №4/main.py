import sys
from PIL import Image
import pygame
import requests
import io


def build_map(lon, wid, siz, mod):
    map_req = f"http://static-maps.yandex.ru/1.x/?ll={lon},{wid}&spn={siz},{siz}&l={mod}&size=450,450"
    resp = requests.get(map_req)

    if not resp:
        print("Ошибка выполнения запроса:")
        print(map_req)
        print("Http статус:", resp.status_code, "(", resp.reason, ")")
        sys.exit(1)

    img = Image.open(io.BytesIO(resp.content)).convert('RGB')
    return pygame.image.fromstring(img.tobytes(), img.size, "RGB")


longitude = 37.595000  # Долгота
width = 55.726000  # Широта
size = [0.0001, 0.0005, 0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.3, 0.5, 1, 3, 5, 7,  10, 20, 30, 50]  # Размер list
zoom_level = 7  # Уовень Зума
modes = ["map", "sat", "sat,skl"]  # Формат list
mode_num = 0
# Инициализируем pygame
pygame.init()
screen = pygame.display.set_mode((450, 450))
update = True
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_PAGEUP:
                if zoom_level - 1 >= 0:
                    zoom_level -= 1
                    update = True
            if event.key == pygame.K_PAGEDOWN:
                if zoom_level + 1 <= len(size) - 1:
                    zoom_level += 1
                    update = True

            if event.key == pygame.K_LEFT:
                if longitude - size[zoom_level] > -180:
                    longitude -= size[zoom_level]
                    longitude = round(longitude, 6)
                    update = True
            if event.key == pygame.K_RIGHT:
                if longitude + size[zoom_level] < 180:
                    longitude += size[zoom_level]
                    longitude = round(longitude, 6)
                    update = True

            if event.key == pygame.K_DOWN:
                if width - size[zoom_level] > -86:
                    width -= size[zoom_level]
                    width = round(width, 6)
                    update = True
            if event.key == pygame.K_UP:
                if width + size[zoom_level] < 86:
                    width += size[zoom_level]
                    width = round(width, 6)
                    update = True
            if event.key == pygame.K_1:
                mode_num = 0
                update = True
            if event.key == pygame.K_2:
                mode_num = 1
                update = True
            if event.key == pygame.K_3:
                mode_num = 2
                update = True

    if update:
        screen.fill((0, 0, 0))
        screen.blit((build_map(longitude, width, size[zoom_level], modes[mode_num])), (0, 0))
        pygame.display.flip()
        update = False
    pygame.time.wait(10)
pygame.quit()
