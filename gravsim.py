import pygame
import numpy as np

#  TODO:
# X   1. infinite plane instead of modulo space
# 2. functionalize game loop
# 3. convert to vector math using numpy
#     a. better algo for force solving! (quadratic now - could use
#        a matrix operation for much faster results
# 4. fix object inheritance
# 5. UI around edge of screen
# 6. DEBUG FEATURES:
# X    a. PAUSE (able to report during pause)
# P    b. toggle accel/vel vector drawing
# X    c. reset veladd/mass vectors to 0
#     d. debug screen overlay
#           - cycle thru bodies and show instantaneous vel/accel/pos of each
#           - display game tick number %10000 so user can see how much time since last pause
#           - calculate vector deltas since last pause
# 7. graphical effects
#     a. add grid
#     b. add toggle for particle trails
#     c. make radius proportional to mass
#     d. toggle for color change on velocity
# 8. EFFICIENCY
#     a. only draw objects that are on screen
#     b. re=code using numpy for vector math
#     c. decouple game ticks and FPS - render as fast as possible (with bound t1)
#           but only tick game once every t2
#     d. reduce processor usage - probably related to gametick implementation.
#           this small game should not use a full core unless there are many bodies.
#           figure out why and stop it.


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
      self.paused = False
      self.mobile = True # CREATOR param

   def gameLoop(self):
      running = True
      # gameticks
      clock = self.pg.time.Clock()
      
      
      # should create a "body creator" function which has these...)
      vel = [0,0] # initial velocity adder for new bodies
      veladd = [0,0]
      mass = 1      
      creator_settings = [vel, veladd, mass]

      
      try:      
         while running:
            clock.tick(self.ftick)
            # inputs
            
            creator_settings = self.handleInputs(creator_settings)
            vel = creator_settings[0]
            mass = creator_settings[2]
            
            # screen rendering
               # draw stuff
            
            # render bodies
            self.gameSpace.drawFrame()

            # CREATOR Info
            font = self.pg.font.Font(None,32)
            text = font.render("Velocity: "+str(vel), True, (128,0,0))
            text2 = font.render("Mass: "+str(mass),True,(128,0,0))
            text3 = font.render("Mobile:"+str(self.mobile),True,(128,0,0))
            self.gameSpace.screen.blit(text,(10,10))
            self.gameSpace.screen.blit(text2,(10+text.get_width(),10))
            self.gameSpace.screen.blit(text3,(10+text.get_width()+10+text2.get_width(),10))
            # flip the buffer
            self.pg.display.flip()
            
            
            if not self.paused:
               self.gameSpace.updatePositions(self.ftick)
               self.gameSpace.updateVels(self.ftick)
      finally:
         pygame.quit()
         
   def handleInputs(self,creator_settings):
      """
      function which polls the keyboard for keys pressed and checks the event stack
      
      performs functions based on what keys are pressed.
      
      in the future, should reference a keybinding which maps keys to functions
      actions should also become separate functions
      """
      pressed = self.pg.key.get_pressed()
      up_key = pressed[self.pg.K_UP]
      down_key = pressed[self.pg.K_DOWN]
      left_key = pressed[self.pg.K_LEFT]
      right_key = pressed[self.pg.K_RIGHT]
      w_key = pressed[self.pg.K_w]
      s_key = pressed[self.pg.K_s] # these variables are kind of redundant
                                    # since self.pg.K_w is pretty self-documenting
      dirkeys = (up_key, down_key, left_key, right_key)
      
      vel = creator_settings[0]
      veladd = creator_settings[1]
      mass = creator_settings[2]
      
      
      # CREATOR: increase/decrease initial velocity
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
      
      # CREATOR: increase/decrease mass
      if w_key:
         mass = (round(mass + 1)%99)+1
         print('increasing mass to',mass)
      if s_key:
         if mass==1:
            mass = round(mass - 2)%100 # for some reason this doesnt work when %99+1
         mass = round(mass - 1)%100                              # it just doesnt change the mass value
         print('reducing mass to',mass)
         if mass==0:
            mass = 1
      if pressed[self.pg.K_e]:
         self.mobile = not self.mobile
         
      # CREATOR: RESET creator settings
      if pressed[self.pg.K_f]:
         mass = 1
         vel = [0,0]
         
      # PHYSICS SIM PAUSE
      if pressed[self.pg.K_p]:
         #this makes it obvious that key rate polling needs to be decreased,
         # or "debouncing" or something
         self.paused = True
         print('paused')
      if pressed[self.pg.K_o]:
         self.paused = False
         print('unpaused')
         
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
               ## CALL CREATOR CLASS for createBody()
               self.gameSpace.addBody(mass, vel.copy(), [mouseloc[0],mouseloc[1]],self.mobile)
               print('mouse clicked at',mouseloc)
               
      creator_settings = [vel, veladd, mass]
      return creator_settings

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
      self.gravconst = 100

      self.bodies = []

   def addBody(self, mass, vel=[0,0], location=[0,0],mobile=True):
      """
      adds a body to the space
      """
      newBody = body(mass,5+mass//5,vel,location,mobile) # radius ~ mass//5
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
         drawlist = body.draw(self.pg,self.screen)   # could definitely fix all this
         for d in drawlist:                          # parameter passing with proper
            d                        # object inheritance.
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
               delx = otherbody.location[0] - body.location[0]
               dely = otherbody.location[1] - body.location[1]
               r2 = (delx**2+dely**2)
               Ftot = self.gravconst*body.mass*otherbody.mass/r2
               Fx = Ftot*(delx/(r2**0.5))
               Fy = Ftot*(dely/(r2**0.5))
               
               #print(delx,dely)
               # must determine sign because the information is lost 
               # by the r^2 part of the gravity equation.
               if delx<0:  signx = -1
               else: signx = 1
                  
               if dely<0: signy = -1
               else: signy = 1

               # meant to be a divide by 0 catch but somethings very
               # wrong here
               if (dely<=0.1 and dely>0) or (dely>=-0.1 and dely<=0):
                  dely = 0.1
               if (delx<=0.1 and delx>0) or (delx>=-0.1 and delx<=0):
                  delx = 0.1
               
               #print(delx,dely)
                  
               F[0] += Fx#signx * self.gravconst * body.mass * otherbody.mass / delx**2
               F[1] += Fy#signy * self.gravconst * body.mass * otherbody.mass / dely**2
               accel[0] = F[0]/body.mass
               accel[1] = F[1]/body.mass
         v2[0] = v2[0] + accel[0]/tick
         v2[1] = v2[1] + accel[1]/tick
         body.set_vel(v2)
         body.set_force(F)
         # could do a body.set_accel / set_force here to give the body its
         # own force data for drawing overlays.
               

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
         print(body.force, "force")
         #print(body.trail,"trail")

class body(game):
   """
   a body can be any distinct unit of mass present in space. currently treated 
   as a point mass. a body can have scalar properties:   mass   radius
   and vector properties:  velocity   location
   """
   def __init__(self, mass=1, rad=5, vel=[0,0], location=[0,0], mobile=True):
      self.mass = mass
      self.rad = rad
      self.vel = vel
      self.location = location
      self.trail = [location.copy(),location.copy()]
      self.trail_max = 100
      self.velend = location.copy()
      self.force = [0,0] #used to store force acting on the object in current tck
      self.forceend = location.copy()
      self.mobile = mobile # is the mass fixed or mobile?
      
   def get_vel(self):
      return self.vel
   
   def set_vel(self,vel):
      self.vel = vel
   
   def set_force(self,force):
      self.force = force

   def newPosition(self,tick,length,height):
      # keep location as float, only round when rendering
      
      # put last location onto the trail
      self.trail.append(self.location.copy())
      if len(self.trail)>self.trail_max:
         self.trail.pop(0)
      
      if self.mobile:
         # calculate the new position
         self.location[0] += self.vel[0]*2/tick 
         self.location[1] += self.vel[1]*2/tick
      
      # calculate the velocity vector for display
      velvect = [0,0]
      velvect[0] = 10*(self.location[0] - self.trail[-1][0])
      velvect[1] = 10*(self.location[1] - self.trail[-1][1])
      self.velend[0] = self.location[0]+velvect[0]
      self.velend[1] = self.location[1]+velvect[1]
      # should really make these force vectors instead, but the data for
      # force/accel isn't stored in the body object...
      forcevect = [0,0]
      forcevect[0] = 10*(self.force[0])
      forcevect[1] = 10*(self.force[1])
      self.forceend[0] = self.location[0]+forcevect[0]
      self.forceend[1] = self.location[1]+forcevect[1]
      
      
   def draw(self,pg,screen): #fix parameter passing with proper object inheritance
      rendCoords = (round(self.location[0]),round(self.location[1]))

      
      me = [pg.draw.circle(screen, (32, 255, 64), rendCoords,self.rad),
            pg.draw.lines(screen, (64,64,64), False, self.trail),
            pg.draw.line(screen, (255, 0, 0),self.location,self.velend),
            pg.draw.line(screen, (0, 0, 255), self.location, self.forceend)]
      return me
      

def main():
   print('Starting gravSim')
   activeGame = game()
   activeGame.gameLoop()


if __name__ == '__main__':
   main()