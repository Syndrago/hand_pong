"""
Hand Pong
=====

Author: Synclair Chendranaga (Syndrago)
Email: chendranaga@gmail.com
"""

import pygame
import cv2
import numpy as np


pygame.init()

# Font that is used to render the text
font20 = pygame.font.Font('freesansbold.ttf', 20)

# RGB values of standard colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Basic parameters of the screen
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hand Pong")
clock = pygame.time.Clock() 
FPS = 30

# Pixel buffer for neutral hand position
move_pixel_buffer = 25

# Game settings
speed_multiplier = 1.25
overlay_opacity = 75 # Webcam overlay opacity

# Paddle class
class Paddle:
		# Take the initial position, dimensions, speed and color of the object
	def __init__(self, posx:int, posy:int, width:int, height:int, speed:float, color:tuple):
		self.posx = posx
		self.posy = posy
		self.width = width
		self.height = height
		self.speed = speed
		self.color = color
		# Rect that is used to control the position and collision of the object
		self.paddle_rect = pygame.Rect(posx, posy, width, height)
		# Object that is blit on the screen
		self.paddle_blit = pygame.draw.rect(screen, self.color, self.paddle_rect)

	# Used to display the object on the screen
	def display(self):
		self.paddle_blit = pygame.draw.rect(screen, self.color, self.paddle_rect)

	def update(self, yFac:int):
		self.posy = self.posy + self.speed*yFac

		# Restricting the Paddle to be below the top surface of the screen
		if self.posy <= 0:
			self.posy = 0
		# Restricting the Paddle to be above the bottom surface of the screen
		elif self.posy + self.height >= HEIGHT:
			self.posy = HEIGHT-self.height

		# Updating the rect with the new values
		self.paddle_rect = (self.posx, self.posy, self.width, self.height)

	def displayScore(self, text, score, x, y, color):
		text = font20.render(text+str(score), True, color)
		textRect = text.get_rect()
		textRect.center = (x, y)

		screen.blit(text, textRect)

	def getRect(self):
		return self.paddle_rect

# Ball class
class Ball:
	def __init__(self, posx, posy, radius, speed, color):
		self.posx = posx
		self.posy = posy
		self.radius = radius
		self.speed = speed
		self.color = color
		self.xFac = 1
		self.yFac = -1
		self.ball = pygame.draw.circle(
			screen, self.color, (self.posx, self.posy), self.radius)

	def display(self):
		self.ball = pygame.draw.circle(
			screen, self.color, (self.posx, self.posy), self.radius)

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
		self.posx = WIDTH//2
		self.posy = HEIGHT//2
		self.xFac *= -1
		self.speed = 7

	# Used to reflect the ball along the X-axis
	def hit(self, paddle_xpos):
		self.speed *= speed_multiplier
		# Reflect ball in Y if ball hits Paddle corner
		if paddle_xpos < self.posx:
			self.yFac *= -1
		else:
			self.xFac *= -1

	def getRect(self):
		return self.ball

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

# Game Manager
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
        if webcam.y_pos > webcam.im_frame.shape[0] // 2 + move_pixel_buffer:
            player_YFac = 1
        elif webcam.y_pos < webcam.im_frame.shape[0] // 2 - move_pixel_buffer:
            player_YFac = -1

        if pygame.Rect.colliderect(ball.getRect(), paddle.getRect()):
            ball.hit(paddle.posx)
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
        paddle.displayScore("Score: ", player_score, WIDTH - 100, 20, WHITE)

        img = pygame.pixelcopy.make_surface(np.swapaxes(webcam.im_frame, 0, 1))
        img.set_colorkey(img.get_colorkey())
        img = pygame.transform.scale(img, (int(webcam.im_frame.shape[1] * 0.5), int(webcam.im_frame.shape[0] * 0.5)))
        img.set_alpha(overlay_opacity)
        screen.blit(img, img.get_rect())

        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
	main()
	pygame.quit()
