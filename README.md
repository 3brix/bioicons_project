# bioicons_project

## 1. Task
Scientist and students often need icons for figures, but creating vector style icon from sratch requires graphic design skills. In this project we attempt to fine-tune Black Forests FLUX.1-dev model to learn the specific visual patterns of the "bioicons" library.
Our objective is to generate new, scientifically accurate icons in "bioicons style".  

## 2. Dataset
The dataset is curated from bioicons.com, an open-source repository of scientific illustrations hosted on GitHub.
The raw data consist of 2804 icons(bioicons.com) as svg-files categorized by scientific field. The illustrations are contributed by various scientific illustrators, but generally follow a unified aesthetic. Most icons are under MIT, CC0 or CC-BY-(SA) licences, which makes them ideal for use them in academic projects. These licences allow to reuse, modify and build upon the data with easy-to-meet requirements (BY: credit must be given to the creator, SA: Adaptations must be licenced under the same terms). Source and details: https://mit-license.org/, https://creativecommons.org/share-your-work/cclicenses/.

## 3. Related related work / problems / tasks in literature

## 4. Preprocessing
In progress ... The plan is to find the data automatically (located on the github page of bioicons in static, loop through subfolders) then download the svg files into a local folder. Then convert svgs into pngs(1024) and normalize them using cairosvg/pillow, then generate captions using the image names. 

## 5. Initial Model

## 6. Fine tuning and final model

## 7. Results

## 8. Lessons / challenges / further ideas