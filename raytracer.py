import numpy as np
import vectormath as vm
from vectormath import Vector3
import math
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
			return (False, 0, 0)

		# Compute both possible solutions of the ray-sphere intersection
		a = (np.dot(-ray.direction, ray_offset) + sqrt(discriminant)) / ray_dir_dot
		b = (np.dot(-ray.direction, ray_offset) - sqrt(discriminant)) / ray_dir_dot

		t = 0
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
		closest_sphere = None
		closest_t = None
		closest_normal = None
		for sphere in self.spheres:
			hit, t, normal = sphere.hit(ray, t0, t1)
			if hit:
				any_hit = True
				closest_sphere = sphere
				closest_t = t
				closest_normal = normal

		return (any_hit, closest_sphere, closest_t, closest_normal)

class Ray():
	def __init__(self, start, direction):
		self.start = start
		self.direction = direction

MAX_CALL_DEPTH = 16
def raycolor_recursive(scene, ray, t0, t1, depth, do_reflect):
	hit1, sphere, t, normal = scene.hit_anything(ray, t0, t1)
	if not hit1:
		return scene.background

	# Initialize color with just the diffuse and ambient terms
	# This accounts for "ambient light" - light that just happens to be everywhere
	# The idea is an approximation for a full global illumination solution
	mat = sphere.material
	color = mat.diffuse * mat.ambient
	# Use the parameter t to get the actual point of intersection
	p = ray.start + ray.direction * t
	# N is the normal vector for the ray bounce
	N = normal.normalize()
	# D is the incoming direction vector
	D = ray.direction.normalize()
	# R is the reflection vector
	R = D - 2.0 * np.dot(D, N) * N

	# Now we compute the effect of each light on this point
	for light in scene.lights:
		# We get the direction vector towards the light
		light_dir = light.position - p
		distance = light_dir.length
		L = light_dir.normalize()
		# We need to cast a new ray to check if this point is shadowed
		# A point is in a shadow if another object is between it and the light
		# We discard the other return values because we don't care about them
		hit2, _, _, _ = scene.hit_anything(Ray(p, light_dir), .001, math.inf)
		if not hit2:
			# No shadow, so lets compute the effect of the light on this point
			# H is the "half vector"
			H = L + (-ray.direction).normalize()
			H = H.normalize()
			# Compute the diffuse color
			diffuse = mat.diffuse * light.color * np.clip(np.dot(N, L), 0.0, 1.0)
			# Now the specular highlights
			specular = light.color * mat.specular * pow(np.dot(H, N), mat.phong_power)
			# Accumulate these into color
			color += diffuse + specular
			color = np.clip(color, 0.0, 1.0)

	if do_reflect and depth < MAX_CALL_DEPTH and (mat.reflective is not None) and mat.reflective.any():
		ref_color = mat.reflective * raycolor_recursive(scene, Ray(p, R), .01, math.inf, depth+1, do_reflect)
		color += ref_color
		color = np.clip(color, 0.0, 1.0)

	return color

def raycolor(scene, ray, do_reflect):
	return raycolor_recursive(scene, ray, 0.0, math.inf, 0, do_reflect)


def render(scene, do_reflect=False):
	width = 512
	height = 512
	img = np.zeros(shape=(width, height, 3), dtype=np.float32)

	# for i in range(width):
	# 	for j in range(height):
	# 		img[j][i] = scene.background

	# Camera basis vectors
	# W grows out of the screen, so its the opposite of the gaze direction
	W = (scene.camera.position - scene.camera.look_at).normalize()
	# V grows towards the top of the screen
	V = scene.camera.up.normalize()
	# U grows to the right
	U = scene.camera.right.normalize()

	# Define screen-space bound values
	left = -1
	right = 1
	top = 1 
	bottom = -1;

	for i in range(width):
		for j in range(height):
			# Rays are cast through "target points" on a plane that sits in front of the camera.
			# Each point represents a specific pixel on screen.
			# Here we define each coordinate of each point in terms of camera space.
			# Since the W basis grows out of the screen, the w coordinate is always -1.
			# The plane is 1 unit along the gaze direction, which is opposite the W basis.
			ws = -1.0
			# The U and V coordinates are determined by how far along the pixel is along the
			# screen's width and height, respectively. We add .5 to center the point within the pixel.
			# Bigger i values are closer to the right of the screen
			us = ((i + 0.5) / width) * (right - left) + left
			# Bigger j values are closer to the bottom of the screen
			vs = ((j + 0.5) / height) * (bottom - top) + top

			# We now construct the direction of the ray using these coordinates.
			# Each coordinate is multiplied by its associated basis vector.
			# This gives us freedom to define any location for the camera in world-space.
			target = us * U + vs * V + ws * W
			direction = target - scene.camera.position

			# A ray starts at the camera and goes in the direction of the target 
			ray = Ray(scene.camera.position, direction)
			# hit, sphere, t, normal = scene.hit_anything(ray, 0.0, math.inf)
			# if hit:
			# 	img[j][i] = sphere.material.diffuse
			img[j][i] = raycolor(scene, ray, do_reflect)


	return img