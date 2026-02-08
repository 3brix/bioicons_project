# Bioicons Project - CO5

## 1. Related related work / problems / tasks in literature
Recent advances in text-to-image diffusion models have focused on efficient fine-tuning and subject-driven generation. Several adapter and fine-tuning strategies have emerged improving efficiency and flexibility. 

Since our project uses a combined Dreambooth and LoRA we focus only on them. DreamBooth by Ruiz et al. is a training technique that updates the entire diffusion model by training on just a few images of a subject or style. It works by associating a special word in the prompt with the example images and can generate a wide variety of images of the subject in different contexts, guided by a text prompt (1),(5).

LoRA by Hu et al. allows large models to adapt with minimal memory cost by freezing the base model weights and injecting small adapter modules (low-rank matrices into selected layers). This way most of the base model’s capabilities are retained while adding new, task-specific functionality (6). Hu et al. also states that “LoRA can be combined with other efficient adaptation methods, potentially providing orthogonal improvement” (2), e.g. DreamBooth to speedup training (7).

A comparative overview of four popular methods, Dreambooth, LoRA, Hypernetworks, and Textual Inversion by Martini et al., found that LoRA is the most efficient for producing high-quality outputs with minimal computational overhead (3).

In a recent study by Pascua et al. (4) applies a few-shot, multi-token DreamBooth - LoRA approach using dreambooth_lora_flux.py on FLUX-based models, achieving style-consistent character generation. However, the study largely focus on artistic or character domains, there is currently limited evaluation of how well DreamBooth - LoRA preserves conceptual consistency and symbolic semantics rather than just visual style.

## 2. Task
Scientist and students often need icons for figures, but creating a vector style icon from sratch requires graphic design skills. In this project we attempt to fine-tune Black Forests FLUX.1-dev model to learn the specific visual patterns of the "bioicons" library.
Our objective is to generate new, scientifically accurate icons in "bioicons style".  

## 3. Dataset
The dataset originates from bioicons.com, an open-source repository of scientific illustrations hosted on GitHub.
The raw data consist of 2804 icons (8) as SVG-files categorized by scientific field. The illustrations are contributed by various scientific illustrators, but generally follow a unified aesthetic. Most icons are under MIT, CC0 or CC-BY-(SA) licences, which makes them ideal for use them in academic projects. These licences allow to reuse, modify and build upon the data with easy-to-meet requirements (BY: credit must be given to the creator, SA: Adaptations must be licenced under the same terms). Source and details: (9), (10).

## 4. Preprocessing
The initial plan was to find the data automatically (located on the github page of bioicons in static, loop through subfolders) then download the SVG-files into a local folder. A recursive function was created to navigate the nested folders via the GitHub API, identifying and gathering download links for multiple SVG-files. However, at the testing phase it had to be reconsidered because of GitHub REST API request limits and lack of control.

As a result, a local version was created which requires to first clone the bioicon repository or manually download the selected icons. The logic of the preprocessing loop remained identical: Using the folder structure, SVGs were filtered by target category and were converted into a 1024 pixel PNG using cairosvg, and processed with PIL to replace transparency with solid white background for better model compatibility. Finally, the script generates matching captions as TXT, based on the original filename of the SVGs and utilizing a special trigger prompt to associate the visual data with the textual descriptions for training. All pairs (PNG + TXT) were saved in the directory static/png. The dataset was uploaded to modal volume using batch upload. 

Later, to be more straightforward, the local preprocessing was updated for manual curation and we switched to Hugging Face to host our test data. During inspection we found that bioicons are visually not uniform across contributors: while the repository contains thousands of SVGs from many illustrators, some sources follow incompatible visual conventions for a single LoRA training set. In particular, icons credited to "Servier" (i.e., the Servier Medical Art library) follow a clean, minimal "icon" language (flat fills, black outlines, limited colors), whereas other large contributors (e.g., DBCLS) include much more detailed, multi-color, Illustrator-like exports with very large file sizes. Mixing these would teach the model conflicting visual rules and reduce style consistency. To maximize stylistic coherence, we therefore restricted the final training subset to a single source style family (Servier Medical Art, CC-BY-3.0) and expanded across multiple categories to increase subject diversity while keeping the style constant. The final selection contains 100 SVGs, distributed across categories such as Animals (19), Parasites (19), Lab_apparatus (15), Microbiology (15), Plants_Algae (10), Viruses (7), Oncology (5), Tissues (5), and Intracellular (5). We also addressed a near-duplicate issue inside categories (especially Animals), where many files were merely color variants of the same subject (e.g., multiple mouse/rabbit/fruitfly recolors).

## 5. Initial Model

To build the initial pipeline, the script from the heroicons exercise was adapted. The initial model, Black Forest Labs FLUX.1 and its weights and the test dataset were loaded / fetched using huggingface. First test was succesful using lr 1e-4, max_trainstep 1000 and rank 16. The output was reasonable. 
Initial Configuration Test:
Learning Rate: 1e-4
Max Training Steps: 1000
LoRA Rank: 16
Instance Prompt: "a bioicon style illustration of"
Class Prompt: "a style illustration of" (for prior preservation)

## 6. Fine tuning and final model
To find the optimal final model, we conducted an exhaustive hyperparameter search by testing all possible combinations of three key configurations. We experimented with three different learning rates (1e-4, 2e-4, 3e-4) to identify which rate enables the model to learn the Bioicon style most effectively and stably. We also evaluated four distinct training durations (1000, 1500, 3000, and 4000 steps) to determine the optimal point where the model captures the style well without overfitting to the training examples. Additionally, we tested three different LoRA adapter capacities (ranks 8, 16, and 32), which control how much the model can modify the original architecture.

In total, this resulted in 36 different combinations that we trained in parallel using Modal's infrastructure. Each resulting model was automatically evaluated with 15 test prompts covering diverse biological and scientific subjects, ranging from jellyfish to neurons and viruses. The results were organized into comparative tables in Weights & Biases, allowing us to visually identify which combination of hyperparameters produces the best Bioicon-style illustrations while maintaining the base model's capability to generate other types of images.

## 7. Results
The hyperparameter sweep successfully trained all 36 model configurations and revealed clear patterns in performance:
- Learning Rate: 2e-4 (balanced convergence speed and stability)
- Training Steps: 3000 (sufficient for style capture without overfitting)
- LoRA Rank: 16 (optimal capacity for style adaptation)

## 8. Lessons / challenges / further ideas
As we decided on the project to be to train Black Forests Flux.1-dev on Bioicons (similar to the Heroicons exercise), the first challenge was to understand the heroicons script. We read the comments and links provided in the script and consulted with a Modal blog of a similar project. We also used AI(Gemini/ChatGPT) to understand the code better. 

The second problem we need to address was how to choose, download, curate and then preprocess the dataset. Then we needed to decide on a platform to host our dataset which enables us to share it and the pipeline to be reproducible as in the heroicons example. First, we tried to work with a Modal volume, but then decided to switch to huggingface to be more strightforward. 

Further work could focus on (1) expanding the curated dataset across more categories while keeping a single style family, (2) automating duplicate removal (e.g., hashing rendered PNGs to detect near-identical icons), and (3) running a broader hyperparameter sweep (rank, learning rate, training steps, and resolution) to study overfitting vs. generalization. In addition, we would like to test prompt/caption strategies more systematically—for example, comparing generic “bioicon style” prompts to captions that include the icon’s semantic label—to see how strongly the model learns style versus subject content.


## 9. References

Literature:

1. Nataniel Ruiz, Yuanzhen Li, Varun Jampani, Yael Pritch, Michael Rubinstein, Kfir Aberman, DreamBooth: Fine Tuning Text-to-Image Diffusion Models for Subject-Driven Generation, 2022, https://arxiv.org/abs/2208.12242

2. Edward J. Hu, Yelong Shen, Phillip Wallis, Zeyuan Allen-Zhu, Yuanzhi Li, Shean Wang, Lu Wang, Weizhu ChenLoRA: Low-Rank Adaptation of Large Language Models,2021, https://arxiv.org/abs/2106.09685 

3. Martini, L.; Iacono, S.; Zolezzi, D.; Vercelli, G.V. Advancing Persistent Character Generation: Comparative Analysis of Fine-Tuning Techniques for Diffusion Models. AI 2024, 5, 1779-1792. https://doi.org/10.3390/ai5040088

4. Ruben Pascual, Mikel Sesma-Sara, Aranzazu Jurio, Daniel Paternain, Mikel Galar, Few-shot multi-token DreamBooth with LoRa for style-consistent character generation, 2025, https://arxiv.org/abs/2510.09475

5. https://huggingface.co/docs/diffusers/training/dreambooth, accessed: 07.02.2026

6. https://oicm.docs.openinnovation.ai/latest/llm/lora-adapters.html#2-enabling-lora-in-fine-tuning, accesssed: 07.02.2026

7. https://huggingface.co/docs/diffusers/training/lora, accessed: 07.02.2026

8. bioicons.com, accessed: 30.01.2026
 
9. https://mit-license.org/, acessed: 31.01.2026

10. https://creativecommons.org/share-your-work/cclicenses/, accessed: 31.01.2026



### 10. Resources
Data and Preprocessing:

https://huggingface.co/datasets/yirenlu/heroicons-subset-25-images/viewer, accessed: 01.02.2026

https://modal.com/docs/reference/modal.Volume#batch_upload,hero, accessed: 01.02.2026

https://www.w3schools.com/PYTHON/ref_requests_response.asp, accessed: 01.02.2026

https://www.w3schools.com/python/python_recursion.asp, accessed: 01.02.2026

https://pytutorial.com/handling-transparency-and-alpha-channels-with-pillow/, accessed: 29.01.2026

https://medium.com/@ackmanb/,how-to-train-the-flux-1-image-generation-model-a-step-by-step-guide-291557d8f8db, accessed: 01.02.2026

https://huggingface.co/docs/datasets/en/image_dataset, accessed: 01.02.2026

https://www.geeksforgeeks.org/nlp/how-to-load-a-huggingface-dataset-from-local-path/, accesssed: 04.02.2026

https://www.exgenex.com/article/how-to-create-a-huggingface-dataset accessed: 04.02.2026

https://huggingface.co/blog/flux-qlora accessed: 01.02.2026




Initial Model:

https://modal.com/blog/fine-tuning-flux-style-lora, accessed: 04.02.2026

