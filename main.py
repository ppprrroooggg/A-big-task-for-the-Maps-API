import os
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


longitude = 37.595526  # Долгота
width = 55.726193  # Широта
size = 0.1  # Размер
mode = 'map'  # Формат

# Инициализируем pygame
pygame.init()
screen = pygame.display.set_mode((450, 450))
screen.blit((build_map(longitude, width, size, mode)), (0, 0))
pygame.display.flip()
while pygame.event.wait().type != pygame.QUIT:
    pass
pygame.quit()

