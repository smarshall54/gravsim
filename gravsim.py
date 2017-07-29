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
      #main game window parameters
      self.ftick = 60
      self.winsizex = 1280
      self.winsizey = 720
      self.paused = False
      # set up pygame object
      self.pg = pygame
      self.pg.init()
      self.screen = self.pg.display.set_mode((self.winsizex, self.winsizey))
      # set up game objects
      self.gameSpace = space(self.pg)
      self.creator = creator(self.pg)

   def toggle_pause(self):
      self.paused = not self.paused
      if self.paused:   print("Paused")
      else: print("Unpaused")

   def gameLoop(self):
      running = True
      # gameticks
      clock = self.pg.time.Clock() 
      try:      
         while running:
            # GAME TICKS / FPS
            ###################
            clock.tick(self.ftick)
            
            # UPDATE GAME
            ######################            
            if not self.paused:
               self.gameSpace.updatePositions(self.ftick)
               self.gameSpace.updateVels(self.ftick)

            # INPUT/EVENT HANDLING
            #######################
            self.handleInputs()
            
            # RENDER
            #################
            self.drawAll()
            
      finally:
         pygame.quit()
         
   def drawAll(self):
      # space draws entities
      # really should be, get render data from space and draw it
      self.gameSpace.drawFrame()
      # define menu area for creator status
      self.pg.draw.rect(self.gameSpace.screen, (96,96,96), self.pg.Rect(0,self.gameSpace.height,self.gameSpace.length,40))
      # take render data from Creator and draw that
      self.creator.drawGenBar()
      twidth = 10
      for t in self.creator.textitems:
         self.gameSpace.screen.blit(t,(twidth,self.gameSpace.height))
         twidth+=(10+t.get_width())
      
      self.pg.display.flip()

   def handleInputs(self):
      """
      checks for user input and manages the event stack
      """
      pressed = self.pg.key.get_pressed()     
      # Change CREATOR parameters
      if pressed[self.pg.K_UP]:     self.creator.update_vel(1,0.05)
      if pressed[self.pg.K_DOWN]:   self.creator.update_vel(1,-0.05)
      if pressed[self.pg.K_LEFT]:   self.creator.update_vel(0,-0.05)
      if pressed[self.pg.K_RIGHT]:  self.creator.update_vel(0,0.05)
      if pressed[self.pg.K_w]:      self.creator.update_mass(1)
      if pressed[self.pg.K_s]:      self.creator.update_mass(1)
      if pressed[self.pg.K_f]:      self.creator.reset_params()
      
      # Manage Event Stack
      for event in pygame.event.get():
         if event.type == pygame.QUIT:    self.pg.quit()
         if event.type == self.pg.KEYDOWN:
            if event.key == self.pg.K_ESCAPE:   self.pg.quit()
            if event.key == self.pg.K_c:  self.gameSpace.clearBodies()
            if event.key == self.pg.K_r:  self.gameSpace.reportBodies()
            if event.key == self.pg.K_p:  self.toggle_pause()
            if event.key == self.pg.K_e:  self.creator.toggle_mobile()
         # on Lclick, add a body to the space
         if event.type==pygame.MOUSEBUTTONDOWN: 
            if event.button==1:
               mouseloc = self.pg.mouse.get_pos()
               ## CALL CREATOR CLASS for createBody()
               self.gameSpace.addBody(self.creator.mass, self.creator.vel.copy(), [mouseloc[0],mouseloc[1]],self.creator.mobile)
               print('mouse clicked at',mouseloc)

class creator(game):
   def __init__(self,pg):
      # pygame object (shouldn't need once set up right)
      self.pg = pg
      # physical constants
      self.vel = [0,0]
      self.veladd = [0,0]
      self.mass = 1
      self.mobile = True
      # render data
      self.textitems = () # creator settings text to render
   
   def update_vel(self,ind,incr):
         self.veladd[ind]+=incr
         self.veladd[ind]%=2
         self.vel[ind] = round(1-self.veladd[ind],2)
   def update_mass(self,incr):
      self.mass = (round(self.mass + incr)%99)+1
   def toggle_mobile(self):
      self.mobile = not self.mobile
   def reset_params(self):
      self.mass = 1
      self.vel = [0,0]
   
   def drawGenBar(self):
      font = self.pg.font.Font(None,28)
      text = font.render("Velocity: "+str(self.vel), True, (128,0,0))
      text2 = font.render("Mass: "+str(self.mass),True,(128,0,0))
      text3 = font.render("Mobile:"+str(self.mobile),True,(128,0,0))
      self.textitems = (text,text2,text3)
      
   
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
      #game.__init__(self)
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
         loc = body.newPosition(self.tick,self.length, self.height)
         if (loc[0]**2+loc[1]**2)**0.5 > 20000:
            self.bodies.remove(body)
            print('removed body - too far away')
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

               
               # div by 0 catch since no collision
               if (dely<=1 and dely>0) or (dely>=-1 and dely<=0):
                  dely = 1
               if (delx<=1 and delx>0) or (delx>=-1 and delx<=0):
                  delx = 1
               F[0] += Ftot*(delx/(r2**0.5))
               F[1] += Ftot*(dely/(r2**0.5))
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
   def clearBodies(self):
      self.bodies = []

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
      
      if self.mobile: # only update position and trail if the point is mobile
         self.trail.append(self.location.copy())
         if len(self.trail)>self.trail_max:
            self.trail.pop(0)
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
      return self.location
      
      
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