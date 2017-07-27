import pygame
import numpy as np

class game(object):
   """
   contains data about the game session
   """
   def __init__(self):
      self.ftick = 60
      self.pg = pygame
      self.gameSpace = space(self.pg)
      self.winsizex = 1280
      self.winsizey = 720
      self.pg.init()

   def gameLoop(self):
      done = False
      # gameticks
      clock = self.pg.time.Clock()
      # initial position:
      x=30
      y=30
      vel = [0,0] # initial velocity adder for new bodies
      veladd = [0,0]
      try:      
         while not done:
            clock.tick(self.ftick)
            # inputs
            pressed = self.pg.key.get_pressed()
            up_key = pressed[self.pg.K_UP]
            down_key = pressed[self.pg.K_DOWN]
            left_key = pressed[self.pg.K_LEFT]
            right_key = pressed[self.pg.K_RIGHT]
            
            if up_key: 
               veladd[0]+=0.05 
               veladd[0]%=20
               vel[0] = round(veladd[0]-10,2)
               print(dirkeys)
            if down_key: 
               veladd[0]-=0.05 
               veladd[0]%=20
               vel[0] = round(veladd[0]-10,2)
               print(dirkeys)
            if left_key: 
               veladd[1]-=0.05 
               veladd[1]%=20
               vel[1] = round(veladd[1]-10,2)
               print(dirkeys)
            if right_key: 
               veladd[1]+=0.05 
               veladd[1]%=20
               vel[1] = round(veladd[1]-10,2)
               print(dirkeys)
            
            dirkeys = (up_key, down_key, left_key, right_key)
            
            for event in pygame.event.get():
               if event.type == pygame.QUIT:
                  done = True
                  self.pg.quit()
                  break
               if event.type == self.pg.KEYDOWN and event.key == self.pg.K_ESCAPE:
                  done = True
                  self.pg.quit()
                  break
               
               if event.type == self.pg.KEYDOWN and event.key == self.pg.K_c:
                  self.gameSpace.bodies = []
               if event.type == self.pg.KEYDOWN and event.key == self.pg.K_r:
                  self.gameSpace.reportBodies()
               # on Lclick, add a body to the space
               if event.type==pygame.MOUSEBUTTONDOWN: 
                  if event.button==1:
                     mouseloc = self.pg.mouse.get_pos()
                     self.gameSpace.addBody(vel.copy(), [mouseloc[0],mouseloc[1]])

            # wrap the screen
            y = y%self.gameSpace.height
            x = x%self.gameSpace.length
            
            # screen rendering
               # draw stuff
            font = self.pg.font.Font(None,32)
            text = font.render("Velocity: "+str(vel), True, (128,0,0))
            
            self.gameSpace.drawFrame()
            self.gameSpace.screen.blit(text,(10,10))
            # flip the buffer
            self.pg.display.flip()
            
            self.gameSpace.updatePositions(self.ftick)
      finally:
         pygame.quit()

class space(game):
   """
   space represents the entire area of space being
   simulated. this object contains all existing
   bodies in the space, as well as parameters defining
   the space itself; such as size, boundaries etc.
   """
   def __init__(self, pg, length=800, height=600, wrap=True):
      self.length = length
      self.height = height
      self.wrap = wrap
      self.grid = 1          #sets space granularity to 1 pixel
      self.tick = 1         #sets time granularity to 1x the game loop tick
      self.pg = pg
      self.screen = pg.display.set_mode((self.length+50, self.height+50))

      self.bodies = []

   def addBody(self, vel=[0,0], location=[0,0]):
      """
      adds a body to the space
      """
      newBody = body(1,5,vel,location)
      self.bodies.append(newBody)

   def updatePositions(self,tick):
      """
      calculate new positions for the next frame
      """
      for body in self.bodies:
         body.newPosition(self.tick,self.length, self.height)

   def drawFrame(self):
      """
      draws the space for the next frame
      """
      # erase previous screen
         ### THIS REFERENCE IS BROKE, HACKED TOGETHER
         ### HOW TO DO PROPER OO REFERENCING OF PARENT CLASS?
      self.screen.fill((0,0,0))  
      for body in self.bodies:
         body.draw(self.pg,self.screen)   # could definitely fix all this
                                       # parameter passing with proper
                                       # object inheritance.
                                       # space() and body() should inherit
                                       # pygame and screen objects from game()
                                       # object
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
   def reportBodies(self):
      print(len(self.bodies),"bodies exist")
      for body in self.bodies:
         print(body.vel,"velocity")
         print(body.location,"location")

class body(game):
   """
   a body can be any distinct unit of mass present in space. currently treated 
   as a point mass. a body can have scalar properties:   mass   radius
   and vector properties:  velocity   location
   """
   def __init__(self, mass=1, rad=5, vel=[0,0], location=[0,0]):
      self.mass = mass
      self.rad = rad
      self.vel = vel
      self.location = location

   def newPosition(self,tick,length,height):
      self.location[0] += round(self.vel[0]*2/tick)
      self.location[1] += round(self.vel[1]*2/tick)
      self.location[0] %= length
      self.location[1] %= height
      
   def draw(self,pg,screen): #fix parameter passing with proper object inheritance
      me = pg.draw.circle(screen, (32, 255, 64), (self.location[0],self.location[1]),self.rad)
      return me
      

def main():
   print('Starting gravSim')
   activeGame = game()
   activeGame.gameLoop()


if __name__ == '__main__':
   main()