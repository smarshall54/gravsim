import pygame
import numpy as np

class game(object):
   """
   contains data about the game session
   """
   def __init__(self):
      self.ftick = 60

   def gameLoop(self):
      pygame.init()
      self.winsizex = 1280
      self.winsizey = 720
      self.ftick = 60
      screen = pygame.display.set_mode((self.winsizex, self.winsizey))
      done = False
         
      # gameticks
      clock = pygame.time.Clock()
      
      # initial position:
      x=30
      y=30
      
      while not done:
         clock.tick(self.ftick)
         yprev = y
         xprev = x
         for event in pygame.event.get():
            if event.type == pygame.QUIT:
               done = True
               pygame.quit()
               if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                  done = True
                  pygame.quit()
                  
         #input checking
         pressed = pygame.key.get_pressed()
         up_key = pressed[pygame.K_UP]
         down_key = pressed[pygame.K_DOWN]
         left_key = pressed[pygame.K_LEFT]
         right_key = pressed[pygame.K_RIGHT]
         if up_key: y-=3
         if down_key: y+=3
         if left_key: x-=3
         if right_key: x+=3
         
         # wrap the screen
         y = y%self.winsizey
         x = x%self.winsizex
         
         
         # screen rendering
         # do we need to draw stuff?
         if x!=xprev or y!=yprev:
            # erase previous screen
            screen.fill((0,0,0))  
            # draw stuff
            pygame.draw.rect(screen, (0, 128, 255), pygame.Rect(x, y, 60, 60))
            
         # flip the buffer
         pygame.display.flip()
         

class space(game):
   """
   space represents the entire area of space being
   simulated. this object contains all existing
   bodies in the space, as well as parameters defining
   the space itself; such as size, boundaries etc.
   """
   def __init__(self, length=800, width=600, wrap=True):
      self.length = length
      self.width = width
      self.wrap = wrap
      self.grid = 1          #sets space granularity to 1 pixel
      self.tick = 1         #sets time granularity to 1x the game loop tick

      self.bodies = []

   def addBody(self,location=[0,0]):
      """
      adds a body to the space
      """
      newBody = body()
      self.bodies.append(newBody)

   def updatePositions():
      """
      calculate new positions for the next frame
      """
      for body in self.bodies:
         body.newPosition()

   def drawFrame():
      """
      draws the space for the next frame
      """
      for body in self.bodies:
         body.draw()   
      pass

   def checkCollisions():
      """
      walks through self.bodies to see if any have the same coordinate
      """
      pass

   def resolveCollisions():
      """
      for each collision between bodies, resolves the momentum vectors
      for each body.
      """
      pass

class body(game):
   """
   a body can be any distinct unit of mass
   present in space. currently treated as 
   a point mass.

   a body can have scalar properties:
      mass
      radius
   and vector properties:
      velocity
      location
   """
   def __init__(self, mass=1, rad=5, vel=[0,0], location=[0,0]):
      self.mass = mass
      self.rad = rad
      self.vel = vel
      self.location = location

   def newPosition():
      self.location[0] += self.vel[0]*game.tick
      self.location[1] += self.vel[1]*game.tick


def main():
   print('Starting gravSim')
   activeGame = game()
   activeGame.gameLoop()


if __name__ == '__main__':
   main()