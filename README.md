# bioicons_project

## 1. Task
Scientist and students often need icons for figures, but creating vector style icon from sratch requires graphic design skills. In this project we attempt to fine-tune Black Forests FLUX.1-dev model to learn the specific visual patterns of the "bioicons" library.
Our objective is to generate new, scientifically accurate icons in "bioicons style".  

## 2. Dataset
The dataset originates from bioicons.com, an open-source repository of scientific illustrations hosted on GitHub.
The raw data consist of 2804 icons(bioicons.com) as SVG-files categorized by scientific field. The illustrations are contributed by various scientific illustrators, but generally follow a unified aesthetic. Most icons are under MIT, CC0 or CC-BY-(SA) licences, which makes them ideal for use them in academic projects. These licences allow to reuse, modify and build upon the data with easy-to-meet requirements (BY: credit must be given to the creator, SA: Adaptations must be licenced under the same terms). Source and details: https://mit-license.org/, https://creativecommons.org/share-your-work/cclicenses/.

## 3. Related related work / problems / tasks in literature

## 4. Preprocessing
In progress... 

The initial plan was to find the data automatically (located on the github page of bioicons in static, loop through subfolders) then download the SVG-files into a local folder. A recursive function was created to navigate the nested folders via the GitHub API, identifying and gathering download links for multiple SVG-files. However, at the testing phase it had to be reconsiered because of GitHub REST API request limits and lack of control.

As a result, a local version was created which requires to first clone the bioicon repo or manually download the selected icons. The logic of the preprocessing loop remained identical: Using the folder structure,  SVGs were (at this point) filtered by target category (i proceded with animals, CC-0) and were converted into a 1024 pixel PNG using cairosvg, and processed with PIL to replace transparency with solid white background for better model compatibility. Finally, the script generates matching captions as TXT, based on the original filename of the svgs and utilizing a special trigger prompt to associate the visual data with the textual descriptions for training. All pairs (PNG + TXT) are saved in the directory static/png. The dataset was uploaded to modal volume using batch upload. 

Later to be more straighforward, the local preprocessing was updated for manual curation and we switched to huggingface to host our test data (79 image caption pairs from catgory "Animals").

TO DO: The curation of the final dataset is yet to be done.

## 5. Initial Model
In progress... 

To build the initial pipeline, the script from the heroicons exercise was adapted. The initial model, Black Forest Labs FLUX.1 and its weights and the test dataset were loaded / fetched using huggingface. First test was succesful using lr 1e-4, max_trainstep 1000 and rank 16. The output is reasonable. 

## 6. Fine tuning and final model

## 7. Results

## 8. Lessons / challenges / further ideas
As we decided on the project to be to train Black Forests Flux.1-dev on Bioicons similar to the Heroicons exercise, the fist challenge was to understand the heroicons script. We read the comments and links provided in the script and consulted with the modal blog of a similar project. We also used AI(Gemini/ChatGPT) to understand the code better. The second problem we need to address was how to choose, download, curate and then preprocess the dataset. Then we needed to decide on a platform to host our dataset which enables us to share it and the pipeline to be reproducible as in the heroicons example. First we tried to work with a modal volume (suggested by ChatGPT), but then decided to switch to huggingface to be more strightforward. 

More on AI: Fist we tried to work with AI, but eventually it made us take detours and suggested controversal procedures. It turned out to be easier and less frustrating to find blogs / examples / tutorials and adapt them... It was still helpful to get the context and easily find resources though. 

## 9. References

Data:
https://huggingface.co/datasets/yirenlu/heroicons-subset-25-images/viewer,
https://modal.com/docs/reference/modal.Volume#batch_upload,hero,
https://www.w3schools.com/PYTHON/ref_requests_response.asp,
https://www.w3schools.com/python/python_recursion.asp,
https://pytutorial.com/handling-transparency-and-alpha-channels-with-pillow/,
https://medium.com/@ackmanb/,how-to-train-the-flux-1-image-generation-model-a-step-by-step-guide-291557d8f8db,
https://huggingface.co/docs/datasets/en/image_dataset,
https://www.geeksforgeeks.org/nlp/how-to-load-a-huggingface-dataset-from-local-path/,
https://www.exgenex.com/article/how-to-create-a-huggingface-dataset

Initial Model:
https://modal.com/blog/fine-tuning-flux-style-lora

