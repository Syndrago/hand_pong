import pygame
import cv2 # Import the OpenCV library
import numpy as np # Import Numpy library

pygame.init()

# Font that is used to render the text
font20 = pygame.font.Font('freesansbold.ttf', 20)

# RGB values of standard colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

# Basic parameters of the screen
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hand Pong")
move_pixel_buffer = 25
overlay_opacity = 75

clock = pygame.time.Clock() 
FPS = 30

# Striker class


class Striker:
		# Take the initial position, dimensions, speed and color of the object
	def __init__(self, posx, posy, width, height, speed, color):
		self.posx = posx
		self.posy = posy
		self.width = width
		self.height = height
		self.speed = speed
		self.color = color
		# Rect that is used to control the position and collision of the object
		self.geekRect = pygame.Rect(posx, posy, width, height)
		# Object that is blit on the screen
		self.geek = pygame.draw.rect(screen, self.color, self.geekRect)

	# Used to display the object on the screen
	def display(self):
		self.geek = pygame.draw.rect(screen, self.color, self.geekRect)

	def update(self, yFac):
		self.posy = self.posy + self.speed*yFac

		# Restricting the striker to be below the top surface of the screen
		if self.posy <= 0:
			self.posy = 0
		# Restricting the striker to be above the bottom surface of the screen
		elif self.posy + self.height >= HEIGHT:
			self.posy = HEIGHT-self.height

		# Updating the rect with the new values
		self.geekRect = (self.posx, self.posy, self.width, self.height)

	def displayScore(self, text, score, x, y, color):
		text = font20.render(text+str(score), True, color)
		textRect = text.get_rect()
		textRect.center = (x, y)

		screen.blit(text, textRect)

	def getRect(self):
		return self.geekRect

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
		# self.firstTime = 1

	def display(self):
		self.ball = pygame.draw.circle(
			screen, self.color, (self.posx, self.posy), self.radius)

	def update(self):
		self.posx += self.speed*self.xFac
		self.posy += self.speed*self.yFac

		# If the ball hits the top or bottom surfaces, 
		# then the sign of yFac is changed and 
		# it results in a reflection
		if self.posy <= 0 or self.posy >= HEIGHT:
			self.yFac *= -1
		if self.posx <= 0: # and self.firstTime:
			# self.firstTime = 0
			self.xFac *= -1
			# return 1
		elif self.posx >= WIDTH: #and self.firstTime:
			# self.firstTime = 0
			return -1
		else:
			return 0

	def reset(self):
		self.posx = WIDTH//2
		self.posy = HEIGHT//2
		self.xFac *= -1
		self.firstTime = 1

	# Used to reflect the ball along the X-axis
	def hit(self):
		self.xFac *= -1

	def getRect(self):
		return self.ball
	
class Webcam:

	def __init__(self):
    # Create a VideoCapture object
		self.cap = cv2.VideoCapture(0)
	
		# Create the background subtractor object
		# Use the last 700 video frames to build the background
		self.back_sub = cv2.createBackgroundSubtractorMOG2(history=700, 
			varThreshold=25, detectShadows=True)
	
		# Create kernel for morphological operation
		# You can tweak the dimensions of the kernel
		# e.g. instead of 20,20 you can try 30,30.
		self.kernel = np.ones((20,20),np.uint8)
		self.im_frame = self.cap.read()
		self.max_index = 0
		self.y_pos = 0

	def cap_images(self):
 

		# Capture frame-by-frame
		# This method returns True/False as well
		# as the video frame.
		ret, frame = self.cap.read()

		# Use every frame to calculate the foreground mask and update
		# the background
		fg_mask = self.back_sub.apply(frame)

		# Close dark gaps in foreground object using closing
		fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, self.kernel)

		# Remove salt and pepper noise with a median filter
		fg_mask = cv2.medianBlur(fg_mask, 5) 
		
		# Threshold the image to make it either black or white
		_, fg_mask = cv2.threshold(fg_mask,127,255,cv2.THRESH_BINARY)

		# Find the index of the largest contour and draw bounding box
		fg_mask_bb = fg_mask
		contours, hierarchy = cv2.findContours(fg_mask_bb,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[-2:]
		areas = [cv2.contourArea(c) for c in contours]

		# If there are no countours
		if len(areas) < 1:

			# Display the resulting frame
			# cv2.imshow('frame',frame):
				
			# Go to the top of the while loop
			self.im_frame = frame
				
		else:
			# Find the largest moving object in the image
			self.max_index = np.argmax(areas)

			# Draw the bounding box
			# print(self.max_index)
			cnt = contours[self.max_index]
			x,y,w,h = cv2.boundingRect(cnt)
			frame = cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),3)

			# Draw circle in the center of the bounding box
			x2 = x + int(w/2)
			y2 = y + int(h/2)
			frame = cv2.circle(frame,(x2,y2),4,(0,255,0),-1)

			# Print the centroid coordinates (we'll use the center of the
			# bounding box) on the image
			text = "x: " + str(x2) + ", y: " + str(y2)
			# print(text)
			frame = cv2.putText(frame, text, (x2 - 10, y2 - 10),
				cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
			
			# Display the resulting frame
			# cv2.imshow('frame',frame)
			self.im_frame = frame
			self.y_pos = y2

	def cam_stop(self):
		# Close down the video stream
		self.cap.release()
		cv2.destroyAllWindows()


# Game Manager
def main():
	running = True

	# Defining the objects
	# geek1 = Striker(20, 0, 10, 100, 10, GREEN)
	geek2 = Striker(WIDTH-30, 0, 10, 100, 10, GREEN)
	ball = Ball(WIDTH//2, HEIGHT//2, 7, 7, WHITE)
	webcam = Webcam()

	# listOfGeeks = [geek1, geek2]
	listOfGeeks = [geek2]

	# Initial parameters of the players
	# geek1Score, geek2Score = 0, 0
	geek2Score = 0
	geek2YFac = 0

	while running:
		screen.fill(BLACK)
		webcam.cap_images()
		# Event handling
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			# if event.type == pygame.KEYDOWN:
			# 	if event.key == pygame.K_UP:
			# 		geek2YFac = -1
			# 	if event.key == pygame.K_DOWN:
			# 		geek2YFac = 1
			# if event.type == pygame.KEYUP:
			# 	if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
			# 		geek2YFac = 0
		if webcam.y_pos > webcam.im_frame.shape[0]//2 + move_pixel_buffer:
			geek2YFac = 1
		elif webcam.y_pos < webcam.im_frame.shape[0]//2 - move_pixel_buffer:
			geek2YFac = -1
		else:
			geek2YFac = 0

		# Collision detection
		for geek in listOfGeeks:
			if pygame.Rect.colliderect(ball.getRect(), geek.getRect()):
				ball.hit()

		# Updating the objects
		geek2.update(geek2YFac)
		point = ball.update()

		# -1 -> Geek_1 has scored
		# +1 -> Geek_2 has scored
		# 0 -> None of them scored
		if point == -1:
			geek2Score -= 1
		elif point == 1:
			geek2Score += 1

		# Someone has scored
		# a point and the ball is out of bounds.
		# So, we reset it's position
		if point: 
			ball.reset()

		# Displaying the objects on the screen
		# geek1.display()
		geek2.display()
		ball.display()

		# Displaying the scores of the players
		# geek1.displayScore("Geek_1 : ", 
		# 				geek1Score, 100, 20, WHITE)
		geek2.displayScore("Geek_2 : ", 
						geek2Score, WIDTH-100, 20, WHITE)
		img = pygame.pixelcopy.make_surface(np.rot90(webcam.im_frame))
		img.set_colorkey(img.get_colorkey())
		img = pygame.transform.scale(img, (webcam.im_frame.shape[1]*0.5, webcam.im_frame.shape[0]*0.5))
		img.set_alpha(overlay_opacity)
		screen.blit(img,img.get_rect())

		pygame.display.update()
		
		clock.tick(FPS)


if __name__ == "__main__":
	main()
	pygame.quit()
