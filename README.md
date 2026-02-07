# bioicons_project

## 1. Task
Scientist and students often need icons for figures, but creating vector style icon from sratch requires graphic design skills. In this project we attempt to fine-tune Black Forests FLUX.1-dev model to learn the specific visual patterns of the "bioicons" library.
Our objective is to generate new, scientifically accurate icons in "bioicons style".  

## 2. Dataset
The dataset originates from bioicons.com, an open-source repository of scientific illustrations hosted on GitHub.
The raw data consist of 2804 icons(bioicons.com) as SVG-files categorized by scientific field. The illustrations are contributed by various scientific illustrators, but generally follow a unified aesthetic. Most icons are under MIT, CC0 or CC-BY-(SA) licences, which makes them ideal for use them in academic projects. These licences allow to reuse, modify and build upon the data with easy-to-meet requirements (BY: credit must be given to the creator, SA: Adaptations must be licenced under the same terms). Source and details: https://mit-license.org/, https://creativecommons.org/share-your-work/cclicenses/.

## 3. Related related work / problems / tasks in literature
Recent advances in text-to-image diffusion models have focused on efficient fine-tuning and subject-driven generation.
Several adapter and fine-tuning strategies have emerged to improve efficiency and flexibility. Martini et al. provide a comparative overview of four popular methods, Dreambooth, LoRA, Hypernetworks, and Textual Inversion (1).


Since our project uses a combined Dreambooth and LoRA we focus only on them. DreamBooth by Ruiz et al. is a training technique that updates the entire diffusion model by training on just a few images of a subject or style. It works by associating a special word in the prompt with the example images and can generate a wide variety of images of the subject in different contexts, guided by a text prompt (2),(5).


LoRA by Hu et al. allows large models to adapt with minimal memory cost by freezing the base model weights and injecting small adapter modules (low-rank matrices into selected layers). This way most of the base model’s capabilities are retained while adding new, task-specific functionality (6).


Hu et al. also states that “LoRA can be combined with other efficient adaptation methods, potentially providing orthogonal improvement”(3), e.g. DreamBooth to speedup training (7).

A recent study by Pascua et al. (4) applies a few-shot, multi-token DreamBooth - LoRA approach using dreambooth_lora_flux.py on FLUX-based models, achieving style-consistent character generation.However, the study largely focus on artistic or character domains, there is currently limited evaluation of how well DreamBooth - LoRA preserves conceptual consistency and symbolic semantics rather than just visual style.

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
https://huggingface.co/datasets/yirenlu/heroicons-subset-25-images/viewer, accesssed: 01.02.2026
https://modal.com/docs/reference/modal.Volume#batch_upload,hero, accesssed: 01.02.2026
https://www.w3schools.com/PYTHON/ref_requests_response.asp, accesssed: 01.02.2026
https://www.w3schools.com/python/python_recursion.asp, accesssed: 01.02.2026
https://pytutorial.com/handling-transparency-and-alpha-channels-with-pillow/, accesssed: 29.01.2026
https://medium.com/@ackmanb/,how-to-train-the-flux-1-image-generation-model-a-step-by-step-guide-291557d8f8db, accesssed: 01.02.2026
https://huggingface.co/docs/datasets/en/image_dataset, accesssed: 01.02.2026
https://www.geeksforgeeks.org/nlp/how-to-load-a-huggingface-dataset-from-local-path/, accesssed: 04.02.2026
https://www.exgenex.com/article/how-to-create-a-huggingface-dataset accesssed: 04.02.2026

Literatur:
1. Martini, L.; Iacono, S.; Zolezzi, D.; Vercelli, G.V. Advancing Persistent Character Generation: Comparative Analysis of Fine-Tuning Techniques for Diffusion Models. AI 2024, 5, 1779-1792. https://doi.org/10.3390/ai5040088

2. Nataniel Ruiz, Yuanzhen Li, Varun Jampani, Yael Pritch, Michael Rubinstein, Kfir Aberman, DreamBooth: Fine Tuning Text-to-Image Diffusion Models for Subject-Driven Generation, 2022, https://arxiv.org/abs/2208.12242

3. Edward J. Hu, Yelong Shen, Phillip Wallis, Zeyuan Allen-Zhu, Yuanzhi Li, Shean Wang, Lu Wang, Weizhu ChenLoRA: Low-Rank Adaptation of Large Language Models,2021, https://arxiv.org/abs/2106.09685 

4. Ruben Pascual, Mikel Sesma-Sara, Aranzazu Jurio, Daniel Paternain, Mikel Galar, Few-shot multi-token DreamBooth with LoRa for style-consistent character generation, 2025, https://arxiv.org/abs/2510.09475


5. https://huggingface.co/docs/diffusers/training/dreambooth, accesssed: 07.02.2026
6. https://oicm.docs.openinnovation.ai/latest/llm/lora-adapters.html#2-enabling-lora-in-fine-tuning, accesssed: 07.02.2026
7. https://huggingface.co/docs/diffusers/training/lora, accesssed: 07.02.2026


Preprocessing:


Initial Model:
https://modal.com/blog/fine-tuning-flux-style-lora, accesssed: 04.02.2026

