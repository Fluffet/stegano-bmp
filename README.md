# stegano-bmp

### Description
This is a program for secret messages. You can hide text or files in .bmp files, and it is completely invisible to the naked eye.

This is an image of me chugging a beer:

![Image of Fluffet](./fluffet.bmp)

This is the same image of me chugging a beer, except it has about 550 lines (17600 characters) of the Inception screenplay script in it.

![Image of Fluffet](./fluffet_inception.bmp)

##### How does this work?
In bmp files, the pixels are stored as rgb values. For example, a pixel might be (16,108,234) which is a nice blue.

The binary representation of the same pixel is (0010000, 01101100, 11101010). 

In one pixel of bmp data, we can fit three bits of our message by changing the last bit of the r value, g value and b value. 
This shifts the color slightly. Completely invisible to the naked eye, of course, but it still changes a little.

When masking the letter "a" (which has a binary representation of **110**0001) can encode the first three bits (**110**) in the rgb value to slightly shift the color to (0010000**1**, 0110110**1**, 1110101**0**).

We can't hide too much stuff though, for every 32 bits of bmp we can hide 3 bits of message. I think you could easily change the last two bits and fit double the amount of data and it still wouldn't be noticeable by humans (but maybe by machines).

If you want, you could fit bigger files by compressing them first (untested).
### Contributing
All contributions are very welcome :)

### Usage

##### Masking
```sh
$ python3 stegano-bmp.py mask -s some_image.bmp -d destination_bmp.bmp -m "Super secret message"
```
You can mask contents of a file with
```sh
$ python3 stegano-bmp.py mask -s some_image.bmp -d destination_bmp.bmp -m some_file
```

##### Unmasking
```sh
$ python3 stegano-bmp.py unmask -s some_image_with_hidden_message.bmp
```
You can unmask into a file with
```sh
$ python3 stegano-bmp.py unmask -s some_image_with_hidden_message.bmp -d some_file.txt
```
#### Hiding a file that isn't text (like an image in another image)

Masking:
```sh
$ python3 stegano-bmp.py mask -s some_image.bmp -d destination_bmp.bmp -m some_cool_image.png
```
Demasking:
```sh
$ python3 stegano-bmp.py unmask -s some_image_with_hidden_message.bmp -d some_cool_image_demasked.png
```
Only thing you need to care about is that you need to know the file extension when reconstructing it :)
