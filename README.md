# WILL to SVG

Python program that reads Wacom WILL file and converts it to SVG. 

The WILL file is the file that contains the most accurate data of drawings made in Wacom products (in my example, the Bamboo slate). Although the Wacom app (Incspace) exports to SVG format, it represents the strokes as closed polygons. If you, for example, draw a straight line in the tablet, the SVG won't have a single path line, but instead a closed shape with the width of the stroke strength that you used to draw the line. 

For several applications, what matters is the path traced by the pen and the strokes widths along that path. That information IS present in the WILL file but, as mentioned before, not in the exported SVG. Hence, this program reads the WILL file and save an SVG with each path as each stroke given in the tablet. For now the program ignores the stroke width (or pen pressure) simply because the SVG format do not seems to support it. But it reads that information from the WILL file, so it is very easy to incorporate into the SVG.

The information contained in the SVG can be used to, for instance, make stop-motions of the drawings in the tablet, since it have the stroke positions in the same order it was given in the tablet. Another thing is that we can now pos-process the draw. For instance change stroke widths, close strokes, etc...

## Software

- Wacom Inkspace

## Hardware

- Wacom Bamboo Slate (drawing tablet)

## Screen-shoots

![Sample](/doc/sample.png?raw=true "Sample")

![img1](/doc/img1.png?raw=true "img1")

![Wacom problem](/doc/wacom_problem.png?raw=true "Wacom problem")

## Instructions

Usage: will_reader.py [filename]
 where filename is the name of the WILL file without the extension.

 Obs.: the file.svg will be overitten