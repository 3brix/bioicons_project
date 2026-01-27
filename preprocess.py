# import libraries
import io
from pathlib import Path
import requests  # source/usage w3schools: https://www.w3schools.com/PYTHON/ref_requests_response.asp
import cairosvg
from PIL import Image


# test url for one svg
#url = "https://raw.githubusercontent.com/duerrsimon/bioicons/main/static/icons/cc-0/Nucleic_acids/Kumar/DNA.svg"

# config, folderstructure: static/svg (raw), static/png: img + caption(.txt.)
input_folder = Path("static/svg")
output_folder = Path("static/png")

input_folder.mkdir(exist_ok=True)
output_folder.mkdir(exist_ok=True)

# img
limit = 5  # nr of svgs fetched
size = 1024 # to be compatible with FLUX.1-dev
output_png = output_folder / "DNA.png"

# caption
instance_name: str = "bioicon"
class_name: str = "style"
instance_prompt = "scientific icon, white background"


# find data, data located on github, loop through folders
api_url = "https://api.github.com/repos/duerrsimon/bioicons/content/static/icons/"



svg_urls = []

def find_svgs(url):
    """
    Recursively looks for icons. Opens folders till there is a leaf (svg-file), then put it in the collection. Stops once reaching limit.
    """
    if len(svg_urls) >= limit: return # safety check: limits
    res = requests.get(url)
    if res.status_code != 200: return # status check

    items = res.json()  # more info: https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28#get-repository-content
    for item in items:
        if len(svg_urls) >= limit: break
        if item["type"] == "dir":
            find_svgs(item["url"])
        elif item ["name"].endswith(".svg"):
            svg_urls.append((item["name"], item["download_url"]))

print("Searching for icons...")
find_svgs(api_url)


# for loop
png_data = cairosvg.svg2png(
     bytestring=response.content,
    # write_to=str(png_file),
     output_width=size,
     output_height=size,  # if img not square can cause problems, using only width can maintain initial aspect ratio
    # background_color="white" (if no additional preprocessing)
    )

# white background
img = Image.open(io.BytesIO(png_data)).convert("RGBA")
# center?
white_bg = Image.new("RGBA", img.size, (255, 255, 255))  # no alpha channel needed
# paste using the original image as mask --> smooth edges?
white_bg.paste(img, mask=img)
white_bg.save(output_png, "PNG")


print(f"Test ok {output_png}")



# generate captions using the image names
# Convert string to a Path object
img_path = Path(output_png)

# .with_suffix(".txt") changes the extension perfectly
caption_path = img_path.with_suffix(".txt")

# .stem gets the filename without any extension
simple_name = img_path.stem.replace("_", " ").replace("-", " ")

with open(caption_path, "w") as f:
    f.write(f" a {instance_name} {class_name} illustration of {simple_name}, {instance_prompt}")

# save ds  