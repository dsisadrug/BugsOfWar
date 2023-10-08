import pygame
import random
import math

pygame.init()

screen_w = 800
screen_h = 600

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

s_font = pygame.font.SysFont("comicsansms", 20)

clock = pygame.time.Clock()
game_display = pygame.display.set_mode((screen_w, screen_h))


# tank block
class Tank:
    def __init__(self, rect_x, rect_y, direction):
        self.rect_x = rect_x
        self.rect_y = rect_y
        self.direction = direction  # 1 - left; -1 - right
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

    def draw_with_mask(self):
        self.surf.fill(self.bg_color)
        self.surf.set_colorkey(self.bg_color)
        pygame.draw.circle(self.surf, self.color, (self.x, self.y), int(self.h / 2))
        pygame.draw.rect(
            self.surf, self.color, (self.x - self.h, self.y, self.w, self.h)
        )
        pygame.draw.line(
            self.surf,
            self.color,
            (self.x, self.y),
            (self.line_x, self.line_y),
            self.turret_w,
        )
        start_x = 15
        for i in range(7):
            pygame.draw.circle(
                self.surf, self.color, (self.x - start_x, self.y + 20), self.wheel_w
            )
            start_x -= 5
        pygame.draw.rect(
            self.surf,
            "#808080",
            (int(0.05 * self.w), int(0.05 * self.surf_h), int(100 / 3), 5),
        )
        pygame.draw.rect(
            self.surf,
            self.health_color,
            (int(0.05 * self.w), int(0.05 * self.surf_h), int(self.health / 3), 5),
        )

    def update_turret(self, change):
        """Updates the turret's direction.

        Args:
            change (int): Change in direction (1 left; -1 right)
        """
        self.direction = change
        self.line_x = self.x - (self.turret_positions[self.tur_pos][0] * self.direction)
        self.line_y = self.y - self.turret_positions[self.tur_pos][1]

    def decrease_health(self, damage):
        """Decrease the health on damage and change the color of the healthbar

		Args:
			damage (int): The amount of damage to decrease health by
		"""
        self.health -= damage
        if self.health <= 25:
            self.health_color = red
        elif self.health <= 75:
            self.health_color = yellow


class Mount:
    def __init__(self, display, shape):
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


def ground_tank(tank, mount):
    t_offset = (mount.rect.left - tank.rect.left, mount.rect.top - tank.rect.top)
    overlap_flag = False

    while overlap_flag == False:
        tank.rect = tank.rect.move((0, 1))
        t_offset = (mount.rect.left - tank.rect.left, mount.rect.top - tank.rect.top)
        if tank.rect.bottom >= screen_h:
            tank.rect.bottom = screen_h
            overlap_flag = True
        elif tank.mask.overlap_area(mount.mask, t_offset) > 50:
            tank.rect = tank.rect.move((0, -1))
            overlap_flag = True
    return tank


def move_tank(tank, mount, step):
    """Makes the tank move in the the given direction
    and also allows the tank to climb up to a certain slope

	Args:
		tank (_type_): _description_
		mount (_type_): _description_
		step (_type_): _description_

	Returns:
		_type_: _description_
	"""
    tank.rect = tank.rect.move((step, 0))  # make the tank move
    t_offset = (mount.rect.left - tank.rect.left, mount.rect.top - tank.rect.top)
    if (
        tank.mask.overlap_area(mount.mask, t_offset) > 50
    ):  # if the movement results in the tank overlapping with the mount
        tank.rect = tank.rect.move((0, -5))  # raise the tank to the acceptable slope
        t_offset = (mount.rect.left - tank.rect.left, mount.rect.top - tank.rect.top)
        if (
            tank.mask.overlap_area(mount.mask, t_offset) > 50
        ):  # if it is still overlapping
            tank.rect = tank.rect.move(
                (-step, 0)
            )  # return it to its initial position on the x axis (ground_tank will handle the y axis)
    return tank


def explosion(x, y, size=explosion_radius):
    explode = True

    while explode:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        color_choices = [red, light_red, yellow, light_yellow]

        magnitude = 1
        for tank in tank_list:
            game_display.blit(tank.surf, tank.rect)
        #game_display.blit(tank1.surf, tank1.rect)
        # game_display.blit(tank2.surf, tank2.rect)

        while magnitude < size:
            exploding_bit_x = x + random.randrange(-1 * magnitude, magnitude)
            exploding_bit_y = y + random.randrange(-1 * magnitude, magnitude)

            pygame.draw.circle(
                game_display,
                color_choices[random.randrange(0, 4)],
                (exploding_bit_x, exploding_bit_y),
                random.randrange(1, 5),
            )
            magnitude += 1
            pygame.display.update()
            clock.tick(100)

        explode = False


def fireshell(tank, direction, power):
    # damage = 0
    # take the gun coordinates and fire the shell
    fire = True
    # convert the tuple into a list to enable modifications of the shell position
    print("Fire!")

    tur_pos = tank.tur_pos
    gun_power = power

    shell_surf = pygame.Surface((10, 10))
    shell_surf.fill(blue)
    shell_surf.set_colorkey(blue)

    turret_exit = (tank.rect.center[0] - (15 * direction), tank.rect.top + 10)

    shell_rect = shell_surf.get_rect(center=turret_exit)
    pygame.draw.circle(shell_surf, red, (5, 5), 5)
    shell_mask = pygame.mask.from_surface(shell_surf)
    prev_coords = []

    # make the loop stop after a single press of the space key
    while fire:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        if shell_rect.bottom > screen_h:
            shell_rect.bottom = screen_h
            explosion(
                shell_rect.left,
                shell_rect.top,
                size=explosion_radius,
            )
            explode_coords = (shell_rect.left, shell_rect.top - 300)
            explode_list.append(explode_coords)
            fire = False

        x_change = (12 - tur_pos) * (2 * direction)
        y_change = int(
            (((shell_rect.center[0] - turret_exit[0]) * 0.015 / (gun_power / 50)) ** 2)
            - (tur_pos + tur_pos / (12 - tur_pos))
        )

        # shell_rect.center[1] += y_change
        shell_rect = shell_rect.move((-x_change, y_change))
        # calculate the offset
        offset_x = shell_rect.left - mount.rect.left
        offset_y = shell_rect.top - mount.rect.top

        # check if there is a collision or not
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
            explode_offset_x = explode_rect.left - mount.rect.left
            explode_offset_y = explode_rect.top - mount.rect.top
            for vehicle in tank_list:
                if math.dist(shell_rect.center, vehicle.rect.center) < (
                    explosion_radius
                    + math.dist(vehicle.rect.center, vehicle.rect.bottomleft)
                ):
                    vehicle.decrease_health(25)
            mount.mask.erase(explode_mask, (explode_offset_x, explode_offset_y))
            fire = False
        game_display.blit(shell_surf, shell_rect)
        pygame.display.update()
        prev_coords.append(shell_rect.center)
        if len(prev_coords) > 1:
            pygame.draw.circle(game_display, blue, prev_coords[-2], 5)
        clock.tick(60)


def game_over(win_index):
    game_over = True

    while game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    quit()

        game_display.fill(white)
        text_surf = s_font.render(f"Player {win_index+1} won!", True, black)
        text_rect = text_surf.get_rect()
        text_rect.center = (screen_w / 2), (screen_h / 2)
        game_display.blit(text_surf, text_rect)

        pygame.display.update()
        clock.tick(30)


# explosion block
explode_surf = pygame.Surface((100, 100))
explode_surf.fill(blue)
explode_surf.set_colorkey(blue)
pygame.draw.circle(explode_surf, red, (50, 50), 50)
explode_mask = pygame.mask.from_surface(explode_surf)

"""
Create first the surface, draw a polygon on it, 
then set its rect to cover the lesser half of the screen,
finally - create a mask for collision purposes
"""
explode_list = []

mount = Mount(display=game_display, shape=mount_shape)
tank1 = Tank(rect_x=int(0.1 * 800), rect_y=int(0.1 * 600), direction=-1)
tank1.draw_with_mask()
tank2 = Tank(rect_x=int(0.9 * 800), rect_y=int(0.1 * 600), direction=1)
tank2.draw_with_mask()

tank_list = [tank1, tank2]
tank_index = 0
current_tank = tank_list[tank_index]

left_flag = False
right_flag = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                power_change += 1
            elif event.key == pygame.K_LEFT:
                left_flag = True
                current_tank.update_turret(change=1)
                current_tank.draw_with_mask()
            elif event.key == pygame.K_RIGHT:
                right_flag = True
                current_tank.update_turret(change=-1)
                current_tank.draw_with_mask()
            elif event.key == pygame.K_UP:
                up_flag = True
                if current_tank.tur_pos < 8:
                    current_tank.tur_pos += 1
                    current_tank.update_turret(
                        change=current_tank.direction
                    )
                    current_tank.draw_with_mask()
                    clock.tick(10)
            elif event.key == pygame.K_DOWN:
                up_flag = True
                if current_tank.tur_pos > 0:
                    current_tank.tur_pos -= 1
                    current_tank.update_turret(
                        change=current_tank.direction
                    )
                    current_tank.draw_with_mask()
                    clock.tick(10)
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                left_flag = False
            elif event.key == pygame.K_RIGHT:
                right_flag = False
            elif event.key == pygame.K_SPACE:
                fireshell(
                    current_tank,
                    direction=current_tank.direction,
                    power=gun_power,
                )
                power_change = 0
                gun_power = 1  # must be at leat 1 to prevent dividionbyzero error
                tank_index += 1
                tank_index %= 2
                current_tank = tank_list[tank_index]

    gun_power += power_change
    if gun_power > 100:
        gun_power = 100
    clock.tick(35)

    """
	Render all the appropriate objects:
	Screen, sun, power rectangle, mount, tanks etc
	"""

    # render the screen, sun and surface
    game_display.fill(blue)
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

    # Tanks
    for tank in tank_list:
        tank = ground_tank(tank,mount)

    # The mountain
    game_display.blit(mount.surf, mount.rect)

    if left_flag:
        current_tank = move_tank(
            current_tank, mount, -5
        )
        clock.tick(15)
    if right_flag:
        current_tank = move_tank(current_tank, mount, 5)
        clock.tick(15)

    # now draw this surface with the color depending on the collision or not
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

    pygame.display.update()

    for vehicle in tank_list:
        if vehicle.health == 0:
            game_over(win_index=(tank_list.index(vehicle) + 1) % 2)
