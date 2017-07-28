import pygame
import numpy as np

#  TODO:
# 1. infinite plane instead of modulo space
# 2. functionalize game loop
# 3. convert to vector math using numpy
#     a. better algo for force solving! (quadratic now) 
# 4. fix object inheritance
# 5. UI around edge of screen
# 6. fix position and velocity updates to maintain precision;
#     only round() on the render
#
#
#


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
      mass = 1
      try:      
         while not done:
            clock.tick(self.ftick)
            # inputs
            pressed = self.pg.key.get_pressed()
            up_key = pressed[self.pg.K_UP]
            down_key = pressed[self.pg.K_DOWN]
            left_key = pressed[self.pg.K_LEFT]
            right_key = pressed[self.pg.K_RIGHT]
            w_key = pressed[self.pg.K_w]
            s_key = pressed[self.pg.K_s]
            
            if up_key: 
               veladd[1]+=0.05 
               veladd[1]%=20
               vel[1] = round(10-veladd[1],2)
               print(dirkeys)
            if down_key: 
               veladd[1]-=0.05 
               veladd[1]%=20
               vel[1] = round(10-veladd[1],2)
               print(dirkeys)
            if left_key: 
               veladd[0]-=0.05 
               veladd[0]%=20
               vel[0] = round(10-veladd[0],2)
               print(dirkeys)
            if right_key: 
               veladd[0]+=0.05 
               veladd[0]%=20
               vel[0] = round(10-veladd[0],2)
               print(dirkeys)
            
            dirkeys = (up_key, down_key, left_key, right_key)
            
            if w_key:
               mass += 0.05
               mass %= 100
            if s_key:
               mass -= 0.05
               mass %= 100
               
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
                     self.gameSpace.addBody(mass, vel.copy(), [mouseloc[0],mouseloc[1]])
                     
            # wrap the screen
            y = y%self.gameSpace.height
            x = x%self.gameSpace.length
            
            # screen rendering
               # draw stuff
            font = self.pg.font.Font(None,32)
            text = font.render("Velocity: "+str(vel), True, (128,0,0))
            text2 = font.render("Mass: "+str(mass),True,(128,0,0))
            
            self.gameSpace.drawFrame()
            self.gameSpace.screen.blit(text,(10,10))
            self.gameSpace.screen.blit(text2,(10+text.get_width(),10))
            # flip the buffer
            self.pg.display.flip()
            
            self.gameSpace.updatePositions(self.ftick)
            self.gameSpace.updateVels(self.ftick)
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
      self.gravconst = 0.01

      self.bodies = []

   def addBody(self, mass, vel=[0,0], location=[0,0]):
      """
      adds a body to the space
      """
      newBody = body(mass,5,vel,location)
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
   def updateVels(self,tick):
      # F/m = a
      # F = gm1m2/r2
      # v = a*dt
      for body in self.bodies:
         v1 = body.get_vel()
         v2 = v1.copy()
         F = [0,0]
         accel = [0,0]
         for otherbody in self.bodies:
            if otherbody!=body:
               #edit this to handle modulo'd space
               delx = body.location[0] - otherbody.location[0]
               dely = body.location[1] - otherbody.location[1]
               # this still doesnt quite work; there is an edge effect
               # for proper sim, probably best NOT to wrap the world; 
               # it is enforcing a "spherical" space onto a cartesian plot
               # which is always going to have edge effects.
               # instead allow an infinite plane outside of the screen bounds
               # and only draw stuff that's on screen.
               r = (delx**2 + dely**2)**0.5
               
#               if delx<0:  signx = -1
#               else: signx = 1
#                  
#               if dely<0: signy = -1
#               else: signy = 1
               signx=1
               signy=1
               
               delx = min(abs(body.location[0] - otherbody.location[0]),
                          abs(otherbody.location[0]-body.location[0]))
               dely = min(abs(body.location[1] - otherbody.location[1]),
                          abs(otherbody.location[1]-body.location[1]))
               
               if dely**2<=0.01 or dely**2>=-0.01:
                  dely = 0.1
               if delx**2<=0.01 or delx**2>=-0.01:
                  delx = 0.1
                  
               F[0] = signx * self.gravconst * body.mass * otherbody.mass / delx**2
               F[1] = signy * self.gravconst * body.mass * otherbody.mass / dely**2
               accel[0] -= F[0]/body.mass
               accel[1] -= F[1]/body.mass
         v2[0] = v2[0] + accel[0]/tick
         v2[1] = v2[1] + accel[1]/tick
         body.set_vel(v2)
               

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
      
   def get_vel(self):
      return self.vel
   
   def set_vel(self,vel):
      self.vel = vel

   def newPosition(self,tick,length,height):
      # keep location as float, only round when rendering
      self.location[0] += self.vel[0]*2/tick 
      self.location[1] += self.vel[1]*2/tick 
      self.location[0] %= length
      self.location[1] %= height
      
   def draw(self,pg,screen): #fix parameter passing with proper object inheritance
      rendCoords = (round(self.location[0]),round(self.location[1]))
      me = pg.draw.circle(screen, (32, 255, 64), rendCoords,self.rad)
      return me
      

def main():
   print('Starting gravSim')
   activeGame = game()
   activeGame.gameLoop()


if __name__ == '__main__':
   main()