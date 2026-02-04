# first you have to curate a subset the raw svgs in a folder

import io
import os
from pathlib import Path
import cairosvg
from PIL import Image

# # config, folderstructure: static/svg (raw), static/png: img + caption(.txt.)
input_folder = Path("static/raw_png_curated")
output_folder = Path("static/png_curated")
output_folder.mkdir(exist_ok=True, parents=True)

# img
size = 1024

# caption
# limit = 5
instance_name = "bioicon"
class_name = "style"
instance_prompt = "flat vector icon, white background"

print(f"Starting preprocessing data from {input_folder}.")

# local loop
svg_files=list(input_folder.glob("*.svg"))
            
if not svg_files:
            print: (f"No svg files in {input_folder}.")
else: 
    for svg_file in svg_files:
            name = svg_file.name
            try:
                # rasterization, convert SVG -> PNG
                png_data = cairosvg.svg2png(
                    url=str(svg_file),
                    output_width=size,
                    output_height=size,  # if img not square can cause problems, using only width can maintain initial aspect ratio (but is it ok though?)
                    # background_color="white" (if no additional preprocessing)
                )

                # white background
                img = Image.open(io.BytesIO(png_data)).convert("RGBA")
                white_bg = Image.new("RGBA", img.size, (255, 255, 255, 255)) 
                
                # paste using the original image as mask --> smooth edges?
                white_bg.paste(img, mask=img)
                final_img = white_bg.convert("RGB")

                # center?

                # save
                png_path = output_folder / name.replace(".svg", ".png")
                final_img.save(png_path, "PNG")

                # generate captions using the image namesg the image names
                img_path = png_path
                # .with_suffix(".txt") changes the extension perfectly
                caption_path = img_path.with_suffix(".txt")
                # .stem gets the filename without any extension
                simple_name = img_path.stem.replace("_", " ").replace("-", " ")
                # get right article (a/an)
                article = "an" if simple_name[0].lower() in "aeiou" else "a"


                with open(caption_path, "w") as f:
                    f.write(f"a {instance_name} {class_name} illustration of {article} {simple_name}, {instance_prompt}")
                
                print(f"Success: {name}")

            except Exception as e:
                print(f"Skipping {name} due to error: {e}")

print(f"\nPreprocessing complete! All pairs are in {output_folder}, yay.")