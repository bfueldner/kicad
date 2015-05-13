#!/usr/bin/python
#
# Copyright (c) 2015 Benjamin Fueldner
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

# This script contains commons object definitions to generate kicad footprints

import time
import csv
import config
import math
cfg = config.Config("config")

class technology():
	smd = "smd"
	connector = "TBD"
	thru_hole = "thru_hole"
	non_plated = "TBD"

class type():
	circle = "circle"
	oval = "oval"
	rect = "rect"
	trapezoid = "trapezoid"

registered_footprints = {}

class metaclass_register(type):
	def __init__(cls, name, bases, nmspc):
		super(metaclass_register, cls).__init__(name, bases, nmspc)
		registered_footprints[name] = cls

#class class1(object):
#	__metaclass__ = metaclass_register
#
#	def foo(self):
#		print "foo"

class text():
	"""Generate text at x/y"""
	format = """  (fp_text %s %s (at %.3f %.3f) (layer %s)
	(effects (font (size %.3f %.3f) (thickness %.3f)))
  )\n"""

	def __init__(self, layer, name, value, x, y, size, thickness):
		self.layer = layer
		self.name = name
		self.value = value
		self.x = x
		self.y = y
		self.size = size
		self.thickness = thickness

	def render(self):
		return text.format%(self.name, self.value, self.x, self.y, self.layer, self.size, self.size, self.thickness)

class line():
	"""Generate line from x1/y1 to x2/y2"""
	format = "  (fp_line (start %.3f %.3f) (end %.3f %.3f) (layer %s) (width %.3f))\n"

	def __init__(self, layer, x1, y1, x2, y2, width):
		self.layer = layer
		self.x1 = x1
		self.y1 = y1
		self.x2 = x2
		self.y2 = y2
		self.width = width

	def render(self):
		return line.format%(self.x1, self.y1, self.x2, self.y2, self.layer, self.width)

class arc():
	"""Generate arc between x1/y1 and x2/y2 with given angle"""

	format = "  (fp_arc (start %.3f %.3f) (end %.3f %.3f) (angle %.3f) (layer %s) (width %.3f))\n"

	def __init__(self, layer, x1, y1, x2, y2, angle, width):
		self.layer = layer
		self.x1 = x1
		self.y1 = y1
		self.x2 = x2
		self.y2 = y2
		self.angle = angle
		self.width = width

	def render(self):
		return arc.format%(self.x1, self.y1, self.x2, self.y2, self.angle, self.layer, self.width)

class circle():
	"""Generate circle with center x1/y1 and radius through point x2/y2"""

	format = "  (fp_circle (center %.3f %.3f) (end %.3f %.3f) (layer %s) (width %.3f))\n"

	def __init__(self, layer, x1, y1, x2, y2, width):
		self.layer = layer
		self.x1 = x1
		self.y1 = y1
		self.x2 = x2
		self.y2 = y2
		self.width = width

	def render(self):
		return circle.format%(self.x1, self.y1, self.x2, self.y2, self.layer, self.width)

class rectangle():
	"""Generate rectangle on given layer"""

	def __init__(self, layer, x, y, width, height, line_width, centered = False):
		if centered:
			x -= width / 2
			y -= height / 2

		self.elements = []
		self.elements.append(line(layer, x, y, x + width, y, line_width))
		self.elements.append(line(layer, x + width, y, x + width, y + height, line_width))
		self.elements.append(line(layer, x + width, y + height, x, y + height, line_width))
		self.elements.append(line(layer, x, y + height, x, y, line_width))

	def render(self):
		result = ""
		for element in self.elements:
			result += element.render()
		return result

class beveled_rectangle():
	"""Rectangle with beveled edges"""

	def __init__(self, layer, x, y, width, height, bevel, line_width, centered = False):
		if centered:
			x -= width / 2
			y -= height / 2

		self.elements = []
		self.elements.append(line(layer, x + bevel, y, x + width - bevel, y, line_width))							# -
		self.elements.append(line(layer, x + width - bevel, y, x + width, y + bevel, line_width))					# \
		self.elements.append(line(layer, x + width, y + bevel, x + width, y + height - bevel, line_width))			# |
		self.elements.append(line(layer, x + width, y + height - bevel, x + width - bevel, y + height, line_width))	# /
		self.elements.append(line(layer, x + width - bevel, y + height, x + bevel, y + height, line_width))			# -
		self.elements.append(line(layer, x + bevel, y + height, x, y + height - bevel, line_width))					# \
		self.elements.append(line(layer, x, y + height - bevel, x, y + bevel, line_width))							# |
		self.elements.append(line(layer, x, y + bevel, x + bevel, y, line_width))									# /

	def render(self):
		result = ""
		for element in self.elements:
			result += element.render()
		return result

class beveled_outline():
	"""Outline with beveled corners every grid point"""

	def __init__(self, layer, x, y, width, height, bevel, grid, line_width, centered = False):
		if centered:
			x -= width / 2
			y -= height / 2

		self.elements = []

		x_rep = int(width / grid)
		y_rep = int(height / grid)
		for i in range(x_rep):
			if i != 0:
				self.elements.append(line(layer, i * grid + x, y + bevel, i * grid + x + bevel, y, line_width))
			self.elements.append(line(layer, i * grid + x + bevel, y, i * grid + x + grid - bevel, y, line_width))
			self.elements.append(line(layer, i * grid + x + grid - bevel, y, i * grid + x + grid, y + bevel, line_width))

		for i in range(y_rep):
			if i != 0:
				self.elements.append(line(layer, x + width - bevel, i * grid + y, x + width, i * grid + y + bevel, line_width))
			self.elements.append(line(layer, x + width, i * grid + y + bevel, x + width, i * grid + y + grid - bevel, line_width))
			self.elements.append(line(layer, x + width, i * grid + y + grid - bevel, x + width - bevel, i * grid + y + grid, line_width))

		for i in reversed(range(x_rep)):
			if i != (x_rep - 1):
				self.elements.append(line(layer, i * grid + x + grid, y + height - bevel, i * grid + x + grid - bevel, y + height, line_width))
			self.elements.append(line(layer, i * grid + x + grid - bevel, y + height, i * grid + x + bevel, y + height, line_width))
			self.elements.append(line(layer, i * grid + x + bevel, y + height, i * grid + x, y + height - bevel, line_width))

		for i in reversed(range(y_rep)):
			if i != (y_rep - 1):
				self.elements.append(line(layer, x + bevel, i * grid + y + grid, x, i * grid + y + grid - bevel, line_width))
			self.elements.append(line(layer, x, i * grid + y + grid - bevel, x, i * grid + y + bevel, line_width))
			self.elements.append(line(layer, x, i * grid + y + bevel, x + bevel, i * grid + y, line_width))

	def render(self):
		result = ""
		for element in self.elements:
			result += element.render()
		return result

class pad():
	"""Generate pad in x/y with size width/height in given technology/type"""

	format = "  (pad %s %s %s (at %.3f %.3f %.3f) (size %.3f %.3f) %s(layers %s))\n"
	format_drill = "(drill %.3f) "

	def __init__(self, layers, name, tech, type, x, y, width, height, drill = 0, angle = 0):
		self.layers = layers
		self.name = name
		self.tech = tech
		self.type = type
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		if drill:
			self.drill = pad.format_drill%(drill)
		else:
			self.drill = ""
		self.angle = angle

	def render(self):
		return pad.format%(self.name, self.tech, self.type, self.x, self.y, self.angle, self.width, self.height, self.drill, self.layers)

class footprint(object):
	__metaclass__ = metaclass_register

	def __init__(self, name, description = "", tags = "", smd = False, add_text = True):
		self.name = name
		self.description = description
		self.tags = tags
		self.smd = smd
		self.elements = []

		if add_text:
			self.elements.append(text(cfg.FOOTPRINT_REFERENCE_LAYER, "reference", "REF**", 0, 0, cfg.FOOTPRINT_REFERENCE_FONT_SIZE, cfg.FOOTPRINT_REFERENCE_FONT_THICKNESS))
			self.elements.append(text(cfg.FOOTPRINT_VALUE_LAYER, "value", "VAL**", 0, cfg.FOOTPRINT_VALUE_FONT_SIZE + 2 * cfg.FOOTPRINT_VALUE_FONT_THICKNESS, cfg.FOOTPRINT_VALUE_FONT_SIZE, cfg.FOOTPRINT_VALUE_FONT_THICKNESS))

	def add(self, element):
		self.elements.append(element)

	def remove(self, index):
		self.elements.remove(index)

	def render(self):
		result = '(module %s (tedit %.8X)\n'%(self.name, int(time.time()))
		if self.smd:
			result += '  (attr smd)\n'

		if len(self.description):
			result += '  (descr "'+self.description+'")\n'

		if len(self.tags):
			result += '  (tags "'+self.tags+'")\n'

		for element in self.elements:
			result += element.render()
		result += ')\n'
		return result

class wired(footprint):
	"""Generator for wired resistors, capacitors, ..."""

	def __init__(self, name, description, tags, package_width, package_height, pad_width, pad_height, pad_grid, pad_distance, count, drill):
		footprint.__init__(self, name, description, tags)

class wired_resistor(footprint):
	"""Wired resistor with beveled edges"""

	def __init__(self, name, description, tags, package_width, package_height, pad_diameter, pad_distance, pad_drill):
		footprint.__init__(self, name, description, tags)

		bevel = math.sqrt(package_width * package_width + package_height * package_height) * 0.1
		footprint.add(self, beveled_rectangle(cfg.FOOTPRINT_PACKAGE_LAYER, 0, 0, package_width, package_height, bevel, cfg.FOOTPRINT_PACKAGE_LINE_WIDTH, True))
		footprint.add(self, pad(cfg.FOOTPRINT_THD_LAYERS, 1, technology.thru_hole, type.circle, -pad_distance / 2, 0, pad_diameter, pad_diameter, pad_drill))
		footprint.add(self, pad(cfg.FOOTPRINT_THD_LAYERS, 2, technology.thru_hole, type.circle, pad_distance / 2, 0, pad_diameter, pad_diameter, pad_drill))

class dip(footprint):
	"""Generator for dual inline ICs"""

	def __init__(self, name, description, tags, package_width, package_height, pad_width, pad_height, pad_grid, pad_distance, pad_count, pad_drill):
		footprint.__init__(self, name, description, tags)

		if pad_count % 2:
			raise NameError("pad_count is odd")

		pin = 1
		x = pad_grid * -((float(pad_count) / 4) - 0.5)
		line_x = package_width / 2

		footprint.add(self, rectangle(cfg.FOOTPRINT_PACKAGE_LAYER, 0, 0, package_width, package_height, cfg.FOOTPRINT_PACKAGE_LINE_WIDTH, True))
		footprint.add(self, arc(cfg.FOOTPRINT_PACKAGE_LAYER, -line_x, 0, -line_x, 1.0, -180, cfg.FOOTPRINT_PACKAGE_LINE_WIDTH))
		for i in range(pad_count / 2):
			footprint.add(self, pad(cfg.FOOTPRINT_THD_LAYERS, pin, technology.thru_hole, type.oval, x, pad_distance / 2, pad_width, pad_height, pad_drill))
			x += pad_grid
			pin += 1

		for i in range(pad_count / 2, pad_count):
			x -= pad_grid
			footprint.add(self, pad(cfg.FOOTPRINT_THD_LAYERS, pin, technology.thru_hole, type.oval, x, -pad_distance / 2, pad_width, pad_height, pad_drill))
			pin += 1

class connector_grid_male(footprint):
	"""Generator wired connector lines (pins)"""

	def __init__(self, name, description, tags, package_width, package_height, pad_diameter, pad_grid, pad_drill, pin_count_x, pin_count_y):
		footprint.__init__(self, name, description, tags, False, False)

		bevel = pad_grid * 0.2
		footprint.add(self, text(cfg.FOOTPRINT_REFERENCE_LAYER, "reference", "REF**", 0, -(package_height + cfg.FOOTPRINT_REFERENCE_FONT_SIZE) / 2 - 2 * cfg.FOOTPRINT_REFERENCE_FONT_THICKNESS, cfg.FOOTPRINT_REFERENCE_FONT_SIZE, cfg.FOOTPRINT_REFERENCE_FONT_THICKNESS))
		footprint.add(self, text(cfg.FOOTPRINT_VALUE_LAYER, "value", "VAL**", 0, (package_height + cfg.FOOTPRINT_VALUE_FONT_SIZE) / 2 + 2 * cfg.FOOTPRINT_VALUE_FONT_THICKNESS, cfg.FOOTPRINT_VALUE_FONT_SIZE, cfg.FOOTPRINT_VALUE_FONT_THICKNESS))
		footprint.add(self, beveled_outline(cfg.FOOTPRINT_PACKAGE_LAYER, 0, 0, package_width, package_height, bevel, pad_grid, cfg.FOOTPRINT_PACKAGE_LINE_WIDTH, True))

		pin = 1
		y = pad_grid * -((float(pin_count_y) / 2) - 0.5)
		for i in range(pin_count_y):
			x = pad_grid * -((float(pin_count_x) / 2) - 0.5)
			for j in range(pin_count_x):
				if pin == 1:
					footprint.add(self, pad(cfg.FOOTPRINT_THD_LAYERS, pin, technology.thru_hole, type.rect, x, y, pad_diameter, pad_diameter, pad_drill))
				else:
					footprint.add(self, pad(cfg.FOOTPRINT_THD_LAYERS, pin, technology.thru_hole, type.circle, x, y, pad_diameter, pad_diameter, pad_drill))

				pin += 1
				x += pad_grid
			y += pad_grid

class connector_grid_female(footprint):
	"""Generator wired connector lines (plugs)"""

	def __init__(self, name, description, tags, package_width, package_height, pad_diameter, pad_grid, pad_drill, pin_count_x, pin_count_y):
		footprint.__init__(self, name, description, tags, False, False)

		bevel = pad_grid * 0.2
		footprint.add(self, text(cfg.FOOTPRINT_REFERENCE_LAYER, "reference", "REF**", 0, -(package_height + cfg.FOOTPRINT_REFERENCE_FONT_SIZE) / 2 - 2 * cfg.FOOTPRINT_REFERENCE_FONT_THICKNESS, cfg.FOOTPRINT_REFERENCE_FONT_SIZE, cfg.FOOTPRINT_REFERENCE_FONT_THICKNESS))
		footprint.add(self, text(cfg.FOOTPRINT_VALUE_LAYER, "value", "VAL**", 0, (package_height + cfg.FOOTPRINT_VALUE_FONT_SIZE) / 2 + 2 * cfg.FOOTPRINT_VALUE_FONT_THICKNESS, cfg.FOOTPRINT_VALUE_FONT_SIZE, cfg.FOOTPRINT_VALUE_FONT_THICKNESS))
		footprint.add(self, beveled_outline(cfg.FOOTPRINT_PACKAGE_LAYER, 0, 0, package_width, package_height, bevel, pad_grid, cfg.FOOTPRINT_PACKAGE_LINE_WIDTH, True))

		pin = 1
		y = pad_grid * -((float(pin_count_y) / 2) - 0.5)
		for i in range(pin_count_y):
			x = pad_grid * ((float(pin_count_x) / 2) - 0.5)
			for j in range(pin_count_x):
				if pin == 1:
					footprint.add(self, pad(cfg.FOOTPRINT_THD_LAYERS, pin, technology.thru_hole, type.rect, x, y, pad_diameter, pad_diameter, pad_drill))
				else:
					footprint.add(self, pad(cfg.FOOTPRINT_THD_LAYERS, pin, technology.thru_hole, type.circle, x, y, pad_diameter, pad_diameter, pad_drill))

				pin += 1
				x -= pad_grid
			y += pad_grid

class dsub(footprint):
	"""Generator for dsub connectors (this one will be tricky...)"""

	def __init__(self, name, description, tags, package_width, package_height, pad_width, pad_height, pad_grid, pad_distance, count_x, count_y, drill):
		footprint.__init__(self, name, description, tags)

class chip(footprint):
	"""Generator for chip resistors, capacitors, inductors, MELF and Tantal devices"""

	def __init__(self, name, description, tags, package_width, package_height, pad_width, pad_height):
		footprint.__init__(self, name, description, tags, True)
		self.package_width = package_width
		self.package_height = package_height
		self.pad_width = pad_width
		self.pad_height = pad_height
		footprint.add(self, rectangle(cfg.FOOTPRINT_PACKAGE_LAYER, 0, 0, package_width, package_height, cfg.FOOTPRINT_PACKAGE_LINE_WIDTH, True))

class chip_pol(chip):
	"""Generator for chip devices with polarity marker"""

	def __init__(self, name, description, tags, package_width, package_height, pad_width, pad_height):
		chip.__init__(self, name, description, tags, package_width, package_height, pad_width, pad_height)

		line_x = package_width / 2 + package_widht * 0.1
		line_y = package_height / 2
		footprint.add(self, line(cfg.FOOTPRINT_PACKAGE_LAYER, -line_x, -line_y, -line_x, line_y, cfg.FOOTPRINT_PACKAGE_LINE_WIDTH))

class soic(footprint):
	"""Generator for small outline ICs"""

	def __init__(self, name, description, tags, package_width, package_height, pad_width, pad_height, pad_grid, pad_distance, pad_count):
		footprint.__init__(self, name, description, tags, True)

		if pad_count % 2:
			raise NameError("pad_count is odd")

		pin = 1
		x = pad_grid * -((float(pad_count) / 4) - 0.5)
		line_x = package_width / 2
		line_y = package_height / 2 - 0.5

		footprint.add(self, rectangle(cfg.FOOTPRINT_PACKAGE_LAYER, 0, 0, package_width, package_height, cfg.FOOTPRINT_PACKAGE_LINE_WIDTH, True))
		footprint.add(self, line(cfg.FOOTPRINT_PACKAGE_LAYER, -line_x, line_y, line_x, line_y, cfg.FOOTPRINT_PACKAGE_LINE_WIDTH))

		diff = -line_x - x
		line_y += diff
		footprint.add(self, circle(cfg.FOOTPRINT_PACKAGE_LAYER, x, line_y, x - 0.3, line_y, cfg.FOOTPRINT_PACKAGE_LINE_WIDTH))
		for i in range(pad_count / 2):
			footprint.add(self, pad(cfg.FOOTPRINT_SMD_LAYERS, pin, technology.smd, type.rect, x, pad_distance / 2, pad_width, pad_height))
			x += pad_grid
			pin += 1

		for i in range(pad_count / 2, pad_count):
			x -= pad_grid
			footprint.add(self, pad(cfg.FOOTPRINT_SMD_LAYERS, pin, technology.smd, type.rect, x, -pad_distance / 2, pad_width, pad_height))
			pin += 1

class qfp(footprint):
	"""Generator for LQFP/TQFP/PQFP and other xQFP footprints"""

	def __init__(self, name, description, tags, package_width, package_height, pad_width, pad_height, pad_grid, pad_distance_x, pad_distance_y, pad_count_x, pad_count_y):
		footprint.__init__(self, name, description, tags)

		if pad_count_x % 2 or pad_count_y % 2:
			raise NameError("Pad count is odd!")

		footprint.add(self, rectangle(cfg.FOOTPRINT_PACKAGE_LAYER, 0, 0, package_width, package_height, cfg.FOOTPRINT_PACKAGE_LINE_WIDTH, True))

		pin = 1
		y = pad_grid * -((float(pad_count_y) / 4) - 0.5)
		x = pad_grid * -((float(pad_count_x) / 4) - 0.5)
		footprint.add(self, circle(cfg.FOOTPRINT_PACKAGE_LAYER, x, y, x + 0.5, y, cfg.FOOTPRINT_PACKAGE_LINE_WIDTH))
		for i in range(pad_count_y / 2):
			footprint.add(self, pad(cfg.FOOTPRINT_SMD_LAYERS, pin, technology.smd, type.rect, -pad_distance_x / 2, y, pad_width, pad_height, 0, 90))
			y += pad_grid
			pin += 1

		for i in range(pad_count_x / 2):
			footprint.add(self, pad(cfg.FOOTPRINT_SMD_LAYERS, pin, technology.smd, type.rect, x, pad_distance_y / 2, pad_width, pad_height, 0, 0))
			x += pad_grid
			pin += 1

		y = pad_grid * ((float(pad_count_y) / 4) - 0.5)
		for i in range(pad_count_y / 2):
			footprint.add(self, pad(cfg.FOOTPRINT_SMD_LAYERS, pin, technology.smd, type.rect, pad_distance_x / 2, y, pad_width, pad_height, 0, 90))
			y -= pad_grid
			pin += 1

		x = pad_grid * ((float(pad_count_x) / 4) - 0.5)
		for i in range(pad_count_x / 2):
			footprint.add(self, pad(cfg.FOOTPRINT_SMD_LAYERS, pin, technology.smd, type.rect, x, -pad_distance_y / 2, pad_width, pad_height, 0, 0))
			x -= pad_grid
			pin += 1


class bga(footprint):
	"""Generator for ball grid array footprints"""

	def __init__(self, name, description, tags, package_width, package_height, pad_diameter, pad_grid, pad_distance, count_x, count_y):
		footprint.__init__(self, name, description, tags)

if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser(description = 'Footprint generator from csv table.')
	parser.add_argument('--csv', metavar = 'csv', type = str, help = 'CSV formatted input table', required = True)
	parser.add_argument('--output_path', metavar = 'output_path', type = str, help = 'Output path for generated KiCAD footprint files', required = True)
	args = parser.parse_args()

	with open(args.csv, 'rb') as csvfile:
		table = csv.reader(csvfile, delimiter=',', quotechar='\"')
		first_row = 1
		for row in table:
			if first_row == 1:
				header = row
				first_row = 0
			else:
				data = dict(zip(header, row))
				# Can this be made little bit more elegant?
				for key in data:
					try:
						if key.find("count") != -1:
							data[key] = int(data[key])
						else:
							data[key] = float(data[key])
					except:
						pass

#	eval generator call
				generator = data['generator']
				del data['generator']

				if generator == "soic":
					fp = soic(**data)
				elif generator == "dip":
					fp = dip(**data)
				elif generator == "qfp":
					fp = qfp(**data)
				elif generator == "wired_resistor":
					fp = wired_resistor(**data)
				elif generator == "connector_grid_male":
					fp = connector_grid_male(**data)
				elif generator == "connector_grid_female":
					fp = connector_grid_female(**data)

				if 'fp' in locals():
					output = open(args.output_path+'/'+data['name']+cfg.FOOTPRINT_EXTENSION, "w")
				#	print fp.render()
					output.write(fp.render())
					output.close()
					del fp
				else:
					print "Unknown footprint generator '"+generator+"'"
