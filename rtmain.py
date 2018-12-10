# Library imports
import argparse
import numpy as np
import vectormath as vm
from vectormath import Vector3
from pprint import pprint
from PIL import Image
import time

# Project imports
import raytracer as rt

m1 = rt.Material(
		diffuse=Vector3(0.7, 0.2, 0.5),
		ambient=Vector3(0.3, 0.3, 0.3),
		specular=Vector3(0.85, 0.85, 0.85),
		reflective=Vector3(0.5, 0.2, 0.1),
		phong_power=200
		)

m2 = rt.Material(
		diffuse=Vector3(0.5, 0.7, 0.4),
		ambient=Vector3(0.3, 0.3, 0.3),
		specular=Vector3(0.55, 0.55, 0.55),
		reflective=Vector3(0.1, 0.3, 0.2),
		phong_power=32
		)

m3 = rt.Material(
		diffuse=Vector3(0.1, 0.3, 0.7),
		ambient=Vector3(0.3, 0.3, 0.3),
		specular=Vector3(0.75, 0.75, 0.75),
		reflective=Vector3(0.1, 0.2, 0.4),
		phong_power=148
		)

m4 = rt.Material(
		diffuse=Vector3(0.4, 0.1, 0.6),
		ambient=Vector3(0.3, 0.3, 0.3),
		specular=Vector3(0.95, 0.95, 0.95),
		reflective=Vector3(0.1, 0.1, 0.1),
		phong_power=256
		)

m5 = rt.Material(
		diffuse=Vector3(0.2, 0.2, 0.2),
		ambient=Vector3(0.3, 0.3, 0.3),
		specular=Vector3(0.95, 0.95, 0.95),
		reflective=Vector3(0.9, 0.9, 0.9),
		phong_power=512
		)

def default_camera():
	return rt.Camera(position=Vector3(0., 0., 6.),
		look_at=Vector3(0., 0., 0.),
		up=Vector3(0.0, 1.0, 0.0),
		right=Vector3(1.0, 0.0, 0.0))

def simplest_scene():
	cam = default_camera()
	lights = [rt.Light(cam.position, Vector3(.9, .9, .9))]
	spheres = [rt.Sphere(Vector3(0.0, 0.0, 0.0), .5, m1)]

	return rt.Scene(cam, lights, spheres, background=Vector3(0.3, 0.3, 0.3))

def example_scene():
	cam = default_camera()

	lights = [
		rt.Light(Vector3(3, 1, 3), Vector3(0.7, 0.7, 0.7)),
		rt.Light(cam.position, Vector3(0.1, 0.1, 0.1)),
		rt.Light(Vector3(0, 4, 0), Vector3(0.6, 0.0, 0.1)),
	]

	spheres = [
		rt.Sphere(Vector3(-.3, 0.0, -1.0), .3, m1),
		rt.Sphere(Vector3(.3, 0.0, -1.0), .3, m2),
		rt.Sphere(Vector3(.4, .5, .2), .1, m3),
		rt.Sphere(Vector3(.5, 0.0, -.5), .2, m4),
		#rt.Sphere(Vector3(0., 0., -5.), .7, m5),
	]

	return rt.Scene(cam, lights, spheres, background=Vector3(0.3, 0.3, 0.3))

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--out', default='example.png', help='Output file name')
	parser.add_argument('--reflect', action='store_true', help='Will compute reflections if passed')
	args = parser.parse_args()
	scene = example_scene()
	#scene = simplest_scene()
	render_start = time.perf_counter()
	img_data = rt.render(scene, do_reflect=args.reflect)
	render_end = time.perf_counter()
	print('Rendering time: {}s'.format(render_end - render_start))
	#print(img_data)
	img_start = time.perf_counter()
	img = Image.fromarray(np.uint8(img_data*255))
	img.save(args.out)
	img_end = time.perf_counter()
	print('Image conversion/saving time: {}s'.format(img_end - img_start))

if __name__ == '__main__':
	main()