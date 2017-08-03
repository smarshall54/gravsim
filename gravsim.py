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
#     e. find a way to get better trails - maybe don't store and render them all every frame.
# 			could just draw them to a separate surface and blit that every frame? etc
#
# 9. GAMEPLAY FEATURES
#     a. MOUSE-DRAG LAUNCHING w. predictor trail
#     b. predictor trail does not know future movements - just predicts an accel path based on current positions of bodies
#     c. mass/density sliders
#     d. collision
#     e. better behavior for close bodies (shootoff bug)
#     f. undo function (remove last body from list of bodies)
#     g. SAVE feature to allow user to save a cool configuration
#
#  SCOPE CREEP
#     - sandbox mode and puzzle mode
#     - sandbox is just sandbox sim
#           - puzzle mode has pre-built space "levels" with certain bodies
#              already instantiated; you would have to accomplish some goal - 
#              such as shoot your body thru a maze of gravity wells, or rescue
#              some orbiting body before its orbit decays by placing new bodies
#              to alter the gravitational field
#
##############################################################################
##############################################################################
class game(object):
   """
   contains data about the game session
   """
   def __init__(self):
      #main game window parameters
      self.ftick = 600
      self.winsizex = 1280
      self.winsizey = 720
      self.paused = False
      # set up pygame object
      self.pg = pygame
      self.pg.init()
      # screen panels --> eventually give to Window class
      self.simWidth = 1080
      self.simHeight = 620
      self.screen = self.pg.display.set_mode((self.winsizex, self.winsizey))
      self.debugPanel = Panel((self.winsizex-200,self.winsizey-720),200,720)
      self.creatorPanel = Panel((0,self.winsizey-100),self.winsizex-200,100)
      self.simPanel = Panel((0,0),self.simWidth,self.simHeight)
      # set up game objects
      self.gameSpace = space(self.pg,self.screen,self.simWidth,self.simHeight)
      self.creator = creator(self.pg)
      self.mousedown = [0,0]
      self.mouseup = [0,0]

   def toggle_pause(self):
      self.paused = not self.paused
      if self.paused:   print("Paused")
      else: 			   print("Unpaused")
   ##############################################
   ##############################################
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
               self.gameSpace.solve2Bodies(self.ftick)

            # INPUT/EVENT HANDLING
            #######################
            self.handleInputs()
            
            # RENDER
            #################
            self.drawAll()
            
      finally:
         pygame.quit()
   ##############################################
   ##############################################         
   def drawAll(self):

      drawers = {
      'circle':self.pg.draw.circle
      ,'lines':self.pg.draw.lines
      ,'line':self.pg.draw.line
      }
      
      self.screen.fill((0,0,0)) 
      # space draws entities
      # really should be, get render data from space and draw it

      # get call methods for objects to create their drawing data this tick
      simSurfaces = self.gameSpace.drawFrame() #should be a panel!
      self.debugPanel.drawPanel()
      self.creator.drawGenBar()
      # create creatorPanel's properties...
      self.creatorPanel.set_contents(self.creator.textitems)
      self.creatorPanel.init_fields(1,len(self.creator.textitems))
      self.creatorPanel.drawPanel()

      # blit/draw various objects back onto the main window surface
      self.screen.blit(self.debugPanel.panelSurf,self.debugPanel.position)
      self.screen.blit(self.creatorPanel.panelSurf,self.creatorPanel.position)
      for d in simSurfaces:
         for key in d:
            if 'circle' in key:
               self.pg.draw.circle(self.screen, d[key][0], d[key][1],d[key][2])
            if 'lines' in key:
               self.pg.draw.lines(self.screen, d[key][0], d[key][1],d[key][2])
            if 'line' in key and not 's' in key:
               self.pg.draw.line(self.screen, d[key][0], d[key][1],d[key][2])

      # flip the screen buffer
      self.pg.display.flip()

   ##############################################
   ##############################################
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
            if event.key == self.pg.K_q:  self.gameSpace.removeBody()
            if event.key == self.pg.K_p:  self.toggle_pause()
            if event.key == self.pg.K_e:  self.creator.toggle_mobile()
            if event.key == self.pg.K_a:  self.creator.update_order(-1)
            if event.key == self.pg.K_d:  self.creator.update_order(1)
         # on Lclick, add a body to the space
         if event.type==pygame.MOUSEBUTTONDOWN: 
            if event.button==1:
               mouseloc = self.pg.mouse.get_pos()
               ## CALL CREATOR CLASS for createBody()
               #self.gameSpace.addBody(self.creator.mass, self.creator.vel.copy(), [mouseloc[0],mouseloc[1]],self.creator.mobile)
               self.mousedown = mouseloc
               initvel = [0,0]
               initvel[0] = (self.mousedown[0] - self.mouseup[0])/100
               initvel[1] = (self.mousedown[1] - self.mouseup[1])/100
               b = body(self.creator.mass, int(5+self.creator.mass//50), initvel.copy(), [self.mousedown[0],self.mousedown[1]])
               self.gameSpace.body_creation_buffer = b
         if event.type==pygame.MOUSEBUTTONUP:
            self.gameSpace.dumpBuffer()
            #self.gameSpace.addBody(self.creator.mass, initvel.copy(), [self.mousedown[0],self.mousedown[1]])
      if pygame.mouse.get_pressed()[0]:# and event.button==1:
         self.mouseup = self.pg.mouse.get_pos()
         initvel = [0,0]
         initvel[0] = (self.mousedown[0] - self.mouseup[0])/100
         initvel[1] = (self.mousedown[1] - self.mouseup[1])/100
         #b = body(self.creator.mass, int(5+self.creator.mass//50), initvel.copy(), [self.mousedown[0],self.mousedown[1]])
         self.gameSpace.body_creation_buffer.vel = initvel.copy()
         self.gameSpace.body_creation_buffer.calcLaunchVect()
##############################################################################
##############################################################################
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
   ##############################################
   ##############################################
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
   ##############################################
   ##############################################
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
##############################################################################
##############################################################################
class Window(game):
   """
   class that contains info about the game window - handles placement
   of sim grid, menus, etc. basically keeps track of the screen layout.
   """
   def __init__(self):
      self.winsizex = winsizex
      self.winsizey = winsizey
      self.panels = []

##############################################################################
##############################################################################
class Panel(game):
   def __init__(self, position, width, height):
      self.position = position   # tuple of upper left corner coords (x,y)
      self.width = width         # width in pixels
      self.height = height       # height in pixels
      self.fields = []
      self.color = (48,48,48)
      self.contents = [] # list containing items to go in the menu
         # possible drawing items: some are pygame objects, some are custom
         # font
         # rect
         # circle
         # line
         # lines
         # sliderbars
         # toggleswitches
      self.panelSurf = pygame.Surface((self.width,self.height))

   def set_contents(self,contents):
      self.contents = contents

   def init_fields(self,nrows,ncols):
      fieldheight = self.height//nrows
      fieldwidth = self.width//ncols
      for i in range(0,ncols):
         for j in range(0,nrows):
            self.fields.append([i*fieldwidth,j*fieldheight])

   def drawPanel(self):
      self.panelSurf.fill(self.color)
      for ind,item in enumerate(self.contents):
         try:
            self.panelSurf.blit(item,self.fields[ind])
         except:
            print('content too long for panel fields')
##############################################################################
##############################################################################
class space(game):
   """
   space represents the entire area of space being
   simulated. this object contains all existing
   bodies in the space, as well as parameters defining
   the space itself; such as size, boundaries etc.
   """
   def __init__(self, pg, screen, width, height):

      self.grid = 1           #sets space granularity to 1 pixel
      self.tick = 1           #sets time granularity to 1x the game loop tick
      self.pg = pg
      #self.screen = screen #not sure how to get this via inheritance
      #print("space inherits",self.screen)
      self.width = width    # valid render area
      self.height = height    # valid render area
      self.gravconst = 100
      self.bodies = []
      self.body_creation_buffer = False
      
   def addBody(self, mass, vel=[0,0], location=[0,0],mobile=True):
      """
      adds a body to the space
      """
      # gotta fix this function too, needs to get data from Creator
      newBody = body(mass,int(5+mass//50),vel,location,mobile) # radius ~ mass//5
      self.bodies.append(newBody)

   def removeBody(self):
      '''
      removes the most recently created body
      '''
      self.bodies.pop()

   def dumpBuffer(self):
      self.body_creation_buffer.launchvect = [0,0]
      self.body_creation_buffer.launchend = self.body_creation_buffer.location.copy()
      self.bodies.append(self.body_creation_buffer)
      self.body_creation_buffer = False

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
      
      if self.body_creation_buffer!=False:
         drawlist.append(self.body_creation_buffer.getDrawData())
         print('drawing buffered body')
      return drawlist
   ##############################################
   ##############################################
   def solve2Bodies(self,tick):
      # F/m = a
      # F = gm1m2/r2
      # v = a*dt
      for body in self.bodies:
         eps=10
         Force = [0,0]
         body.set_force(Force) # reset force for the current tick
         for otherbody in self.bodies:
            if otherbody!=body:
               delx = otherbody.location[0] - body.location[0]
               dely = otherbody.location[1] - body.location[1]
               r2 = (delx**2+dely**2)
               Ftot = self.gravconst*body.mass*otherbody.mass*r2**0.5/(r2+eps**2)**(3/2)
               # div by 0 catch since no collision
               # if (dely<=1 and dely>0):   dely = 1
               # if (dely>=-1 and dely<=0): dely = -1
               # if (delx<=1 and delx>0):   delx = 1
               # if (delx>=-1 and delx<=0): delx = -1
               Force[0] = Ftot*(delx/(r2**0.5))
               Force[1] = Ftot*(dely/(r2**0.5))
               body.addForce(Force)
               body.updateVel(tick)
             
   ##############################################
   ##############################################
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
##############################################################################
##############################################################################
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
      self.trail_max = 1000
      self.velend = location.copy()
      self.force = [0,0] #used to store force acting on the object in current tck
      self.forceend = location.copy()
      self.mobile = mobile # is the mass fixed or mobile?
      self.launchvect = [0,0]
      self.launchend = self.location.copy()
      
   def get_vel(self):
      return self.vel
   
   def set_vel(self,vel):
      self.vel = vel
   
   def set_force(self,force):
      self.force = force

   def addForce(self,Force):
      self.force[0] += Force[0]
      self.force[1] += Force[1] 

   def updateVel(self,tick):
      self.vel[0] += (self.force[0]/self.mass)/tick 
      self.vel[1] += (self.force[1]/self.mass)/tick
   ##############################################
   ##############################################
   def newPosition(self,tick):
      # keep location as float, only round when rendering      
      #self.updateTrail()
      if self.mobile:
         # calculate the new position
         self.location[0] += self.vel[0]/tick 
         self.location[1] += self.vel[1]/tick
      #self.calcDispVectors()
      return self.location

   def updateTrail(self):
      if self.mobile: # only update position and trail if the point is mobile
         # put last location onto the trail
         self.trail.append(self.location.copy())
      if len(self.trail)>self.trail_max:
         self.trail.pop(0)

   def calcDispVectors(self):
      self.updateTrail()
      # calculate the velocity and force vectors for display
      velvect = [0,0]
      velvect[0] = 10*(self.location[0] - self.trail[-2][0])
      velvect[1] = 10*(self.location[1] - self.trail[-2][1])
      self.velend[0] = self.location[0]+velvect[0]
      self.velend[1] = self.location[1]+velvect[1]

      forcevect = [0,0]
      forcevect[0] = 10*(self.force[0])
      forcevect[1] = 10*(self.force[1])
      self.forceend[0] = self.location[0]+forcevect[0]
      self.forceend[1] = self.location[1]+forcevect[1]

   def predictPath(self):
      """
      returns a list of points which represents the predicted path assuming 
      all bodies remain in their current position.

      probably belongs in space class since it's a calculation on multiple 
         bodies. but body class will need a new newPosition function which
         does not overwrite its self.location value and instead returns just
         a list of coordinates.
      """
      pass

   def calcLaunchVect(self):
      self.launchend[0] = self.location[0]+pygame.mouse.get_pos()[0]
      self.launchend[1] = self.location[1]+pygame.mouse.get_pos()[1]
      pass
   ##############################################
   ##############################################
   def getDrawData(self):
      """
      returns a dict containing tuples of the arguments to be passed
      to various pygame.draw methods, such as pygame.draw.circle, .lines,
      .line, etc. The tuple can be unpacked as the arguments in the main 
      rendering method, which is the only class that knows what Screen to 
      draw to.
      """
      #Define Colors
      bodycolor = (32,255,64)
      trailcolor = (64,64,64)
      velvectcolor = (255,0,0)
      forcevectcolor = (0,0,255)
      launchvectcolor = (0,64,0)
      
      #calculate vectors to draw
      self.calcDispVectors()
      rendCoords = (round(self.location[0]),round(self.location[1]))
      
      # passes up arguments needed for the renderer, as well as
      #     the type of object to draw.
      drawdata = {'circle':(bodycolor,rendCoords,self.rad),
                  'lines':(trailcolor,False,self.trail),
                  'line0':(velvectcolor,self.location,self.velend),
                  'line1':(forcevectcolor,self.location,self.forceend),
                  'line2':(launchvectcolor,self.location,self.launchend)}
      return drawdata

##############################################################################
##############################################################################
def main(): # consider main() like unit test code
            # could write a generalized gameloop class
            #  gameloop(tick, gameData, updateMethod, renderMethod,
            #           handleInputsMethod)
            # basically a generalized format for real-time physics-based
            # 2d games
            # Game(object)
            #     System(Game) = data about the system its running on;
            #                    in my simple example this is just window size
            #                    but in a full program it might have to know
            #                    about system commands for file saving etc.
            #     States(Game) = data listing all available Game States
            #              e.g. Main Menu, Game, Credits
            #     Panel(Game) = data about screen layout in a given Game State
            #     Inputs(Game) = class defining input relationships from
            #                    events to methods on the game
            #     Render(Game) = render method to grab data about the game
            #                    relevant methods and plot it
            #        rest of the game would be a custom class (in my case, 
            #        "space" is the hook for the main gameplay part)
            # build a basic 3d engine to take mouse input and translate
            #  into FPS vision movement.  
   print('Starting gravSim')
   activeGame = game()
   activeGame.gameLoop()


if __name__ == '__main__':
   main()