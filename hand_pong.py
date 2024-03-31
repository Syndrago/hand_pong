import pygame
import cv2
import numpy as np
import random
from playsound import playsound
import os

# Constants
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
color_list = [RED, GREEN, BLUE, WHITE]
WIDTH, HEIGHT = 900, 600
FPS = 30
move_pixel_buffer = 25
speed_multiplier = 1.25
overlay_opacity = 75

script_dir = os.path.dirname(__file__)
beep_path = "beep.wav"
bounce_path = "bounce.wav"
beep_abs_path = os.path.join(script_dir, beep_path)
bounce_abs_path = os.path.join(script_dir, bounce_path)

pygame.init()
pygame.mixer.init()

# Font
font20 = pygame.font.Font("freesansbold.ttf", 20)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hand Pong")
clock = pygame.time.Clock()

class Paddle:
    def __init__(self, posx, posy, width, height, speed, color):
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height
        self.speed = speed
        self.color = color
        self.paddle_rect = pygame.Rect(posx, posy, width, height)

    def update(self, yFac):
        self.posy += self.speed * yFac
        self.posy = max(0, min(self.posy, HEIGHT - self.height))
        self.paddle_rect.y = self.posy

    def display(self):
        pygame.draw.rect(screen, self.color, self.paddle_rect)

    def display_score(self, text, score, x, y, color):
        text = font20.render(text + str(score), True, color)
        textRect = text.get_rect(center=(x, y))
        screen.blit(text, textRect)

    def getRect(self):
        return self.paddle_rect


class Ball:
    def __init__(self, posx, posy, radius, speed, color):
        self.posx = posx
        self.posy = posy
        self.radius = radius
        self.speed = speed
        self.color = color
        self.xFac = 1
        self.yFac = -1

    def update(self):
        self.posx += self.speed * self.xFac
        self.posy += self.speed * self.yFac

        if self.posy <= self.radius or self.posy >= (HEIGHT - self.radius):
            self.yFac *= -1
        if self.posx <= self.radius:
            self.xFac *= -1
            return 0
        elif self.posx >= (WIDTH - self.radius):
            return -1
        else:
            return 0

    def reset(self):
        self.posx = WIDTH // 2
        self.posy = HEIGHT // 2
        self.xFac *= -1
        self.speed = 7
        pygame.mixer.music.load(beep_abs_path)
        pygame.mixer.music.play()

    def hit(self, paddle_xpos):
        self.speed *= speed_multiplier
        self.yFac *= -1 if paddle_xpos < self.posx else 1
        self.xFac *= -1

    def display(self):
        pygame.draw.circle(screen, self.color, (self.posx, self.posy), self.radius)

    def getRect(self):
        return pygame.Rect(self.posx - self.radius, self.posy - self.radius, 2 * self.radius, 2 * self.radius)


class Webcam:
    def __init__(self, camera_number):
        self.cap = cv2.VideoCapture(camera_number, cv2.CAP_DSHOW)
        self.back_sub = cv2.createBackgroundSubtractorMOG2(history=700, varThreshold=25, detectShadows=True)
        self.kernel = np.ones((20, 20), np.uint8)
        self.im_frame = None
        self.max_index = 0
        self.y_pos = 0

    def cap_images(self):
        ret, frame = self.cap.read()

        fg_mask = self.back_sub.apply(frame)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, self.kernel)
        fg_mask = cv2.medianBlur(fg_mask, 5)
        _, fg_mask = cv2.threshold(fg_mask, 127, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(fg_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) < 1:
            self.im_frame = frame
            self.y_pos = self.im_frame.shape[0] // 2
        else:
            areas = [cv2.contourArea(c) for c in contours]
            self.max_index = np.argmax(areas)
            cnt = contours[self.max_index]
            x, y, w, h = cv2.boundingRect(cnt)
            frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
            x2 = x + int(w / 2)
            y2 = y + int(h / 2)
            frame = cv2.circle(frame, (x2, y2), 4, (0, 255, 0), -1)
            text = "x: " + str(x2) + ", y: " + str(y2)
            frame = cv2.putText(frame, text, (x2 - 10, y2 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            self.im_frame = frame
            self.y_pos = y2

    def cam_stop(self):
        self.cap.release()
        cv2.destroyAllWindows()


def main():
    running = True
    paddle = Paddle(WIDTH - 30, 0, 10, 100, 10, GREEN)
    ball = Ball(WIDTH // 2, HEIGHT // 2, 7, 7, WHITE)
    webcam = Webcam(0)
    player_score = 0
    player_YFac = 0

    while running:
        screen.fill(BLACK)
        webcam.cap_images()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        player_YFac = 0
        if webcam.y_pos >= webcam.im_frame.shape[0] - move_pixel_buffer*3:
            player_YFac = 2
        elif webcam.y_pos > webcam.im_frame.shape[0] // 2 + move_pixel_buffer:
            player_YFac = 1
        elif webcam.y_pos <= move_pixel_buffer*3:
            player_YFac = -2
        elif webcam.y_pos < webcam.im_frame.shape[0] // 2 - move_pixel_buffer:
            player_YFac = -1

        if ball.getRect().colliderect(paddle.getRect()):
            ball.hit(paddle.posx)
            pygame.mixer.music.load(bounce_abs_path)
            pygame.mixer.music.play()
            paddle.color = random.choice(color_list)
            player_score += 1

        paddle.update(player_YFac)
        point = ball.update()

        if point == -1:
            if player_score > 0:
                player_score -= 1
        elif point == 1:
            player_score += 1

        if point:
            ball.reset()

        paddle.display()
        ball.display()
        paddle.display_score("Score: ", player_score, WIDTH - 100, 20, WHITE)
        rgb_frame = cv2.cvtColor(webcam.im_frame, cv2.COLOR_BGR2RGB)
        img = pygame.pixelcopy.make_surface(np.swapaxes(rgb_frame, 0, 1))
        img = pygame.transform.scale(
            img, (int(webcam.im_frame.shape[1] * 0.5), int(webcam.im_frame.shape[0] * 0.5))
        )
        img.set_alpha(overlay_opacity)
        screen.blit(img, img.get_rect())

        pygame.display.update()
        clock.tick(FPS)

    webcam.cam_stop()
    pygame.quit()


if __name__ == "__main__":
    main()
