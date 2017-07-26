import pygame
import numpy as np

class game(object):
	"""
	contains data about the game session
	"""
	def __init__(self):
		self.ftick = 60

	def gameLoop(self):
		

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
		self.grid = 1 			#sets space granularity to 1 pixel
		self.tick = 1			#sets time granularity to 1x the game loop tick

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
		pass

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


if __name__ == '__main__':
    main()