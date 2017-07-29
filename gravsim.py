import pygame
import numpy as np

#  TODO
# 1. Move all physics update logic to body() objects instead of space
#     space object should only be used for counting bodies and holding data
#        about space, like grid, color, size etc.
# 3. convert to vector math using numpy
#     a. better algo for force solving! (quadratic now - could use
#        a matrix operation for much faster results
# P 4. fix object inheritance
#        really should decide how to do rendering, whether to pass screens around...
# P 5. UI around edge of screen
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
#	  e. find a way to get better trails - maybe don't store and render them all every frame.
# 			could just draw them to a separate surface and blit that every frame? etc
#
# 9. GAMEPLAY FEATURES
# 	  a. MOUSE-DRAG LAUNCHING w. predictor trail
#	  b. predictor trail does not know future movements - just predicts an accel path based on current positions of bodies
#	  c. mass/density sliders
# 	  d. collision
#     e. better behavior for close bodies

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
      self.gameSpace = space(self.pg,self.screen)
      self.creator = creator(self.pg)

   def toggle_pause(self):
      self.paused = not self.paused
      if self.paused:   print("Paused")
      else: 			print("Unpaused")

   def gameLoop(self):
      
      #DEBUG TEST: a=inherit()
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
      
      self.screen.fill((0,0,0)) 
      # space draws entities
      # really should be, get render data from space and draw it
      for d in self.gameSpace.drawFrame():
         for key in d:
            if key=='body':
               self.pg.draw.circle(self.screen, d[key][0], d[key][1],d[key][2])
            if key=='trail':
               self.pg.draw.lines(self.screen, d[key][0], d[key][1],d[key][2])
            if key=='velvect':
               self.pg.draw.line(self.screen, d[key][0], d[key][1],d[key][2])
            if key=='forcevect':
               self.pg.draw.line(self.screen, d[key][0], d[key][1],d[key][2])
      # define menu area for creator status
      self.pg.draw.rect(self.screen, (96,96,96), self.pg.Rect(0,self.winsizey-50,self.winsizex,40))
      # take render data from Creator and draw that
      self.creator.drawGenBar()
      twidth = 10
      for t in self.creator.textitems:
         self.screen.blit(t,(twidth,self.winsizey-50))
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
      if pressed[self.pg.K_s]:      self.creator.update_mass(-1)
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
            if event.key == self.pg.K_a:  self.creator.update_order(-1)
            if event.key == self.pg.K_d:  self.creator.update_order(1)
         # on Lclick, add a body to the space
         if event.type==pygame.MOUSEBUTTONDOWN: 
            if event.button==1:
               mouseloc = self.pg.mouse.get_pos()
               ## CALL CREATOR CLASS for createBody()
               self.gameSpace.addBody(self.creator.mass, self.creator.vel.copy(), [mouseloc[0],mouseloc[1]],self.creator.mobile)
               print('mouse clicked at',mouseloc)
class inherit(game):
   def __init__(self):
      game.__init__(self)
      print(self.screen)
class creator(game):
   def __init__(self,pg):
      # pygame object (shouldn't need once set up right)
      self.pg = pg
      # physical constants
      self.vel = [0,0]
      self.veladd = [0,0]
      self.mass = 1
      self.order = 1
      self.mobile = True
      # render data
      self.textitems = () # creator settings text to render
   
   def update_vel(self,ind,incr):
         self.veladd[ind]+=incr
         self.veladd[ind]%=2
         self.vel[ind] = round(1-self.veladd[ind],2)
   def update_mass(self,incr):
      self.mass = (round(self.mass + incr)%(99*10**self.order)+1*10**self.order)
   def update_order(self,incr):
      self.order += incr
   def toggle_mobile(self):
      self.mobile = not self.mobile
   def reset_params(self):
      self.mass = 1
      self.vel = [0,0]
   
   def drawGenBar(self):
      """
      generates text renders and other graphical objects to be passed
      up to the main render method for drawing to the screen.
      """
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
   def __init__(self, pg, screen):

      self.grid = 1           #sets space granularity to 1 pixel
      self.tick = 1           #sets time granularity to 1x the game loop tick
      self.pg = pg
      self.screen = screen #not sure how to get this via inheritance
      print("space inherits",self.screen)
      self.width = self.screen.get_width()    # valid render area
      self.height = self.screen.get_height()    # valid render area
      self.gravconst = 100
      self.bodies = []
      
   def addBody(self, mass, vel=[0,0], location=[0,0],mobile=True):
      """
      adds a body to the space
      """
      # gotta fix this function too, needs to get data from Creator
      newBody = body(mass,int(5+mass//50),vel,location,mobile) # radius ~ mass//5
      self.bodies.append(newBody)

   def updatePositions(self,tick):
      """
      calculate new positions for the next frame
      """
      for body in self.bodies:
         loc = body.newPosition(self.tick)
         if (loc[0]**2+loc[1]**2)**0.5 > 20000:
            self.bodies.remove(body)
            print('removed body - too far away')
   def drawFrame(self):
      """
      goes through self.bodies and gets drawing data for each body
      """
      drawlist = []
      for body in self.bodies:
         drawlist.append(body.getDrawData())   # could definitely fix all this
      return drawlist

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
               if (dely<=1 and dely>0):   dely = 1
               if (dely>=-1 and dely<=0): dely = -1
               if (delx<=1 and delx>0):   delx = 1
               if (delx>=-1 and delx<=0): delx = -1
               F[0] += Ftot*(delx/(r2**0.5))
               F[1] += Ftot*(dely/(r2**0.5))
               accel[0] = F[0]/body.mass
               accel[1] = F[1]/body.mass
         v2[0] = v2[0] + accel[0]/tick
         v2[1] = v2[1] + accel[1]/tick
         body.set_vel(v2)
         body.set_force(F)               

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

   def newPosition(self,tick):
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
      
      
   def getDrawData(self): #fix parameter passing with proper object inheritance
      """
      returns a dict containing tuples of the arguments to be passed
      to various pygame.draw methods, such as pygame.draw.circle, .lines, .line
      The tuple can be unpacked as the arguments in the main rendering method,
      which is the only class that knows what Screen to draw to.
      """
      bodycolor = (32,255,64)
      trailcolor = (64,64,64)
      velvectcolor = (255,0,0)
      forcevectcolor = (0,0,255)
   
      rendCoords = (round(self.location[0]),round(self.location[1]))
      print(rendCoords,self.rad)
      drawdata = {'body':(bodycolor,rendCoords,self.rad),
                  'trail':(trailcolor,False,self.trail),
                  'velvect':(velvectcolor,self.location,self.velend),
                  'forcevect':(forcevectcolor,self.location,self.forceend)}
      #not sure how to get rid of direct draw calls here without just piping ALL of the 
      # data back up. but it works.
      return drawdata
      
def main():
   print('Starting gravSim')
   activeGame = game()
   activeGame.gameLoop()


if __name__ == '__main__':
   main()