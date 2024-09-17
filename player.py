from math import copysign
from pygame.math import Vector2
from pygame.locals import KEYDOWN, KEYUP, K_LEFT, K_RIGHT
from pygame.sprite import collide_rect
from pygame.event import Event
import random
import pygame
from sprite import Sprite
from level import Level
import settings as config

# Return the sign of a number: getsign(-5)-> -1
getsign = lambda x: copysign(1, x)


class Player(Sprite):
    """
    A class to represent the player.

    Manages player's input, physics (movement...).
    Can be accessed via Singleton: Player.instance.
    (Check Singleton design pattern for more info).
    """

    def __init__(self, brain, *args):
        Sprite.__init__(self, *args)
                    
        self.__startrect = self.rect.copy()
        self.__maxvelocity = Vector2(config.PLAYER_MAX_SPEED, 100)
        self.__startspeed = 1.5

        self._velocity = Vector2()
        self._input = 0
        self._jumpforce = config.PLAYER_JUMPFORCE
        self._bonus_jumpforce = config.PLAYER_BONUS_JUMPFORCE

        self.gravity = config.GRAVITY
        self.accel = .5
        self.deccel = .6
        self.dead = False
        self.jumping = False

        self.brain = brain
        self.fitness = 0

    def clone(self):
        cloneBrain = self.brain.clone()
        clone = Player(cloneBrain, config.HALF_XWIN - config.PLAYER_SIZE[0] / 2,
                                config.HALF_YWIN + config.HALF_YWIN / 2,
                                *config.PLAYER_SIZE,
                                config.PLAYER_COLOR)
        return clone

    def _fix_velocity(self) -> None:
        """ Set player's velocity between max/min.
        Should be called in Player.update().
        """
        self._velocity.y = min(self._velocity.y, self.__maxvelocity.y)
        self._velocity.y = round(max(self._velocity.y, -self.__maxvelocity.y), 2)
        self._velocity.x = min(self._velocity.x, self.__maxvelocity.x)
        self._velocity.x = round(max(self._velocity.x, -self.__maxvelocity.x), 2)

    def reset(self) -> None:
        " Called only when game restarts (after player death)."
        self._velocity = Vector2()
        self.rect = self.__startrect.copy()
        self.camera_rect = self.__startrect.copy()
        self.dead = False

    def get_platform_above(self, platforms):
        for platform in platforms:
            if self.rect.y < platform.rect.y:
                    return platform.rect.x
                
    def get_platform_below(self, platforms):
        max_x = None
        for platform in platforms:
            if self.rect.y > platform.rect.y:
                    max_x = platform.rect.x
        return max_x
    
        # Ai Part
    def think(self, platforms):
        coordinatesUp = self.get_platform_above(platforms)
        coordinatesDown = self.get_platform_below(platforms)
        inputs = []
        vision = self.look(platforms)
        
        inputs.append(vision[1])
        inputs.append(vision[2])
        inputs.append(vision[3])

        #inputs.append(self.x/600)                  
        inputs.append(coordinatesUp - self.rect.x / 600 if coordinatesUp is not None else 0)
        inputs.append(coordinatesDown - self.rect.x / 600 if coordinatesDown is not None else 0)
        
        output = self.brain.feedForward(inputs).tolist()     

        index = output.index(max(output))
        return index

    def ai_movement(self, decision):
        if (decision == 0):
            if self._velocity.x < 10:
                self._velocity.x += 1
                self.direction = 0
        elif (decision == 1):
            if self._velocity.x > -10:
                self._velocity.x -= 1
            self.direction = 1
        elif (decision == 2):
            if self._velocity.x > 0:
                self._velocity.x -= 1
            elif self._velocity.x < 0:
                self._velocity.x += 1

        self.rect.x += self._velocity.x

    def look(self, platforms):
        vision = [0, 0, 0, 0]

        for p in platforms:
            rect = pygame.Rect(p.rect.x , p.rect.y, p.rect.width, p.rect.height)
            
            up = pygame.Rect(self.rect.x + 50, self.rect.y, 1, 800)
            down = pygame.Rect(self.rect.x + 50, self.rect.y - 800, 1, 800)
            left = pygame.Rect(self.rect.x-600, self.rect.y + 50, 600, 1)
            right = pygame.Rect(self.rect.x, self.rect.y + 50, 600, 1)

            if (rect.colliderect(up)):
                vision[0] = 1
                #print("******up*******")

            if (rect.colliderect(down)):
                vision[1] = 1
                #print("******down*******")

            if (rect.colliderect(left)):
                vision[2] = 1
                #print("******left*******")

            if (rect.colliderect(right)):
                vision[3] = 1
                #print("******right*******")

        return vision



    def move_left(self):
        self._velocity.x = -self.__startspeed
        self._input = -1

    def move_right(self):
        self._velocity.x = self.__startspeed
        self._input = 1

    def handle_event(self, event: Event) -> None:
        """ Called in main loop for each user input event.
        :param event pygame.Event: user input event
        """
        if event.type == KEYDOWN:
            if event.key == K_LEFT:
                self.move_left()
            elif event.key == K_RIGHT:
                self.move_right()
        elif event.type == KEYUP:
            if (event.key == K_LEFT and self._input == -1) or (
                    event.key == K_RIGHT and self._input == 1):
                self._input = 0

    def jump(self, force: float = None) -> None:
        if not force:
            force = self._jumpforce
        self._velocity.y = -force
        self.jumping = True

    def onCollide(self, obj: Sprite) -> None:
        self.rect.bottom = obj.rect.top
        self.jump()
        self.jumping = False

    def collisions(self) -> None:
        """ Checks for collisions with level.
        Should be called in Player.update().
        """
        lvl = Level.instance
        if not lvl:
            return
        for platform in lvl.platforms:
            if self._velocity.y > .5:
                if platform.bonus and collide_rect(self, platform.bonus):
                    self.onCollide(platform.bonus)
                    self.jump(platform.bonus.force)
                if collide_rect(self, platform):
                    self.onCollide(platform)
                    platform.onCollide()

    def update(self) -> None:
        """ For position and velocity updates.
        Should be called each frame.
        """
        if self.camera_rect.y > config.YWIN * 2:
            self.dead = True
            return
        self._velocity.y += self.gravity
        if self._input:
            self._velocity.x += self._input * self.accel
        elif self._velocity.x:
            self._velocity.x -= getsign(self._velocity.x) * self.deccel
            self._velocity.x = round(self._velocity.x)
        self._fix_velocity()

        self.rect.x = (self.rect.x + self._velocity.x) % (config.XWIN - self.rect.width)
        self.rect.y += self._velocity.y

        self.collisions()

    def random_action(self):
        """Simulate a random action."""
        action = random.choice(['left', 'right', 'stop'])
        if action == 'left':
            self.move_left()
        elif action == 'right':
            self.move_right()
