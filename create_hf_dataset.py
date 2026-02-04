
# i curated the animals category of bioicons and created a test dataset:

from datasets import Dataset, DatasetDict, Features, Value, Image
from pathlib import Path

# Set your local dataset folder
dataset_dir = Path("./static/png_curated")  # folder with .png and .txt files


images = []
texts = []

for img_file in dataset_dir.glob("*.png"):
    txt_file = img_file.with_suffix(".txt")
    if txt_file.exists():
        images.append(str(img_file))
        with open(txt_file, "r", encoding="utf-8") as f:
            texts.append(f.read().strip())

print(f"Found {len(images)} image-text pairs.")

# Define the dataset features
features = Features({
    "image": Image(), 
    "text": Value("string")
})

# Create the dataset
dataset = Dataset.from_dict({"image": images, "text": texts}, features=features)

# Wrap in DatasetDict
dataset_dict = DatasetDict({"train": dataset})

# Push to Hugging Face Hub
dataset_dict.push_to_hub("3brix/bioicons-animal", private=False)  # you have to change it to yours...
print("Dataset uploaded!")


# if you create a dataset: you have login to huggingface hub, with a token:
# huggingface website: your avatar, acces tokens, create token, write permission
# cli: huggingface-cli login --> add your token