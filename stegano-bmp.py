import argparse
import struct
import sys
from collections import namedtuple

class BMPException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class ArgumentException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

parser = argparse.ArgumentParser()

parser.add_argument("action", help="Action can be either 'mask' or 'unmask'")
parser.add_argument('-s', '--sourcebmp', help='Source BMP for either masking or unmasking')
parser.add_argument('-d', '--destination', help='Destination. BMP for masking, whatever you want for unmasking')
parser.add_argument("-m", '--message', help="If you are masking, you need to provide a message. You can pipe a file if you want.")

args = parser.parse_args()

header_fmt    = "<HIII"
BMP_Headerstruct = namedtuple("BMP_Headerstruct", "type size junk offset")
dibheader_fmt = "<3I2H6I"
BMP_DIBHeader    = namedtuple("BMP_DIBHeader", 
	"headersize imgwidth imgheight colorplanes depth compression raw_datasize dpih dpiv palettecolors importantcolors")

# parse command line


def mask_24bit(message, image_content):
	padding_counter = 0
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

def unmask_24bit_file(image_content):
	masked_message = ""
	offset=0
	padding_counter=0

	while offset < len(image_content):
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

		masked_character = chr(int(bitstring,2))
		if masked_character == "|":
			break

		masked_message += masked_character

	return masked_message

def reconstruct_file(bytedata,modified_image_content):
	with open(args.destination,"wb") as destfile:
		destfile.write(bytedata[0:54] + modified_image_content)
		print("Wrote to " + args.destination)





if(args.action == "mask" or args.action == "unmask"):

	if(args.sourcebmp):
		with open(args.sourcebmp, 'rb') as bmp_file:
			bytedata = bytearray(bmp_file.read())

			bitmap_header = BMP_Headerstruct._make(struct.unpack(header_fmt, bytedata[0:14]))

			if struct.pack("h", bitmap_header.type).decode("utf-8") not in ["BM", "BA", "CI", "CP", "IC", "PT"]:
				raise BMPException("This is not a BMP file. :(")

			bitmap_dibheader = BMP_DIBHeader._make(struct.unpack(dibheader_fmt, bytedata[14:54]))
			
			image_content = bytedata[bitmap_header.offset:]

			if( args.action =="mask" and args.destination and args.message):

				try:
					f = open(args.message)
					message = f.read()
					f.close()
					message+= "|"
					message=message.encode("ascii","ignore")
					print("Message found in file " + args.message)
				except FileNotFoundError:
					message = args.message
					message = bytes(message + "|", encoding="ascii")

				if len(message) > 3/32 * bitmap_dibheader.raw_datasize:
					raise BMPException("The message/file is too large to fit inside this bitmap file")

				if bitmap_dibheader.depth == 24:
					image_content = mask_24bit(message,image_content)
					reconstruct_file(bytedata,image_content)
				pass

			elif( args.action =="unmask" ):
				with open(args.sourcebmp,'rb') as source:
					bytedata = bytearray(source.read())
					unmasked_message = unmask_24bit_file(bytedata[bitmap_header.offset :])
					if(args.destination):
						with open(args.destination,'w') as destination:
							destination.write(unmasked_message+"\n")
							print("Masked message written to " + args.destination)
					else:
						print("\n# No destination file, so using stdout. Message is: \n")
						print(unmasked_message)