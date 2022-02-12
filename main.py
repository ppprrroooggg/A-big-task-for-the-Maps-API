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


def geocoder_address(address):
    map_req = f"https://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={address}"
    resp = requests.get(map_req)
    print(resp.content)


loc_name = ""
longitude = 37.595000  # Долгота
width = 55.726000  # Широта
size = [0.0001, 0.0005, 0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.3, 0.5, 1, 3, 5, 7,  10, 20, 30, 50]  # Размер list
zoom_level = 7  # Уовень Зума
modes = ["map", "sat", "sat,skl"]  # Формат list
mode_num = 0
# Инициализируем pygame
pygame.init()

FONT = pygame.font.Font(None, 32)
tex_render = FONT.render(loc_name, True, (255, 0, 0))
screen_bg = None
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

            if event.key == pygame.K_RETURN:
                geocoder_address(loc_name)
            elif event.key == pygame.K_BACKSPACE:
                loc_name = loc_name[:-1]
            else:
                loc_name += event.unicode
            tex_render = FONT.render(loc_name, True, (0, 0, 0))

    if update:
        screen.fill((0, 0, 0))
        screen_bg = build_map(longitude, width, size[zoom_level], modes[mode_num])
        screen.blit(screen_bg, (0, 0))
        update = False
    screen.blit(screen_bg, (0, 0))
    screen.blit(tex_render, (0, 0))
    pygame.time.wait(10)
    pygame.display.flip()
pygame.quit()
