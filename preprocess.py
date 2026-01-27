# import libraries
import io
from pathlib import Path
import requests  # source/usage w3schools: https://www.w3schools.com/PYTHON/ref_requests_response.asp
import cairosvg
from PIL import Image

# test url for one svg
url = "https://raw.githubusercontent.com/duerrsimon/bioicons/main/static/icons/cc-0/Nucleic_acids/Kumar/DNA.svg"


# config, folderstructure: static/svg (raw), static/png: img + caption(.txt.)
input_folder = Path("static/svg")
output_folder = Path("static/png")
output_folder.mkdir(exist_ok=True)

size = 1024 # to be compatible with FLUX.1-dev
output_png = output_folder / "DNA.png"

# find data, data located on github, loop through folders

# download the .svgs in local folder
response = requests.get(url)
response.raise_for_status()

# convert svgs into pngs(1024)
#for svg_file in input_folder.glob("*.svg"):
#    png_file=output_folder /svg_file.with_suffix(".png").name

    # convert
png_data = cairosvg.svg2png(
     bytestring=response.content,
    # write_to=str(png_file),
     output_width=size,
     output_height=size,  
    )

img = Image.open(io.BytesIO(png_data))
img.save(output_png)


print(f"Test ok {output_png}")

# white background

# generate captions using the image names

# save ds  