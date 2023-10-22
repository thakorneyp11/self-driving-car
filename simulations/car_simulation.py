import pygame
import math


class CarSimulator:
    def __init__(self, width=1200, height=400, enable_pygame=False):
        # Initialize the pygame
        pygame.init()

        # Set the dimensions of the window
        self.win_size = self.width, self.height = width, height
        self.enable_pygame = enable_pygame
        if self.enable_pygame:
            self.screen = pygame.display.set_mode(self.win_size)
            pygame.display.set_caption("Car Dynamics Simulation")

        # Car appearance in the simulation
        self.WHITE = (255, 255, 255)
        self.CAR_COLOR = (0, 0, 0)
        self.car_length = 50  # Just for representation in the simulation
        
        self.reset()

    def reset(self):
        # Car parameters (initial)
        self.car_speed = 0
        self.car_orientation = 0  # In degrees, 0 pointing to the right, counterclockwise
        self.trajectory = []

        # Simulation parameters
        self.time_step = 0.1  # Time step in seconds
        self.max_steering_angle = 45  # in degrees
        self.max_acceleration = 10.0  # units/pixel per second^2
        self.max_speed = 50.0  # units/pixel per second
        self.run = True
        
        # control target parameters
        self.initial_y = 300
        self.target_y = 200
        self.target_x = 200
        self.car_pos = pygame.Vector2(50, self.initial_y)  # x, y

    def update_car(self, steering_angle, acceleration):
        # Limit the steering angle and acceleration to min/max allowed values
        steering_angle = max(-self.max_steering_angle, min(steering_angle, self.max_steering_angle))
        acceleration = max(-self.max_acceleration, min(acceleration, self.max_acceleration))

        if abs(steering_angle) > self.max_steering_angle:
            raise ValueError("Exceeding max steering angle")

        if abs(acceleration) > self.max_acceleration:
            raise ValueError("Exceeding max acceleration")

        # Update speed based on acceleration
        self.car_speed += acceleration * self.time_step
        self.car_speed = max(-self.max_speed, min(self.car_speed, self.max_speed))

        # Calculate change in orientation
        orientation_change = (self.car_speed / self.car_length) * math.tan(math.radians(steering_angle)) * self.time_step
        self.car_orientation += math.degrees(orientation_change) % 360

        # Update position based on speed and orientation
        self.car_pos.x += self.car_speed * math.cos(math.radians(self.car_orientation)) * self.time_step
        self.car_pos.y += self.car_speed * math.sin(math.radians(self.car_orientation)) * self.time_step
        self.trajectory.append([self.car_pos.x, self.car_pos.y])

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False

        keys = pygame.key.get_pressed()

        # Set acceleration and steering based on keys
        acceleration = 0
        if keys[pygame.K_UP]:
            acceleration = self.max_acceleration
        if keys[pygame.K_DOWN]:
            acceleration = -self.max_acceleration

        steering_angle = 0
        if keys[pygame.K_LEFT]:
            steering_angle = -self.max_steering_angle
        if keys[pygame.K_RIGHT]:
            steering_angle = self.max_steering_angle

        # Check for ESC key or 'Q' key to quit the game
        if keys[pygame.K_ESCAPE] or keys[pygame.K_q]:
            self.run = False

        return steering_angle, acceleration

    def run_simulation(self):
        while self.run:
            steering_angle, acceleration = self.handle_events()

            # Update car dynamics
            self.update_car(steering_angle, acceleration)

            # Drawing
            self.draw_canvas()
            
            if self.car_pos.x >= self.width:
                self.run = False

        # Quit pygame
        pygame.quit()

    def simulate_session(self, controller, initial_position: list, max_steps=500, time_sample=0.1):
        # Reset the simulation
        self.reset()
        
        # Set initial position
        x_pos = initial_position[0]
        y_pos = initial_position[1]
        self.car_pos = pygame.Vector2(x_pos, y_pos)
        
        # Setup parameters
        self.car_speed = 50
        acceleration = 0
        
        trajectory = list()
        
        while len(trajectory) < max_steps:
            # Recieve control signal from PID controller
            steering_angle = controller.update(self.car_pos.y, define_delta_time=time_sample)
            
            # Update car dynamics
            self.update_car(steering_angle, acceleration)
            
            # Save trajectory
            _trajectory = [self.car_pos.x, self.car_pos.y]
            trajectory.append(_trajectory)
            
        return trajectory

    def _draw_axis_labels(self):
        # Choose a font and size for the labels
        font = pygame.font.Font(None, 24)

        # Calculate the range and step for labels
        x_step = 100  # Adjust the step for different label density
        y_step = 100
        x_range = range(0, self.width + 1, x_step)
        y_range = range(0, self.height + 1, y_step)

        # Draw the grid lines and labels for the x-axis
        for x in x_range:
            # Draw grid line
            pygame.draw.line(self.screen, (217, 217, 217), (x, 0), (x, self.height - 1), 1)  # vertical lines

            # Create the text for the label
            label = font.render(str(x), True, (0, 0, 0))  # Black color

            # Position and draw the text
            label_rect = label.get_rect(center=(x, self.height - 10))
            self.screen.blit(label, label_rect)

        # Draw the grid lines and labels for the y-axis
        for y in y_range:
            # Draw grid line
            pygame.draw.line(self.screen, (217, 217, 217), (0, y), (self.width - 1, y), 1)  # horizontal lines

            # Create the text for the label, inverting the y value because the y-axis is flipped in Pygame
            label = font.render(str(-(y - self.height // 2)), True, (0, 0, 0))  # Black color

            # Position and draw the text
            label_rect = label.get_rect(center=(20, y))
            self.screen.blit(label, label_rect)

    def _draw_car(self):
        car_rect = pygame.Rect(0, 0, self.car_length, self.car_length / 2)
        car_rect.center = (self.width / 2, self.height / 2)

        # Create a new surface with the same dimensions as the car, and draw the car on this surface
        car_surface = pygame.Surface((car_rect.width, car_rect.height), pygame.SRCALPHA)

        # Draw main body of the car
        pygame.draw.rect(car_surface, self.CAR_COLOR, car_surface.get_rect())

        # Draw the front part of the car (as a smaller rectangle or another shape)
        front_indicator_color = (0, 255, 0)  # Green color for the front
        front_indicator = pygame.Rect(3 * self.car_length / 4, self.car_length / 4, self.car_length / 4, self.car_length / 4)
        pygame.draw.rect(car_surface, front_indicator_color, front_indicator)

        # Rotate this surface containing the car, and get the new bounding rectangle
        rotated_surface = pygame.transform.rotate(car_surface, -self.car_orientation)
        rotated_rect = rotated_surface.get_rect(center=car_rect.center)

        # Blit the rotated surface onto the screen, using the bounding rectangle to position it
        self.screen.blit(rotated_surface, self.car_pos - pygame.Vector2(rotated_rect.width / 2, rotated_rect.height / 2))

    def _draw_coordinates(self):
        # Select the font and size for the coordinates
        font = pygame.font.Font(None, 24)

        # Create the text for the coordinates
        text = f'x: {self.car_pos.x:.0f}, y: {self.car_pos.y:.0f}'  # Display the coordinates with two decimal places
        label = font.render(text, True, (0, 0, 0))  # Black color

        # Calculate position for the text, slightly above the car's current position
        label_rect = label.get_rect(center=(self.car_pos.x, self.car_pos.y - self.car_length))

        # Draw the text on the screen
        self.screen.blit(label, label_rect)

    def _draw_target_lines(self):
        # Ensure the target y-values are set
        if not hasattr(self, 'initial_y') or not hasattr(self, 'target_y'):
            raise ValueError("Target y-values are not set.")

        # Draw the line for self.initial_y in the first 100 pixels
        pygame.draw.line(self.screen, (255, 0, 0), (0, self.initial_y), (self.target_x, self.initial_y), 4)  # Blue color line

        # Draw the line for self.target_y from 100 pixels to the end of the window
        pygame.draw.line(self.screen, (255, 0, 0), (self.target_x, self.target_y), (self.width, self.target_y), 4)  # Green color line

    def _draw_trajectory(self):
        if len(self.trajectory) > 1:
            pygame.draw.lines(self.screen, (0, 0, 255), False, self.trajectory, 2)

    def draw_canvas(self):
        self.screen.fill(self.WHITE)
        self._draw_axis_labels()
        self._draw_target_lines()
        self._draw_car()
        self._draw_coordinates()
        self._draw_trajectory()
        pygame.display.flip()
        pygame.time.Clock().tick(30)  # Ensure the program maintains a rate of 30 frames per second
        

# Running the simulation
if __name__ == "__main__":
    sim = CarSimulator(enable_pygame=True)
    sim.run_simulation()  # Open the interactive pygame window for Manual Control


""" Sample script to apply PID controller to this simulation with Pygame window display

import pygame

from controllers.pid_controller import PID
from simulations.car_simulation import CarSimulator

pid = PID(Kp=0.2, Ki=0, Kd=0.2)
pid.set_sample_time(0.1)
pid.set_target(200)

simulation = CarSimulator(enable_pygame=True)

# initial control
steering_angle = 0
acceleration = 0

# Update the PID and the simulation for this time step
simulation.car_speed = 50
while simulation.run:
    current_y = simulation.car_pos.y
    
    # Calculates PID value for given reference feedback
    steering_angle = pid.update(current_y)
    
    # Update car dynamics        
    simulation.update_car(steering_angle, 0)
    simulation.draw_canvas()
    
    if simulation.car_pos.x >= simulation.width:
        simulation.run = False

# Quit pygame
pygame.quit()
"""
