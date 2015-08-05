import argparse
import struct
from collections import namedtuple

class BMPException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

parser = argparse.ArgumentParser()

parser.add_argument("sourcefile")
parser.add_argument("result")
parser.add_argument("message")

args = parser.parse_args()

header_fmt    = "<HIII"

BMP_Headerstruct = namedtuple("BMP_Headerstruct", "type size junk offset")

dibheader_fmt = "<3I2H6I"
BMP_DIBHeader    = namedtuple("BMP_DIBHeader", 
	"headersize imgwidth imgheight colorplanes depth compression raw_datasize dpih dpiv palettecolors importantcolors")

with open(args.sourcefile, 'rb') as bmp_file:
	bytedata = bytearray(bmp_file.read())

	bitmap_header = BMP_Headerstruct._make(struct.unpack(header_fmt, bytedata[0:14]))

	#if chr(bitmap_header.type) not in ["BM", "BA", "CI", "CP", "IC", "PT"]:
	#	raise BMPException("This is not a BMP file.")

	bitmap_dibheader = BMP_DIBHeader._make(struct.unpack(dibheader_fmt, bytedata[14:54]))

	print(bitmap_header)
	print(bitmap_dibheader)
	
	image_content = bytedata[bitmap_header.offset:]


	#message = "This message is completely hidden in the image"
	message = bytes(args.message,encoding="utf-8")

	if len(message*8) > bitmap_dibheader.imgheight * bitmap_dibheader.imgwidth:
		raise BMPException("The message is too large to fit inside this bitmap file")


	if bitmap_dibheader.depth == 24:
		offset = 0
		add_padding = False

		while offset <= bitmap_dibheader.raw_datasize/2+2:
			r = image_content[offset : offset+1]
			offset+=1
			g = image_content[offset : offset+1]
			offset+=1
			b = image_content[offset : offset+1]
			offset+=1
			print("R G B = " + hex(r[0]) + " " + hex(g[0]) + " " + hex(b[0]) + " Added padding: " + str(add_padding) + " Offset: " + str(offset))
			
			if add_padding: offset+=2
			add_padding = not add_padding #Toggle bool




"""
from PIL import Image
bmp_img = Image.open(args.sourcefile)

assert(bmp_img.format == "BMP")
"""