import RPi.GPIO as GPIO
import time
import sys
import pygame
import math
GPIO.setwarnings(False)

#ultrasonic sensor
GPIO.setmode(GPIO.BOARD)
trig_pin = 16
echo_pin = 18
GPIO.setup(trig_pin, GPIO.OUT)
GPIO.setup(echo_pin, GPIO.IN)

#servo
servo_pin = 12
GPIO.setup(servo_pin, GPIO.OUT)
servo = GPIO.PWM(servo_pin,50)
servo.start(2.5)


pygame.init()


screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Radar HUD")

scanned_positions = []

def init_screen():
    screen.fill((0, 0, 0))
    draw_line(screen, (0, 255, 0), angle=0)
    pygame.display.update()
    return screen

def draw_line(screen, color, angle):
    center_x = screen_width // 2
    center_y = screen_height // 2
    radius = screen_height // 2 - 20
    end_x = center_x + radius * math.cos(math.radians(angle))
    end_y = center_y - radius * math.sin(math.radians(angle))
    pygame.draw.line(screen, color, (center_x, center_y), (end_x, end_y), 3)

def draw_dot(screen, color, angle, distance, servo_angle):
        center_x = screen_width // 2
        center_y = screen_height // 2
        radius = distance * 3 if distance is not None else None
        if radius is not None:
            # xy of dot
            x = center_x + radius * math.cos(math.radians(angle))
            y = center_y - radius * math.sin(math.radians(angle))
        
            scanned_positions.append((int(x), int(y)))
            green_line_end_x = center_x + screen_width * math.cos(math.radians(servo_angle)) / 2
            pygame.draw.circle(screen,color, (int(x), int(y)), 5)

# Define a function to measure distance
def distance():
    # Send 10us pulse to trigger pin
    GPIO.output(trig_pin, True)
    time.sleep(0.001)
    GPIO.output(trig_pin, False)

    pulse_start = time.time()
    while GPIO.input(echo_pin) == 0:
        pulse_start = time.time()

    pulse_end = time.time()
    while GPIO.input(echo_pin) == 1:
        pulse_end = time.time()

    #distance in cm
    pulse_duration = pulse_end - pulse_start
    distance_cm = pulse_duration * 17150
    distance_cm = round(distance_cm, 2)
        
    return distance_cm

i = 2.5
screen = init_screen()
draw_line(screen, (0, 255, 0), i) 

while True:
    #servo moves back and forth
    i = 2.5
    while i < 12.5:
        servo.ChangeDutyCycle(i)
        time.sleep(0.01)
        dist = distance()
        screen.fill((0, 0, 0))
        
        angle = (i - 2.5) * 180 / 10
        
        draw_line(screen, (0, 255, 0), angle)
        draw_dot(screen, (255, 255, 255), angle, dist if dist <=100 else None,angle)
       
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GPIO.cleanup()
                pygame.quit()
                sys.exit()
        i += 0.1
    scanned_positions= []
    j = 12.5
    while j > 2.5:
        servo.ChangeDutyCycle(j)
        time.sleep(0.01)
        dist = distance()
        screen.fill((0, 0, 0))
        angle = (j - 2.5) * 180 / 10
        
        draw_line(screen, (0, 255, 0), angle)
        
        draw_dot(screen, (255, 255, 255), angle, dist if dist <=100 else None, angle)
        for pos in scanned_positions:
            pygame.draw.circle(screen, (255, 255, 255), pos, 2)
            pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GPIO.cleanup()
                pygame.quit()
                sys.exit()
        j -= 0.1
    scanned_positions=[]
