import sys
from PIL import Image
import pygame
import requests
import io
import json as js


def build_map(lon, wid, siz, mod, point_li=None):
    if point_li is None:
        point_li = []
    if point_li:
        st_of_points = "&pt="
        for j in range(len(point_li)):
            st_of_points += f"{point_li[j][0]},{point_li[j][1]},pmwtm{j + 1}~"
        st_of_points = st_of_points[:-1]
        map_req = f"http://static-maps.yandex.ru/1.x/?ll={lon},{wid}&spn={siz},{siz}&l={mod}&size=450,450" \
                  f"{st_of_points}"
    else:
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
    map_req = f"https://geocode-maps.yandex.ru/1.x/" \
              f"?format=json&apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={address}"
    resp = requests.get(map_req)  # я не знаю как прасить JSON
    js_resp = js.loads(resp.content)
    try:
        lower_corner = str(js_resp['response']['GeoObjectCollection']['metaDataProperty']['GeocoderResponseMetaData']
                           ['boundedBy']['Envelope']['lowerCorner']).split(" ")
        upper_corner = str(js_resp['response']['GeoObjectCollection']['metaDataProperty']['GeocoderResponseMetaData']
                           ['boundedBy']['Envelope']['upperCorner']).split(" ")
    except BaseException:
        lower_corner = str(js_resp['response']['GeoObjectCollection']['featureMember']
                           [0]['GeoObject']['boundedBy']['Envelope']['lowerCorner']).split(" ")
        upper_corner = str(js_resp['response']['GeoObjectCollection']['featureMember']
                           [0]['GeoObject']['boundedBy']['Envelope']['upperCorner']).split(" ")
    ll = float(lower_corner[0])
    lw = float(lower_corner[1])
    hl = float(upper_corner[0])
    hw = float(upper_corner[1])
    end_l = (ll + hl) / 2
    end_h = (lw + hw) / 2
    siz = max([hl - ll, hw - lw])
    return [end_l, end_h, siz]


points_on_map = []
loc_name = ""
longitude = 37.595000  # Долгота
width = 55.726000  # Широта
size = [0.0001, 0.0005, 0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.3, 0.5, 1, 3, 5, 7,  10, 20, 30, 50]  # Размер list
zoom_level = 7  # Уовень Зума
modes = ["map", "sat", "sat,skl"]  # Формат list
mode_num = 0
# Инициализируем pygame
pygame.init()

dark_black = (0, 0, 0)
light_black = (30, 30, 30)

btn_color = dark_black

FONT = pygame.font.Font(None, 32)
FONT_SEC = pygame.font.Font(None, 45)
tex_render = FONT.render(loc_name, True, (255, 0, 0))
screen_bg = None
screen = pygame.display.set_mode((450, 450))

string = pygame.Surface((450, 25))
string.set_alpha(150)
string.fill((200, 200, 200))

update = True
run = True
while run:
    mouse = pygame.mouse.get_pos()
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
            if event.key == pygame.K_1 and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                mode_num = 0
                update = True
            if event.key == pygame.K_2 and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                mode_num = 1
                update = True
            if event.key == pygame.K_3 and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                mode_num = 2
                update = True

            if event.key == pygame.K_RETURN:
                if loc_name != "":
                    geocoder_place = geocoder_address(loc_name)
                    longitude, width,  = geocoder_place[0], geocoder_place[1]
                    points_on_map.append((geocoder_place[0], geocoder_place[1]))
                    for i in range(len(size)):
                        if size[i] > geocoder_place[2]:
                            zoom_level = i
                            break
                        zoom_level = i
                    update = True
            elif event.key == pygame.K_BACKSPACE:
                loc_name = loc_name[:-1]
            elif not update:
                loc_name += event.unicode
            tex_render = FONT.render(loc_name, True, (0, 0, 0))

        if event.type == pygame.MOUSEBUTTONDOWN:
            if 300 <= mouse[0] <= 450 and 400 <= mouse[1] <= 450:
                points_on_map.clear()
                update = True

    if 300 <= mouse[0] <= 450 and 400 <= mouse[1] <= 450:
        btn_color = light_black
    else:
        btn_color = dark_black

    if update:
        screen.fill((0, 0, 0))
        screen_bg = build_map(longitude, width, size[zoom_level], modes[mode_num], points_on_map)
        screen.blit(screen_bg, (0, 0))
        update = False
    screen.blit(screen_bg, (0, 0))
    screen.blit(string, (0, 0))
    screen.blit(tex_render, (0, 0))
    pygame.draw.rect(screen, btn_color, [300, 400, 150, 50])
    screen.blit(FONT_SEC.render("Обновить", True, (255, 255, 255)), (304, 410))
    pygame.time.wait(10)
    pygame.display.flip()
pygame.quit()
