#!/usr/bin/env /cluster/home/jlawlor/envs/igvgraph/bin/python3.9
from __future__ import print_function
import argparse
import img2pdf
from PIL import Image, ImageFont, ImageDraw
from tempfile import mkstemp

parser = argparse.ArgumentParser(description="Combine image files into a png.")
parser.add_argument('-o', '--output', type=str, required=True, help="File prefix.")
parser.add_argument('imagefiles', type=str, nargs="*", help="image files to combine into pdf")
parser.add_argument('-t', '--textfile', type=str, help="Text file to add to pdf.")
args = parser.parse_args()

if args.textfile:
    with open(args.textfile, "rt") as f:
        text_to_draw = f.read()
    font = ImageFont.truetype("/cluster/lab/gcooper/igv-grapher/times-ro.ttf", 16)
    temp_image = mkstemp(suffix='.png')[1]
    img = Image.new('RGB', (1024, 768), color = 'white')
    draw = ImageDraw.Draw(img)
    draw.text((50,50),text_to_draw,(0,0,0),font=font)
    img.save(temp_image)
    args.imagefiles.append(temp_image)


print('Combining {} to {}'.format(" ".join(args.imagefiles), args.output))
with open(args.output, "wb") as pdf:
    pdf.write(img2pdf.convert(args.imagefiles))

print('Done')
