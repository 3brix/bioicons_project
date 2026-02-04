# bioicons_project

## 1. Task
Scientist and students often need icons for figures, but creating vector style icon from sratch requires graphic design skills. In this project we attempt to fine-tune Black Forests FLUX.1-dev model to learn the specific visual patterns of the "bioicons" library.
Our objective is to generate new, scientifically accurate icons in "bioicons style".  

## 2. Dataset
The dataset is curated from bioicons.com, an open-source repository of scientific illustrations hosted on GitHub.
The raw data consist of 2804 icons(bioicons.com) as SVG-files categorized by scientific field. The illustrations are contributed by various scientific illustrators, but generally follow a unified aesthetic. Most icons are under MIT, CC0 or CC-BY-(SA) licences, which makes them ideal for use them in academic projects. These licences allow to reuse, modify and build upon the data with easy-to-meet requirements (BY: credit must be given to the creator, SA: Adaptations must be licenced under the same terms). Source and details: https://mit-license.org/, https://creativecommons.org/share-your-work/cclicenses/.

## 3. Related related work / problems / tasks in literature

## 4. Preprocessing
In progress... The initial plan was to find the data automatically (located on the github page of bioicons in static, loop through subfolders) then download the SVG-files into a local folder. A recursive function was created to navigate the nested folders via the GitHub API, identifying and gathering download links for multiple SVG-files. However, at the testing phase it had to be revonsiered because of GitHub REST API request limits. Then a local version was created, for which one has to first clone the bioicon repo. The logic of the preprocessing loop remained identical: Using the folder structure,  SVGs were (at this point) filtered by target category (i proceded with animals, CC-0) and were converted into a 1024 pixel PNG using cairosvg, and processed with PIL to replace transparency with solid white background for better model compatibility. Finally, the script generates matching captions as TXT, based on the original filename of the svgs and utilizing a special trigger prompt to associate the visual data with the textual descriptions for training. All pairs (PNG + TXT) are saved in the directory static/png. The dataset was uploaded to modal volume using batch upload.

## 5. Initial Model
In progress... The initial model, Black Forest Labs FLUX.1 and its weights was loaded / fetched using Huggingface. First test was succesful using lr 1e-4, max_trainstep 1000 and rank 16. 
## 6. Fine tuning and final model

## 7. Results

## 8. Lessons / challenges / further ideas