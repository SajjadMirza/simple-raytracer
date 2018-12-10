import numpy as np
import vectormath as vm
from vectormath import Vector3
from math import sqrt

class Material():
	def __init__(self, diffuse, ambient, specular, reflective, phong_power):
		self.diffuse = diffuse
		self.ambient = ambient
		self.specular = specular
		self.reflective = reflective
		self.phong_power = phong_power

class Sphere():
	def __init__(self, position, radius, material):
		self.position = position
		self.radius = radius
		self.material = material

	def hit(self, ray, t0, t1):
		ray_offset = ray.start - self.position
		ray_dir_dot = np.dot(ray.direction, ray.direction)
		ray_offset_dot = np.dot(ray_offset, ray_offset)
		r2 = self.radius * self.radius

		# Get the discriminant, which tells us whether we have a hit at all
		discriminant = pow(np.dot(ray.direction, ray_offset), 2) - ray_dir_dot * (ray_offset_dot - r2)
		if discriminant < 0:
			return (false, 0, 0)

		# Compute both possible solutions of the ray-sphere intersection
		a = (np.dot(-ray.direction, ray_offset) + sqrt(discriminant)) / ray_dir_dot
		b = (np.dot(-ray.direction, ray_offset) - sqrt(discriminant)) / ray_dir_dot

		t = None
		hit = False

		if t0 <= a <= t1 and t0 <= b <= t1:
			hit = True
			t = min(a, b)
		elif t0 <= a <= t1:
			hit = True
			t = a
		elif t0 <= b <= t1:
			hit = True
			t = b

		normal = 2.0 * ((ray.start + t * ray.direction) - self.position)
		return (hit, t, normal)

class Light():
	def __init__(self, position, color):
		self.position = position
		self.color = color

class Camera():
	def __init__(self, position, look_at, up, right):
		self.position = position
		self.look_at = look_at
		self.up = up
		self.right = right

class Scene():
	def __init__(self, camera, lights, spheres, background):
		self.camera = camera
		self.lights = lights
		self.spheres = spheres
		self.background = background

	def hit_anything(self, ray, t0, t1):
		any_hit = False
		
		for sphere in self.spheres:
			hit, t, normal = sphere.hit(ray, t0, t1)
			if hit:
				any_hit = True


class Ray():
	def __init__(self, start, direction):
		self.start = start
		self.direction = direction

def render(scene):
	width = 800
	height = 800

	img = np.zeros(shape=(width, height, 3), dtype=np.float32)

	print(type(img[20][32]))
	for i in range(width):
		for j in range(height):
			img[i][j] = scene.background

	# Camera basis vectors
	# W grows out of the screen, so its the opposite of the gaze direction
	W = (scene.camera.position - scene.camera.look_at).normalize()
	# V grows towards the top of the screen
	V = scene.camera.up.normalize()
	# U grows to the right
	U = scene.camera.right.normalize()

	for j in range(height):
		for i in range(width):
			# Rays are cast through "target points" on a plane that sits in front of the camera.
			# Each point represents a specific pixel on screen.
			# Here we define each coordinate of each point in terms of camera space.
			# Since the W basis grows out of the screen, the w coordinate is always -1.
			# The plane is 1 unit along the gaze direction, which is opposite the W basis.
			ws = -1
			# The U and V coordinates are determined by how far along the pixel is along the
			# screen's width and height, respectively. We add .5 to center the point within the pixel.
			us = (i + 0.5) / width
			vs = (j + 0.5) / height

			# We now construct the direction of the ray using these coordinates.
			# Each coordinate is multiplied by its associated basis vector.
			# This gives us freedom to define any location for the camera in world-space.
			target = us * U + vs * V + ws * W
			direction = target - scene.camera.position

			# A ray starts at the camera and goes in the direction of the target 
			ray = Ray(scene.camera.position, direction)
			img[i][j] = direction

	print((U, V, W))

	return img