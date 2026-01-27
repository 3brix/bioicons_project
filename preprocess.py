# import libraries
from pathlib import Path
import cairosvg


# config, folderstructure: static/svg (raw), static/png: img + caption(.txt.)
input_folder = Path("static/svg")
output_folder = Path("static/png")
output_folder.mkdir(exist_ok=True)

size = 1024 # to be compatible with FLUX.1-dev

# find data, data located on github, loop through folders

# download the .svgs in local folder

# convert svgs into pngs(1024)
for svg_file in input_folder.glob("*.svg"):
    png_file=output_folder /svg_file.with_suffix(".png").name

    # convert
    cairosvg.svg2png(
     url=str(svg_file),
     write_to=str(png_file),
     output_width=size,
     output_height=size   
    )

print(f"Test ok {png_file}")

# white background

# generate captions using the image names

# save ds  