import pygame
import random
import math

pygame.init()

"""
Global variables
"""

# screen dimensions
screen_w = 800
screen_h = 600

# colors
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (50, 125, 255)
orange = (200, 100, 0)

light_red = (255, 0, 0)
yellow = (200, 200, 0)
light_yellow = (245, 245, 0)
light_green = (0, 255, 0)

color = orange

# shape variables
tank_w = 40
tank_h = 20
gun_power = 1
power_change = 0
turret_w = 5
wheel_w = 5
explosion_radius = 50
mount_shape = (
    (0, random.randrange(0.75 * 200, 1.25 * 200)),
    (random.randrange(0.75 * 200, 1.25 * 200), random.randrange(0.8 * 150, 1.2 * 150)),
    (random.randrange(0.8 * 450, 1.2 * 450), random.randrange(0.8 * 250, 1.2 * 250)),
    (random.randrange(0.8 * 650, 1.2 * 650), random.randrange(0.75 * 100, 1.25 * 100)),
    (800, random.randrange(0.75 * 200, 1.25 * 200)),
    (800, 600),
    (0, 600),
)

# general pygame settings
s_font = pygame.font.SysFont("comicsansms", 20)
clock = pygame.time.Clock()
game_display = pygame.display.set_mode((screen_w, screen_h))


class Tank:
    """A class representing a tank."""

    def __init__(self, rect_x, rect_y, direction):
        """Constructs all the important attributes of the Tank class.

        Args:
            rect_x (int): The left most x coordinate of the tank's rectangle
            rect_y (int): The top most y coordinate of the tank's rectangle
            direction (int): The direction the tank is facing (1 - left; -1 - right)
        """
        self.rect_x = rect_x
        self.rect_y = rect_y
        self.direction = direction
        self.moving = False
        self.surf_h = 52
        self.turret_w = 5
        self.wheel_w = 5
        self.tur_pos = 4
        self.w = 40
        self.h = 20
        self.x = self.w / 2
        self.y = self.surf_h / 2
        self.bg_color = blue
        self.color = black
        self.surf = pygame.Surface((self.w, self.surf_h))
        self.rect = self.surf.get_rect(center=(self.rect_x, self.rect_y))
        self.mask = pygame.mask.from_surface(self.surf)
        self.health = 100
        self.health_color = green
        self.turret_positions = [
            (27, 2),
            (26, 5),
            (25, 8),
            (23, 12),
            (20, 14),
            (18, 15),
            (15, 17),
            (13, 19),
            (11, 21),
        ]
        self.line_x = self.x - (self.turret_positions[self.tur_pos][0] * self.direction)
        self.line_y = self.y - self.turret_positions[self.tur_pos][1]

    def draw_shapes(self):
        """Draws the shapes of the tank on the screen"""
        self.surf.fill(self.bg_color)
        self.surf.set_colorkey(self.bg_color)

        # draw the body of the tank
        pygame.draw.circle(self.surf, self.color, (self.x, self.y), int(self.h / 2))
        pygame.draw.rect(
            self.surf, self.color, (self.x - self.h, self.y, self.w, self.h)
        )

        # draw the turret
        pygame.draw.line(
            self.surf,
            self.color,
            (self.x, self.y),
            (self.line_x, self.line_y),
            self.turret_w,
        )

        # draw the wheels
        start_x = 15
        for i in range(7):
            pygame.draw.circle(
                self.surf, self.color, (self.x - start_x, self.y + 20), self.wheel_w
            )
            start_x -= 5

        # draw the health bar
        pygame.draw.rect(
            self.surf,
            self.health_color,
            (int(0.05 * self.w), int(0.05 * self.surf_h), int(self.health / 3), 5),
        )

    def update_turret(self):
        """Updates the turret's direction.

        Args:
                change (int): Change in direction (1 left; -1 right)
        """
        self.line_x = self.x - (
            self.turret_positions[self.tur_pos][0] * (self.direction * -1)
        )
        self.line_y = self.y - self.turret_positions[self.tur_pos][1]

    def decrease_health(self, damage):
        """Decrease the health on damage and change the color of the healthbar

        Args:
                damage (int): The amount of damage to decrease health by
        """
        self.health -= damage

        # change the color of the health bar based on health
        if self.health <= 25:
            self.health_color = red
        elif self.health <= 75:
            self.health_color = yellow

    def ground(self, mount):
        """Drops the tank to the ground if it loses touch with the mount's surface

        Args:
            mount (Mount): The mount on which the tank sits
        """
        t_offset = (mount.rect.left - self.rect.left, mount.rect.top - self.rect.top)
        overlap_flag = False

        # drop the tank until it touches the ground
        while overlap_flag == False:
            self.rect = self.rect.move((0, 1))
            t_offset = (
                mount.rect.left - self.rect.left,
                mount.rect.top - self.rect.top,
            )
            # stop if it touches the bottom of the screen
            if self.rect.bottom >= screen_h:
                self.rect.bottom = screen_h
                overlap_flag = True
            # or stop if it touches the mount
            elif self.mask.overlap_area(mount.mask, t_offset) > 50:
                self.rect = self.rect.move((0, -1))
                overlap_flag = True

    def move(self, mount, step):
        """Makes the tank move in the the given direction
        and also allows the tank to climb up to a certain slope

        Args:
                mount (Mount): The mount that the tank is moving on
                step (int): The step by which the tank is moving
        """
        self.rect = self.rect.move((step, 0))  # make the tank move
        t_offset = (mount.rect.left - self.rect.left, mount.rect.top - self.rect.top)
        if (
            self.mask.overlap_area(mount.mask, t_offset) > 50
        ):  # if the movement results in the tank overlapping with the mount
            self.rect = self.rect.move(
                (0, -5)
            )  # raise the tank to the acceptable slope
            t_offset = (
                mount.rect.left - self.rect.left,
                mount.rect.top - self.rect.top,
            )
            if (
                self.mask.overlap_area(mount.mask, t_offset) > 50
            ):  # if it is still overlapping
                self.rect = self.rect.move(
                    (-step, 0)
                )  # return it to its initial position on the x axis (ground will handle the y axis)

    def fire_shell(self, power):
        """Fires a shell in the direction the tank is facing.

        Args:
            power (int): The power that is applied to the shot.
        """

        # set the fire flag
        fire = True

        # Assign
        tur_pos = self.tur_pos
        gun_power = power

        shell_surf = pygame.Surface((10, 10))
        shell_surf.fill(blue)
        shell_surf.set_colorkey(blue)

        # Draw the first frame of the shell after shooting
        turret_exit = (self.rect.center[0] + (15 * self.direction), self.rect.top + 10)
        shell_rect = shell_surf.get_rect(center=turret_exit)
        pygame.draw.circle(shell_surf, red, (5, 5), 5)
        shell_mask = pygame.mask.from_surface(shell_surf)

        prev_coords = []

        # make the loop stop after a single press of the space key
        while fire:
            for event in pygame.event.get():
                # Closing the window stops the game
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            # make the shell explode if it hits the bottom of the screen
            if shell_rect.bottom > screen_h:
                shell_rect.bottom = screen_h
                explosion(
                    shell_rect.left,
                    shell_rect.top,
                    size=explosion_radius,
                )
                explode_coords = (shell_rect.left, shell_rect.top - 300)
                # add the coordinates to the list and exit the loop
                explode_list.append(explode_coords)

                # check if any vehicle is in range of explosion, if yes decrease health
                for vehicle in tank_list:
                    if math.dist(shell_rect.center, vehicle.rect.center) < (
                        explosion_radius
                        + math.dist(vehicle.rect.center, vehicle.rect.bottomleft)
                    ):
                        vehicle.decrease_health(25)

                fire = False

            # Calculate changes in the x and y coordinates for next frame
            x_change = (12 - tur_pos) * (2 * self.direction)
            y_change = int(
                (
                    ((shell_rect.center[0] - turret_exit[0]) * 0.015 / (gun_power / 50))
                    ** 2
                )
                - (tur_pos + tur_pos / (12 - tur_pos))
            )

            # move the shell by (x_change, y_change)
            shell_rect = shell_rect.move((x_change, y_change))

            # calculate the offset
            offset_x = shell_rect.left - mount.rect.left
            offset_y = shell_rect.top - mount.rect.top

            # Upon collision with mount, trigger explosion
            if mount.mask.overlap(shell_mask, (offset_x, offset_y)):
                explosion(
                    shell_rect.left,
                    shell_rect.top,
                    size=explosion_radius,
                )
                explode_coords = (shell_rect.left, shell_rect.top - mount.h)
                explode_list.append(explode_coords)
                explode_rect = explode_surf.get_rect(
                    center=(explode_coords[0], explode_coords[1] + 300)
                )

                # check if any vehicle is in range of explosion, if yes decrease health
                for vehicle in tank_list:
                    if math.dist(shell_rect.center, vehicle.rect.center) < (
                        explosion_radius
                        + math.dist(vehicle.rect.center, vehicle.rect.bottomleft)
                    ):
                        vehicle.decrease_health(25)

                # Erode the mount based on blast radius and finally exit while loop
                mount.erode(explode_rect)
                fire = False

            # draw the next position of the shell red and paint the previous one blue to simulate movement
            game_display.blit(shell_surf, shell_rect)
            pygame.display.update()
            prev_coords.append(shell_rect.center)
            if len(prev_coords) > 1:
                pygame.draw.circle(game_display, blue, prev_coords[-2], 5)
            clock.tick(60)


class Mount:
    def __init__(self, display, shape):
        """Constructs all the important attributes of the Mount class.

        Args:
            display (display): The game display
            shape (shape): The shape of the mountain
        """
        self.display = display
        self.w = 800
        self.h = 300
        self.center_x = 400
        self.center_y = 450
        self.shape = shape
        self.color = orange
        self.surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        pygame.draw.polygon(
            self.surf, self.color, self.shape
        )  # polygons - KEEP IN MIND! - order of coordinates matter! lines can cross each other
        self.rect = self.surf.get_rect(center=(400, 450))
        self.mask = pygame.mask.from_surface(self.surf)
        self.display.blit(self.surf, self.rect)

    def erode(self, explode_rect):
        """Erodes part of the mount

        Args:
            explode_rect (Rect): The rectangle of the explosion
        """
        explode_offset_x = explode_rect.left - self.rect.left
        explode_offset_y = explode_rect.top - self.rect.top

        # Remove the coordinates of the explosin from the mount's mask
        self.mask.erase(explode_mask, (explode_offset_x, explode_offset_y))


def explosion(x, y, size=explosion_radius):
    """Simulates an explosion.

    Args:
        x (int): The x coordinate of the blast epicentrum
        y (int): The y coordinate of the blast epicentrum
        size (int, optional): The size of the explosion. Defaults to explosion_radius.
    """
    explode = True

    while explode:
        for event in pygame.event.get():
            # Closing the window stops the game
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # List of colors for explosion particles
        color_choices = [red, light_red, yellow, light_yellow]

        # Start with a small magnitude of particles and increase radius
        magnitude = 1
        while magnitude < size:
            # Assign random coordinates
            exploding_bit_x = x + random.randrange(-1 * magnitude, magnitude)
            exploding_bit_y = y + random.randrange(-1 * magnitude, magnitude)

            # Draw the particle with a random color from the list
            pygame.draw.circle(
                game_display,
                color_choices[random.randrange(0, 4)],
                (exploding_bit_x, exploding_bit_y),
                random.randrange(1, 5),
            )
            magnitude += 1
            pygame.display.update()
            clock.tick(100)

        # Exit the while loop
        explode = False


def game_over(win_index):
    """Render the game over screen.

    Args:
        win_index (int): The index of the winning player.
    """
    game_over = True

    while game_over:
        for event in pygame.event.get():
            # Closing the window stops the game
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            # So does pressing the 'Q' key:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    quit()

        # render the game over window
        game_display.fill(white)
        text_surf = s_font.render(f"Player {win_index+1} won!", True, black)
        text_rect = text_surf.get_rect()
        text_rect.center = (screen_w / 2), (screen_h / 2)
        game_display.blit(text_surf, text_rect)

        pygame.display.update()
        clock.tick(30)


"""
Create explosion and first objects (Tank, Mount)
"""

# explosion block
explode_surf = pygame.Surface((100, 100))
explode_surf.fill(blue)
explode_surf.set_colorkey(blue)
pygame.draw.circle(explode_surf, red, (50, 50), 50)
explode_mask = pygame.mask.from_surface(explode_surf)

# List of explosions that will happen throughout the game
explode_list = []

# Instantiate Mount and Tank objects
mount = Mount(display=game_display, shape=mount_shape)
tank1 = Tank(rect_x=int(0.1 * 800), rect_y=int(0.1 * 600), direction=-1)
tank1.draw_shapes()
tank2 = Tank(rect_x=int(0.9 * 800), rect_y=int(0.1 * 600), direction=1)
tank2.draw_shapes()

# Add tanks to list and select the first tank
tank_list = [tank1, tank2]
tank_index = 0
current_tank = tank_list[tank_index]

current_tank.moving = False


"""
Main game loop
"""

while True:
    for event in pygame.event.get():
        # Closing the window stops the game
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN:
            # increasing power of the shot
            if event.key == pygame.K_SPACE:
                power_change += 1
            # move left
            elif event.key == pygame.K_LEFT:
                current_tank.moving = True
                current_tank.direction = -1
            # move right
            elif event.key == pygame.K_RIGHT:
                current_tank.moving = True
                current_tank.direction = 1
            # move the turret up
            elif event.key == pygame.K_UP:
                if current_tank.tur_pos < 8:
                    current_tank.tur_pos += 1
            # move the turret down
            elif event.key == pygame.K_DOWN:
                if current_tank.tur_pos > 0:
                    current_tank.tur_pos -= 1
            current_tank.update_turret()
            current_tank.draw_shapes()
        elif event.type == pygame.KEYUP:
            # letting go of either left or right arrow stops the tank
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                current_tank.moving = False
            # letting go of the space bar shoots the shell
            elif event.key == pygame.K_SPACE:
                current_tank.fire_shell(power=gun_power)
                power_change = 0
                gun_power = 1  # must be at leat 1 to prevent dividionbyzero error
                tank_index += 1
                tank_index %= 2
                current_tank = tank_list[tank_index]

    # increase the power up to 100
    gun_power += power_change
    if gun_power > 100:
        gun_power = 100
    clock.tick(35)

    """
    Render all the appropriate objects:
    Screen, sun, power rectangle, mount, tanks etc
    """

    # Blue background
    game_display.fill(blue)

    # The red sun
    pygame.draw.circle(game_display, red, (150, 150), 100)

    # draw the power rectangle
    pygame.draw.rect(
        game_display, white, (int(0.88 * screen_w), int(0.05 * screen_h), 80, 50)
    )  # backdrop
    text = s_font.render("Power", True, black)
    game_display.blit(
        text, [int(0.895 * screen_w), int(0.05 * screen_h)]
    )  # "Power" text
    pygame.draw.rect(
        game_display,
        black,
        (int(0.9 * screen_w) - 3, int(0.1 * screen_h) - 3, 56, 16),
        3,
    )  # black frame
    pygame.draw.rect(
        game_display,
        red,
        (int(0.9 * screen_w), int(0.1 * screen_h), int(gun_power / 2), 10),
    )  # filling out when charging

    # Make the tanks stick to the ground
    for tank in tank_list:
        tank.ground(mount)

    # Display the mountain
    game_display.blit(mount.surf, mount.rect)

    # Move the tank on the screen
    if current_tank.moving:
        current_tank.move(mount, 5 * current_tank.direction)
        clock.tick(15)

    # Draw the blue circles after explosions to simulate craters
    if len(explode_list) > 0:
        for coords in explode_list:
            pygame.draw.circle(mount.surf, blue, coords, 50)

    # display the tanks as well as highlight the current tank with a yellow dot
    for tank in tank_list:
        game_display.blit(tank.surf, tank.rect)
    pygame.draw.circle(
        game_display,
        yellow,
        (
            current_tank.rect.center[0],
            current_tank.rect.center[1] - 35,
        ),
        5,
    )

    # Update the display after configuring everything
    pygame.display.update()

    # check if the game ended after rendering everything
    for vehicle in tank_list:
        if vehicle.health == 0:
            game_over(win_index=(tank_list.index(vehicle) + 1) % 2)
