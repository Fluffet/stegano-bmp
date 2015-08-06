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

def encode_24bit(message, image_content):
	padding_counter = 0
	add_padding = False
	offset = 0

	for character in message:

		character_bits = "{0:08b}".format(character)
		bit_no = 0

		while(bit_no <= 7):
			color_value = image_content[offset]
			
			if (color_value%2) !=  ord(character_bits[bit_no]) & 0x1:
				color_value = color_value ^ 0x1

			image_content[offset] = color_value
			bit_no+=1
			offset+=1
			padding_counter +=1

			if padding_counter % 3 ==0:
				padding_counter=0
				offset+=2


	return image_content

def decode_24bit_file(image_content):
	decoded_message = ""
	offset=0
	padding_counter=0

	while offset < len(image_content)+20:
		bitstring = ""
		bit_no = 0

		while(bit_no <= 7):
			color_value = image_content[offset]
			
			offset+=1
			bitstring += str(color_value & 0x1)
			bit_no +=1
			
			padding_counter+=1
			if padding_counter % 3 ==0:
				offset+=2
				padding_counter=0

		decoded_character = chr(int(bitstring,2))
		if decoded_character == "|":
			print(decoded_character)
			break

		decoded_message += decoded_character

	print(decoded_message)



def reconstruct_file(bytedata,image_content):
	global args
	with open("result.bmp","wb") as destfile:
		destfile.write(bytedata[0:54] + image_content)

with open(args.sourcefile, 'rb') as bmp_file:
	bytedata = bytearray(bmp_file.read())

	bitmap_header = BMP_Headerstruct._make(struct.unpack(header_fmt, bytedata[0:14]))

	#if bytearray(bitmap_header.type).encode("utf-8") not in ["BM", "BA", "CI", "CP", "IC", "PT"]:
	#	raise BMPException("This is not a BMP file. :(")

	bitmap_dibheader = BMP_DIBHeader._make(struct.unpack(dibheader_fmt, bytedata[14:54]))

	print(bitmap_header)
	print(bitmap_dibheader)
	
	image_content = bytedata[bitmap_header.offset:]

	message = bytes(args.message + "|",encoding="ascii")

	if len(message*8) > bitmap_dibheader.imgheight * bitmap_dibheader.imgwidth:
		raise BMPException("The message is too large to fit inside this bitmap file")

	if bitmap_dibheader.depth == 24:
		image_content = encode_24bit(message,image_content)
		reconstruct_file(bytedata,image_content)

with open("result.bmp",'rb') as f:
	bytedata = bytearray(f.read())
	decode_24bit_file(bytedata[54:])