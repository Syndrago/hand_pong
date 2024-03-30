# Hand Pong
A hand motion-controlled solo version of the classic Pong game.

## Introduction
This code is for the classic solitary Pong game with a twist, where the paddles are controlled with the user hand motion. Built and run entirely on Python, this combines game mechanics and computer vision for a more modern interpretation.

## Dependencies
Libraries:
* [pygame](https://pypi.org/project/pygame/)
* [opencv](https://pypi.org/project/opencv-python/)
* [numpy](https://numpy.org/install/)

**Tested on Python 3.9.13 on Windows 11 Build 22631*

## Installation
Please make sure your device has a builtin webcam or is connected to an external USB camera. If 2 or more cameras are installed on the system, the program will default to using the default system camera. Simply install the requirements on requirements.txt and run main_windows.py on Python.

## Game Details

### Mechanics
The player puts the camera in a still position, then positions their hand on the camera. The vertical position determines which way the paddle moves.

Just like in the classic Pong, the player moves the paddle to bounce the ball away from their zone. This version is the solo right-handed version where the players try to bounce the ball away from the right wall. Should the player miss the ball and the ball hits the right wall, the ball resets to the middle.

The ball bounces the paddles and the walls in the classic 90 degree manner, but every time the ball hits the paddle, the speed of the ball increases. The ball speed resets when the ball resets.

The game runs infinitely.

### Scoring
The player earns a point every time the ball bounces off the paddle. The player loses a point every time the ball hits the right wall.

## Design choices
Increasing ball speed to make it more difficult and interesting.

## Resources
https://en.wikipedia.org/wiki/Foreground_detection#Background_subtraction
https://www.pygame.org/
https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html
https://automaticaddison.com/real-time-object-tracking-using-opencv-and-a-webcam/
https://www.geeksforgeeks.org/create-a-pong-game-in-python-pygame/