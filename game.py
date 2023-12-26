import pygame
import os
from network import Network

pygame.font.init()
pygame.mixer.init()

# Dimensions
WIN_WIDTH, WIN_HEIGHT = 900, 500
BORDER = (WIN_WIDTH//2 - 5, 0, 10, WIN_HEIGHT)
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 55, 40

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Game specific events
PLAYER_HIT = pygame.USEREVENT + 1 # Event for when the player is hit
ENEMY_HIT = pygame.USEREVENT + 2 # Event for when the enemy is hit

# Fonts
WINNER_FONT = pygame.font.SysFont('sans-courier', 100) # Font for result text
HEALTH_FONT = pygame.font.SysFont('sans-courier', 40) # Font for health

# Sounds
BULLET_HIT_SOUND = pygame.mixer.Sound(
    os.path.join("assets", "Grenade+1.mp3")) # Sound when a bullet hits a spaceship
BULLET_FIRE_SOUND = pygame.mixer.Sound(
    os.path.join("assets", "Gun+Silencer.mp3")) # Sound when a bullet is fired

# Visuals
SPACE = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "space.png")), (WIN_WIDTH, WIN_HEIGHT)) # Background
YELLOW_SPACESHIP_IMAGE = pygame.image.load(
    os.path.join("assets", "spaceship_yellow.png")) # Yellow spaceship
YELLOW_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(YELLOW_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 90) # Rotating the image
RED_SPACESHIP_IMAGE = pygame.image.load(
    os.path.join("assets", "spaceship_red.png")) # Red spaceship
RED_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(RED_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 270) # Rotating the image

class Spaceship:
    """Represents a spaceship"""

    VEL = 5
    BULLET_VEL = 7
    MAX_BULLETS = 4
    SPACESHIP_MAX_HEALTH = 10

    def __init__(self, x, y, color, id):
        self.x = x
        self.y = y
        self.color = color
        self.id = id
        self.health = self.SPACESHIP_MAX_HEALTH
        self.set_width()
    
    def draw(self, canvas):
        """Draws the spaceship on the canvas"""

        if self.color == YELLOW:
            self.rect = canvas.blit(YELLOW_SPACESHIP, (self.x, self.y))
        else:
            self.rect = canvas.blit(RED_SPACESHIP, (self.x, self.y))
    
    def set_width(self):
        """Sets the max and min width coordinates that the spaceship can move to"""

        match self.id:
            case "0":
                self.max_width = WIN_WIDTH // 2
                self.min_width = 0
            case "1":
                self.max_width = WIN_WIDTH
                self.min_width = WIN_WIDTH // 2

    def handle_movement(self, keys_pressed):
        """Handles the movement of the spaceship"""

        if keys_pressed[pygame.K_LEFT] and self.x - self.VEL > self.min_width:
            self.x -= self.VEL
        if keys_pressed[pygame.K_RIGHT] and self.x + self.VEL + SPACESHIP_WIDTH < self.max_width:
            self.x += self.VEL
        if keys_pressed[pygame.K_UP] and self.y - self.VEL > 0:
            self.y -= self.VEL
        if keys_pressed[pygame.K_DOWN] and self.y + self.VEL + SPACESHIP_HEIGHT < WIN_HEIGHT:
            self.y += self.VEL

class Bullet:
    """Represents a bullet"""

    BULLET_WIDTH, BULLET_HEIGHT = 10, 5

    def __init__(self, x, y, color):
        self.color = color
        self.repr = pygame.Rect(
                    x,                 # Right edge of the yellow spaceship
                    y,                 # Middle of the yellow spaceship height
                    self.BULLET_WIDTH, # Width of the bullet
                    self.BULLET_HEIGHT # Height of the bullet
                    )

class Game:
    """Represents the game"""

    def __init__(self) -> None:
        self.net = Network() # Initialize the network
        self.canvas = Canvas() # Initialize the game window
        self.player, self.enemy = self.get_players()

    def handle_bullets(self):
        """Displays the bullets of the player and the enemy"""

        for bullet in self.player.bullets:
            if bullet.color == YELLOW:
                bullet.repr.x += self.player.BULLET_VEL
            else: bullet.repr.x -= self.player.BULLET_VEL
            if self.enemy.rect.colliderect(bullet.repr):
                pygame.event.post(pygame.event.Event(ENEMY_HIT))
                self.player.bullets.remove(bullet)
            elif bullet.repr.x < 0 or bullet.repr.x > WIN_WIDTH:
                self.player.bullets.remove(bullet)
        
        for bullet in self.enemy.bullets:
            if bullet.color == RED:
                bullet.repr.x -= self.enemy.BULLET_VEL
            else: bullet.repr.x += self.enemy.BULLET_VEL
            if self.player.rect.colliderect(bullet.repr):
                pygame.event.post(pygame.event.Event(PLAYER_HIT))
                self.enemy.bullets.remove(bullet)
            elif bullet.repr.x < 0 or bullet.repr.x > WIN_WIDTH:
                self.enemy.bullets.remove(bullet)
        

    def get_players(self):
        """Assigns the player and enemy based on the network id"""

        if self.net.id == "0":
            return Spaceship(100, 300, YELLOW, "0"), Spaceship(700, 300, RED, "1")
        elif self.net.id == "1":
            return Spaceship(700, 300, RED, "1"), Spaceship(100, 300, YELLOW, "0")

    def run(self):
        """Game loop"""

        FPS = 30
        clock = pygame.time.Clock()
        self.player.bullets, self.enemy.bullets = [], []

        run = True
        while run:
            clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                if event.type == PLAYER_HIT:
                    self.player.health -= 1
                    BULLET_HIT_SOUND.play()
                """
                if event.type == ENEMY_HIT: # Need to add this event
                    self.enemy.health -= 1
                    BULLET_HIT_SOUND.play()
                """

            keys_pressed = pygame.key.get_pressed()
            if keys_pressed[pygame.K_SPACE] and len(self.player.bullets) < 4:
                BULLET_FIRE_SOUND.play()
                self.player.bullets.append(Bullet(self.player.x, self.player.y + SPACESHIP_HEIGHT // 2, self.player.color))
            self.player.handle_movement(keys_pressed)
            self.handle_bullets()
            self.canvas.draw_window(self.player, self.enemy)
            self.send_data()

            result_text = ""
            if self.player.health <= 0:
                result_text = WINNER_FONT.render("You Lost!", 1, RED)
            
            if self.enemy.health <= 0:
                result_text = WINNER_FONT.render("You Won!", 1, GREEN)
            
            if result_text != "":
                self.canvas.draw_winner(result_text)
                break
    
    def send_data(self):
        """
        Send position, health and bullets of player to server
        Return position, health and bullets of opponent
        """

        data = f"{self.net.id};{self.player.x}:{self.player.y};{self.player.health};{self.bullets_to_str()}"
        self.update_data(self.net.send(data))

    def bullets_to_str(self):
        """Converts a bullet list to a formatted string"""

        if len(self.player.bullets) == 0:
            return ""
        if len(self.player.bullets) == 1:
            return f"{self.player.bullets[0].repr.x}:{self.player.bullets[0].repr.y}"
        res = ""
        res += f"{self.player.bullets[0].repr.x}:{self.player.bullets[1].repr.y}"
        for bullet in self.player.bullets[1:]:
            res += f"#{bullet.repr.x}:{bullet.repr.y}"
        return res

    def list_to_bullets(self, list):
        """Converts a list of coordinates tuples to a list of bullets"""

        res = []
        for x, y in list:
            res.append(Bullet(x, y, self.enemy.color))
        return res

    def split_bullets(self, bullet_str):
        """Converts a formatted string to a list of coordinates tuples"""

        bullet_str = bullet_str.split("#")
        bullet_str = [bullet_str[i].split(":") for i in range(len(bullet_str))]
        for index, i in enumerate(bullet_str):
            bullet_str[index] = list(map(int, bullet_str[index]))
        return bullet_str

    def update_data(self, data):
        """Updates enemy data"""

        elem = data.split(";") # separating data
        try:
            elem[1] = elem[1].split(":") # formatting position
            self.enemy.x, self.enemy.y = int(elem[1][0]), int(elem[1][1]) # updating position
            self.enemy.health = int(elem[2]) # updating health
        except ValueError:
            return
        if len(elem[3]) > 0:
            #print(elem)
            #print(elem[3])
            self.enemy.bullets = self.list_to_bullets(self.split_bullets(elem[3]))
        else:
            self.enemy.bullets = []

class Canvas:
    """Represents the canvas of the game"""

    NAME = "Spaceship Online"

    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    
    def draw_winner(self, text):
        """Displays the result text on the screen"""

        self.screen.blit(text, (
            WIN_WIDTH // 2 - text.get_width() // 2,
            WIN_HEIGHT // 2 - text.get_height() // 2
            )
        )
        pygame.display.update()
        pygame.time.delay(5000)

    def draw_hp(self, player, enemy):
        """
        Displays the health of the player and the enemy
        """

        player_health_text = HEALTH_FONT.render(f"Your Health: {player.health}", 1, WHITE)
        enemy_health_text = HEALTH_FONT.render(f"Opponent Health: {enemy.health}", 1, WHITE)
        if player.color == YELLOW:
            self.screen.blit(player_health_text, (10, 10))
            self.screen.blit(enemy_health_text, (WIN_WIDTH - enemy_health_text.get_width() - 10, 10))
        elif player.color == RED:
            self.screen.blit(enemy_health_text, (10, 10))
            self.screen.blit(player_health_text, (WIN_WIDTH - enemy_health_text.get_width() - 10, 10))
    
    def draw_window(self, player, enemy):
        """
        Renders the game onto the screen
        """

        self.screen.blit(SPACE, (0, 0))
        pygame.draw.rect(self.screen, "BLACK", BORDER)
        player.draw(self.screen)
        enemy.draw(self.screen)
        self.draw_hp(player, enemy)
        for bullet in player.bullets:
            pygame.draw.rect(self.screen, player.color, bullet.repr)
        for bullet in enemy.bullets:
            pygame.draw.rect(self.screen, enemy.color, bullet.repr)
        pygame.display.update()