import pygame, sys
from pygame.locals import QUIT
import pygame.freetype
from Cameragroup import *
from groq import Groq
import os

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def fetch_text():
    full_prompt = f"""Imagine you a NPC for a pygame about bartending and your name is Mix the Crab. Max length is 10 words"""
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": full_prompt,
            }
        ],
        model="llama3-8b-8192",
    )
    answer = response.choices[0].message.content
    return answer

def response(text):
    full_prompt = f"""Imagine you a NPC for a pygame about bartending and your name is Mix the Crab. Respone to {text} Max length is 10 words"""
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": full_prompt,
            }
        ],
        model="llama3-8b-8192",
    )
    answer = response.choices[0].message.content
    return answer
    
display_text = ''

class Bartender(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)
        self.image = pygame.transform.scale(pygame.image.load('graphics/bartender.png').convert_alpha(), (100, 100))
        self.rect = self.image.get_rect(topleft=pos)
        self.touched = False
        self.display_text = 'Talk to the bartender!'

    def update(self):
        global interacting_with_bartender, display_text
        if self.rect.colliderect(player.rect):
            if not self.touched:
                self.touched = True
                interacting_with_bartender = True
                display_text = 'hello there'
        else:
            if self.touched:
                self.touched = False
                interacting_with_bartender = False
                display_text = ''

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)
        self.image = pygame.transform.scale(pygame.image.load('graphics/player.png').convert_alpha(), (50, 50))
        self.rect = self.image.get_rect(center=pos)
        self.direction = pygame.math.Vector2()
        self.speed = 5

    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.direction.y = -1
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
        else:
            self.direction.y = 0
        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
        else:
            self.direction.x = 0

    def update(self):
        self.input()
        self.rect.center += self.direction * self.speed

pygame.init()
WIDTH, HEIGHT = 800, 500
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 176, 240)
screen = pygame.display.set_mode((800, 500))
clock = pygame.time.Clock()
pygame.event.set_grab(True)

pygame.font.init()
pygame.display.set_caption('Hello World!')
pygame.font.init()
font = pygame.freetype.SysFont(None, 16)
camera_group = CameraGroup()
player = Player((640, 360), camera_group)

output_box = pygame.Rect(50, 50, WIDTH - 100, 100)
output_color = BLUE
output_text = fetch_text()

bartender = Bartender((450, 100), camera_group)

input_box = pygame.Rect(50, HEIGHT - 100, WIDTH - 100, 100)
input_color_inactive = BLUE
input_color_active = WHITE
input_color = input_color_inactive

active = False
text = ''
interacting_with_bartender = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        if event.type == pygame.MOUSEWHEEL:
            camera_group.zoom_scale += event.y * 0.03
        if event.type == pygame.MOUSEBUTTONDOWN:
            if interacting_with_bartender and input_box.collidepoint(event.pos):
                active = not active
                if active:
                    text = ''
            else:
                active = False
            input_color = input_color_active if active else input_color_inactive
        if event.type == pygame.KEYDOWN:
            if active:
                if event.key == pygame.K_RETURN:
                    output_text = response(text)
                    text = ''
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode

    screen.fill('#71ddee')
    camera_group.update()
    camera_group.custom_draw(player)
    pygame.draw.rect(screen, output_color, output_box, 0, border_radius=20)
    font.render_to(screen, (output_box.x + 10, output_box.y + 10), output_text, BLACK)
    if interacting_with_bartender:
        pygame.draw.rect(screen, input_color, input_box, 0, border_radius=20)
        font.render_to(screen, (input_box.x + 10, input_box.y + 10), text, BLACK)

    pygame.display.update()
    clock.tick(60)
