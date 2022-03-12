# Programmed by Piboy314 (Test of dev branch)

# Import libraries
import pygame, sys, time, engine
from pygame.locals import *

# Define constants
WINDOW_SIZE = (1200, 800)
DISPLAY_SIZE = (600, 400)
FPS_MAX = 80
GRAVITY = 0.1

# Define variables
tile_rects = []
last_time = time.time()
fps = 80
jumping = False
double_jumped = False
player_spawned = False
last_was_parallax = False
last_was_air = False

# Movement variables
moving_right = False
moving_left = False
movement_speed = 2
player_y_momentum = 0
air_timer = 0
jump_speed = -4.5

true_scroll = [0, 0]

try:
    # Load images
    player_img_noscale = pygame.image   .load("res/img/entities/player/player.png")

    player_img = pygame.transform.scale(player_img_noscale, ((player_img_noscale.get_width() * 2), (player_img_noscale.get_height() * 2)))
    player_img.set_colorkey((255, 255, 255))

    # Tiles
    grass_img_noscale = pygame.image.load("res/img/tileset/grass.png")
    grass_img = pygame.transform.scale(grass_img_noscale, ((grass_img_noscale.get_width() * 2), (grass_img_noscale.get_height() * 2)))
    dirt_img_noscale = pygame.image.load("res/img/tileset/dirt.png")
    dirt_img = pygame.transform.scale(dirt_img_noscale, ((dirt_img_noscale.get_width() * 2), (dirt_img_noscale.get_height() * 2)))

except:
    # Load images
    player_img_noscale = pygame.image.load("img/entities/player/player.png")

    player_img = pygame.transform.scale(player_img_noscale, ((player_img_noscale.get_width() * 2), (player_img_noscale.get_height() * 2)))
    player_img.set_colorkey((255, 255, 255))

    # Tiles
    grass_img_noscale = pygame.image.load("img/tileset/grass.png")
    grass_img = pygame.transform.scale(grass_img_noscale, ((grass_img_noscale.get_width() * 2), (grass_img_noscale.get_height() * 2)))
    dirt_img_noscale = pygame.image.load("img/tileset/dirt.png")
    dirt_img = pygame.transform.scale(dirt_img_noscale, ((dirt_img_noscale.get_width() * 2), (dirt_img_noscale.get_height() * 2)))

TILE_SIZE = dirt_img.get_width()

# Rects
player_rect = pygame.Rect(50, 50, player_img.get_width(), player_img.get_height())
bg_objs = [[0.25, [0, 0, 0, 0]], [0.25, [280, 30, 40, 700]],[0.5, [30, 40, 40, 700]], [0.5, [130, 90, 100, 700]], [0.5, [300, 80, 120, 700]]]

# Create instances
clock = pygame.time.Clock()
colours = engine.Colours()

pygame.init() # Initializes pygame

def_font = pygame.font.SysFont("Arial", 18) # Define a font for the FPS Counter

try:
    # Load sounds
    my_head = pygame.mixer.Sound("res/sfx/MyHead.wav")

    # Load music
    pygame.mixer.music.load("res/music/Investigator Music.wav")

except:
    # Load sounds
    my_head = pygame.mixer.Sound("sfx/MyHead.wav")

    # Load music
    pygame.mixer.music.load("music/Investigator Music.wav")

# Setup pygame window
pygame.display.set_caption("Pygame Platformer Test")
screen = pygame.display.set_mode(WINDOW_SIZE, RESIZABLE)
display = pygame.Surface(DISPLAY_SIZE)

# Define functions
def load_map(path):
    f = open(path + ".txt", "r")
    data = f.read()
    f.close()
    data = data.split("\n")
    game_map = []
    for row in data:
         game_map.append(list(row))

    return game_map

def collision_check(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list

def move(rect, movement, tiles):
    collision_types = {"top": False, "bottom": False, "right": False, "left": False}
    rect.x += movement[0]
    hit_list = collision_check(rect, tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types["right"] = True

        elif movement[0] < 0:
            rect.left = tile.right
            collision_types["left"] = True
    rect.y += movement[1]
    hit_list = collision_check(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types["bottom"] = True

        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types["top"] = True

    return rect, collision_types

def update_fps():
	fps = str(int(clock.get_fps()))
	fps_text = def_font.render(fps, 1, colours.red)
	return fps_text

try:
    game_map = load_map("res/map") # Load game map

except:
    game_map = load_map("map") # Load game map

pygame.mixer.music.play(-1) # Start playing music (-1 for looping)

while True: # Game loop
    # Calculate Delta Time
    dt = time.time() - last_time
    dt *= FPS_MAX # Multiply our delta time by FPS_MAX so we can measure in pixels per second instead of pixels per frame which is frame rate dependant
    #print(dt)
    last_time = time.time()

    true_scroll[0] += (player_rect.x - true_scroll[0] - (DISPLAY_SIZE[0] / 2)) / (20) * dt
    true_scroll[1] += (player_rect.y - true_scroll[1] - (DISPLAY_SIZE[1] / 2)) / (20) * dt
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])

    # Manage Input
    player_movement = [0, 0]
    if moving_right:
        player_movement[0] += round(movement_speed * dt)

    if moving_left:
        player_movement[0] -= round(movement_speed * dt)

    #print(player_movement)

    player_movement[1] += (player_y_momentum * dt)
    player_y_momentum += GRAVITY * dt # Apply Gravity
    if player_y_momentum > (3 * dt): # Max out gravity at 3 pixels per second
        player_y_momentum = (3 * dt)

    for event in pygame.event.get(): # Gets events (mouse click, mouse move, key press etc.)
        if event.type == QUIT:
            pygame.quit() # Clean Pygame
            sys.exit() # Quit Program

        elif event.type == VIDEORESIZE:
            WINDOW_SIZE = (screen.get_width(), screen.get_height())

        elif event.type == KEYDOWN:
            if event.key == K_RIGHT:
                moving_right = True
            elif event.key == K_LEFT:
                moving_left = True

            if event.key == K_UP:
                jumping = True
                if air_timer < 6:
                    player_y_momentum = jump_speed

                elif double_jumped == False:
                    if jumping == True:
                        player_y_momentum = jump_speed
                        double_jumped = True

            if event.key == K_ESCAPE:
                pygame.quit() # Clean Pygame
                sys.exit() # Quit Program

            if event.key == K_e:
                if fps == FPS_MAX:
                    fps = 30
                elif fps == 30:
                    fps = FPS_MAX
                else:
                    print("ERROR, ERROR")

        elif event.type == KEYUP:
            if event.key == K_RIGHT:
                moving_right = False

            elif event.key == K_LEFT:
                moving_left = False

    # Handle Rendering
    display.fill(colours.skyblue)

    # Render Parallax
    # pygame.draw.rect(display, colours.darkgreen, pygame.Rect(0, 300, 600, 130))
    # for bg_obj in bg_objs:
    #     bg_obj_rect = pygame.Rect(bg_obj[1][0] - scroll[0] * bg_obj[0], bg_obj[1][1] - scroll[1] * bg_obj[0], bg_obj[1][2], bg_obj[1][3])
    #     if bg_obj[0] == 0.5:
    #         pygame.draw.rect(display, colours.brightgreen, bg_obj_rect)
    #     else:
    #         pygame.draw.rect(display, colours.midgreen, bg_obj_rect)


    # Render world using game_map variable
    tile_rects = []
    y = 0
    bg_objs[0][1][2] = 0
    bg_objs[0][1][3] = 0
    for row in game_map:
        x = 0
        for tile in row:
            if tile == "0":
                last_was_air = True

            else:
                if tile == "3":
                    bg_obj = bg_objs[0]

                    bg_obj[1][2] += TILE_SIZE
                    if last_was_air:
                        print("last was air and now it's parallax")
                        bg_obj[1][3] += TILE_SIZE

                    if bg_obj[1][2] == 0:
                        print("changing parallax obj position...")
                        print(bg_obj[1][0])
                        bg_obj[1][0] = x * TILE_SIZE
                        bg_obj[1][1] = y * TILE_SIZE

                    print("Width: " + str(bg_obj[1][2]))
                    print("Height: " + str(bg_obj[1][3]))

                    bg_obj_rect = pygame.Rect(bg_obj[1][0] - scroll[0] * bg_obj[0], bg_obj[1][1] - scroll[1] * bg_obj[0], bg_obj[1][2], bg_obj[1][3])
                    pygame.draw.rect(display, colours.midgreen, bg_obj_rect)

                elif tile == "1":
                    display.blit(dirt_img, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))

                elif tile == "2":
                    display.blit(grass_img, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))

                elif player_spawned == False:
                    if tile == "9":
                        player_rect.x = x * TILE_SIZE
                        player_rect.y = y * TILE_SIZE
                        player_spawned = True

                if tile == "1" or tile == "2":
                    tile_rects.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

                last_was_air = False

            x += 1

        y += 1

    player_rect, collisions = move(player_rect, player_movement, tile_rects)

    if not jumping:
        if collisions["bottom"]:
            player_y_momentum = 0
            air_timer = 0

    else:
        air_timer += 1
        if collisions["bottom"]:
            jumping = False
            double_jumped = False

        if collisions["top"]:
            my_head.play()
            player_y_momentum = 0

    #print(player_movement)
    #print(collisions
    display.blit(player_img, (player_rect.x - scroll[0], player_rect.y - scroll[1])) # Blit player_img into the screen
    surf = pygame.transform.scale(display, WINDOW_SIZE)
    #player_rect = pygame.draw.rect(surf, colours.yellow, player_rect)
    screen.blit(surf, (0, 0))
    screen.blit(update_fps(), (10,0))

    pygame.display.update() # Update Display
    clock.tick(fps) # Cap our fps (temporary) to test delta time - in future this will be replaced with either 240 or the current monitor's refresh rate in the variable FPS_CAP
