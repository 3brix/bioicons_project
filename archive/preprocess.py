# import libraries
import io
from pathlib import Path
import requests  # source/usage w3schools: https://www.w3schools.com/PYTHON/ref_requests_response.asp
import cairosvg
from PIL import Image


# config, folderstructure: static/svg (raw), static/png: img + caption(.txt.)
input_folder = Path("static/svg")
output_folder = Path("static/png")

input_folder.mkdir(exist_ok=True)
output_folder.mkdir(exist_ok=True)

# img
limit = 5  # nr of svgs fetched
size = 1024 # to be compatible with FLUX.1-dev
output_png = output_folder

# caption
instance_name: str = "bioicon"
class_name: str = "style"
instance_prompt = "scientific icon, white background"


# find data, data located on github, loop through folders
print(f"Fetching icons from Bioicons GitHub...")
api_url = "https://api.github.com/repos/duerrsimon/bioicons/contents/static/icons"
response = requests.get(api_url)


target_categories = ["Human_physiology", "Intracellular_components", "Genetics"]

svg_urls = []

def find_svgs(url, current_depth=0):
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
            if current_depth != 1 or item["name"] in target_categories:
                 find_svgs(item["url"], current_depth + 1)

        elif item ["name"].endswith(".svg"):
            svg_urls.append((item["name"], item["download_url"]))

print("Searching for icons...")
find_svgs(api_url)


for name, download_url in svg_urls:
    print(f"Processing...: {name}")
    # fetch
    svg_res = requests.get(download_url)
    if svg_res.status_code != 200: continue


    # rasterize
    png_data = cairosvg.svg2png(
        bytestring=svg_res.content,
        output_width=size,
        output_height=size,  # if img not square can cause problems, using only width can maintain initial aspect ratio
        # background_color="white" (if no additional preprocessing)
    )


    # white background
    img = Image.open(io.BytesIO(png_data)).convert("RGBA")
    white_bg = Image.new("RGBA", img.size, (255, 255, 255, 255)) 
    # paste using the original image as mask --> smooth edges?
    white_bg.paste(img, mask=img)
    final_img = white_bg.convert("RGB")
    # save
    png_path = output_folder / name.replace(".svg", ".png")
    final_img.save(png_path, "PNG")


    # generate captions using the image names
    img_path = png_path
    # .with_suffix(".txt") changes the extension perfectly
    caption_path = img_path.with_suffix(".txt")
    # .stem gets the filename without any extension
    simple_name = img_path.stem.replace("_", " ").replace("-", " ")

    with open(caption_path, "w") as f:
        f.write(f"a {instance_name} {class_name} illustration of {simple_name}, {instance_prompt}")

# save ds  
print("Preprocessing complete.")