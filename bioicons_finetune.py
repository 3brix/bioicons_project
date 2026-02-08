import itertools
from dataclasses import dataclass
from pathlib import Path
import cv2
import os
import modal
from fastapi import FastAPI
from fastapi.responses import FileResponse

# Modal app for bioicons training
app = modal.App(name="bioicons-flux")

# Docker image with all required dependencies
image = modal.Image.debian_slim(python_version="3.10").apt_install(
    "git",
    "libgl1-mesa-glx",  # Required for OpenCV
    "libglib2.0-0",
).pip_install(
    # Core training libraries
    "accelerate==0.31.0",
    "datasets==3.1.0",
    "torch~=2.2.0",
    "torchvision~=0.16",
    "transformers~=4.41.2",
    "peft==0.11.1",  # LoRA implementation
    
    # Web UI and API
    "gradio~=4.44.1",
    "fastapi[standard]==0.115.4",
    
    # Additional utilities
    "wandb==0.17.6",  # Experiment tracking
    "opencv-python",  # Image processing
    "albumentations==1.3.0",  # Data augmentation
    
    # Other dependencies from original requirements
    "ftfy~=6.1.0",
    "numpy==1.26.4",
    "pydantic==2.9.2",
    "smart_open~=6.4.0",
    "sentencepiece>=0.1.91,!=0.1.92",
    "triton~=2.2.0",
)

# Install specific diffusers commit for FLUX support
GIT_SHA = "2541d141d5ffa9c94a7e8f5ca7f4ada26bad811d"
image = (
    image.run_commands(
        "cd /root && git init .",
        "cd /root && git remote add origin https://github.com/huggingface/diffusers",
        f"cd /root && git fetch --depth=1 origin {GIT_SHA} && git checkout {GIT_SHA}",
        "cd /root && pip install -e .",  # Install diffusers in development mode
    )
)

# Configuration classes
@dataclass
class SharedConfig:
    """Base configuration shared across training and inference"""
    instance_name: str = "Bioicon"  # The concept we're teaching
    class_name: str = "style"       # Category of the concept
    model_name: str = "black-forest-labs/FLUX.1-dev"  # Base model


# Download base model weights
def download_models():
    """Pre-download the FLUX model to avoid downloading during training"""
    from diffusers import DiffusionPipeline
    from transformers.utils import move_cache

    config = SharedConfig()
    DiffusionPipeline.from_pretrained(config.model_name, force_download=True)
    move_cache()  # Move Hugging Face cache to proper location


image = image.run_function(
    download_models, 
    secrets=[modal.Secret.from_name("huggingface-secret")]
)

# Add web assets (HTML, CSS, JS)
assets_path = Path(__file__).parent / "assets"
web_image = image.add_local_dir(assets_path, remote_path="/assets")

# Persistent storage for trained models
volume = modal.Volume.from_name(
    "dreambooth-finetuning-volume-flux-hypersweep-heroicons-11-17",
    create_if_missing=True,
)
MODEL_DIR = "/model"  # Directory where models are stored

# Enable Weights & Biases for experiment tracking
USE_WANDB = True


@dataclass
class TrainConfig(SharedConfig):
    """Training configuration with hyperparameters"""
    dataset_name = "inescalvoesteva/bioicons-animal"  # Custom dataset
    caption_column = "text"  # Column with text descriptions
    instance_prompt = "a bioicon style illustration of"  # Training prompt template
    
    # Training hyperparameters
    resolution: int = 1024  # Image size
    train_batch_size: int = 1  # Batch size (limited by GPU memory)
    rank: int = 16  # LoRA rank (higher = more parameters)
    gradient_accumulation_steps: int = 1  # Simulate larger batch size
    learning_rate: float = 1e-4  # Initial learning rate
    lr_scheduler: str = "constant"  # Learning rate schedule
    lr_warmup_steps: int = 0  # Warmup steps
    max_train_steps: int = 1000  # Total training steps
    checkpointing_steps: int = 500  # Save checkpoint every N steps
    seed: int = 0  # Random seed for reproducibility


@dataclass
class SweepConfig(TrainConfig):
    """Configuration for hyperparameter sweep - test different combinations"""
    # Hyperparameters to sweep over
    learning_rates = [1e-4, 2e-4, 3e-4]
    train_steps = [1000, 1500, 3000, 4000]
    ranks = [8, 16, 32]

    # Test prompts for evaluating trained models
    bioicon_test_prompts = [
        "a bioicon style illustration of a jellyfish",
        "a bioicon style illustration of a dinosaur skull",
        "a bioicon style illustration of a neuron",
        "a bioicon style illustration of a virus particle",
        "a bioicon style illustration of a leaf cross section",
        "a bioicon style illustration of a snail",
        "a bioicon style illustration of a bat",
        "a bioicon style illustration of a protein",
        "a bioicon style illustration of a fungus",
        "a bioicon style illustration of a DNA",
        "a bioicon style illustration of a bacteri",
        "a bioicon style illustration of a bird",
        "a bioicon style illustration of a rat",
        "a bioicon style illustration of a laboratory flask",
        "a bioicon style illustration of a butterfly",
    ]


def generate_sweep_configs(sweep_config: SweepConfig):
    """Generate all combinations of hyperparameters for the sweep"""
    param_combinations = itertools.product(
        sweep_config.learning_rates,
        sweep_config.train_steps,
        sweep_config.ranks,
    )

    return [
        {
            "learning_rate": lr,
            "max_train_steps": steps,
            "rank": rank,
            "model_name": sweep_config.model_name,
            "instance_prompt": sweep_config.instance_prompt,
            "dataset_name": sweep_config.dataset_name,
            "caption_column": sweep_config.caption_column,
            "resolution": sweep_config.resolution,
            "train_batch_size": sweep_config.train_batch_size,
            "gradient_accumulation_steps": sweep_config.gradient_accumulation_steps,
            "lr_scheduler": sweep_config.lr_scheduler,
            "lr_warmup_steps": sweep_config.lr_warmup_steps,
            "checkpointing_steps": sweep_config.checkpointing_steps,
            "seed": sweep_config.seed,
            "output_dir": Path(MODEL_DIR) / f"lr_{lr}_steps_{steps}_rank_{rank}",
        }
        for lr, steps, rank in param_combinations
    ]


@app.function(
    image=image,
    gpu="A100-80GB",  # Requires high-memory GPU
    volumes={MODEL_DIR: volume},  # Save trained models to volume
    timeout=7200,  # 2 hour timeout
    secrets=[
        modal.Secret.from_name("wandb"),
        modal.Secret.from_name("huggingface-secret"),
    ] if USE_WANDB else [modal.Secret.from_name("huggingface-secret")],
)
def train(config):
    """Fine-tune FLUX model using LoRA on bioicons dataset"""
    import subprocess
    from accelerate.utils import write_basic_config

    # Configure accelerate for mixed precision training
    write_basic_config(mixed_precision="bf16")

    def _exec_subprocess(cmd: list[str]):
        """Run command and stream output in real-time"""
        print(f"Running: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        
        # Stream output
        with process.stdout as pipe:
            for line in iter(pipe.readline, ""):
                print(line.strip())
        
        if process.wait() != 0:
            raise subprocess.CalledProcessError(process.returncode, cmd)

    # Run training script from diffusers
    _exec_subprocess([
        "accelerate", "launch",
        "/root/examples/dreambooth/train_dreambooth_lora_flux.py",
        "--mixed_precision=bf16",
        f"--pretrained_model_name_or_path={config['model_name']}",
        f"--dataset_name={config['dataset_name']}",
        f"--caption_column={config['caption_column']}",
        f"--output_dir={config['output_dir']}",
        f"--instance_prompt={config['instance_prompt']}",
        # Prior preservation helps prevent overfitting
        "--with_prior_preservation",
        "--class_prompt=a style illustration of",
        "--num_class_images=200",
        "--prior_loss_weight=1.0",
        f"--resolution={config['resolution']}",
        f"--train_batch_size={config['train_batch_size']}",
        f"--gradient_accumulation_steps={config['gradient_accumulation_steps']}",
        f"--learning_rate={config['learning_rate']}",
        f"--lr_scheduler={config['lr_scheduler']}",
        f"--lr_warmup_steps={config['lr_warmup_steps']}",
        f"--max_train_steps={config['max_train_steps']}",
        f"--checkpointing_steps={config['checkpointing_steps']}",
        f"--rank={config['rank']}",
        f"--seed={config['seed']}",
        "--enable_xformers_memory_efficient_attention",  # Memory optimization
        *(["--report_to=wandb"] if USE_WANDB else []),
    ])
    
    # Persist trained model to volume
    volume.commit()
    return config


@app.cls(image=image, gpu="A100", volumes={MODEL_DIR: volume})
class Model:
    """Inference class for generating images with trained model"""
    hyperparameter_model_dir: str = modal.parameter()  # Which trained model to use

    @modal.enter()
    def load_model(self):
        """Load base model and LoRA weights"""
        import torch
        from diffusers import DiffusionPipeline

        # Ensure we have latest model from volume
        volume.reload()
        
        # Load base FLUX model
        pipe = DiffusionPipeline.from_pretrained(
            "black-forest-labs/FLUX.1-dev",
            torch_dtype=torch.bfloat16,
        ).to("cuda")
        
        # Load fine-tuned LoRA weights
        lora_path = Path(MODEL_DIR) / self.hyperparameter_model_dir
        if lora_path.exists():
            pipe.load_lora_weights(str(lora_path))
            print(f"Loaded LoRA from {lora_path}")
        
        self.pipe = pipe

    @modal.method()
    def inference(self, text, num_inference_steps=25):
        """Generate image from text prompt"""
        image = self.pipe(
            text,
            num_inference_steps=num_inference_steps,
        ).images[0]

        # Save generated image
        output_path = Path(MODEL_DIR) / "inference_outputs"
        output_path.mkdir(parents=True, exist_ok=True)
        filename = f"{text.replace(' ', '_').replace('/', '_')[:50]}.png"
        image.save(output_path / filename)
        
        return image, text


# Web app configuration
@dataclass
class AppConfig:
    num_inference_steps: int = 25  # More steps = better quality
    guidance_scale: float = 6      # How closely to follow prompt


@app.function(image=web_image, max_containers=1)
@modal.asgi_app()
def fastapi_app():
    """Deploy Gradio web interface for interactive image generation"""
    import gradio as gr
    from gradio.routes import mount_gradio_app
    
    config = AppConfig()
    
    # Example prompts for the web interface
    example_prompts = [
        "A bioicon style illustration of a cat with rainbow-colored stripes",
        "A bioicon style illustration of a shark riding a skateboard",
        "A bioicon style illustration of a rabbit with glowing eyes in a futuristic cyberpunk forest",
        "A bioicon style illustration of a raccoon playing a tiny grand piano",
    ]
    
    def generate_image(prompt):
        """Generate image from prompt using trained model"""
        if not prompt:
            prompt = example_prompts[0]
        
        # Use specific trained model (adjust as needed)
        model_dir = "lr_0.0001_steps_1000_rank_16"
        
        try:
            image, _ = Model(
                hyperparameter_model_dir=model_dir
            ).inference.remote(prompt, config.num_inference_steps)
            return image
        except Exception as e:
            print(f"Generation error: {e}")
            return None
    
    # Build Gradio interface
    with gr.Blocks(title="Bioicons Dreambooth on Modal") as interface:
        gr.Markdown("# Generate Bioicon-style Illustrations")
        
        with gr.Row():
            prompt_input = gr.Textbox(
                label="Prompt",
                placeholder="Describe your bioicon illustration...",
                lines=3,
            )
            output_image = gr.Image(
                height=1024, width=1024, label="Generated Image"
            )
        
        with gr.Row():
            generate_btn = gr.Button("Generate", variant="primary")
            generate_btn.click(generate_image, inputs=prompt_input, outputs=output_image)
        
        # Example buttons
        with gr.Column():
            for prompt in example_prompts:
                btn = gr.Button(prompt, variant="secondary")
                btn.click(lambda p=prompt: p, outputs=prompt_input)
    
    return mount_gradio_app(app=web_app, blocks=interface, path="/")


@app.local_entrypoint()
def run(max_train_steps: int = 250):
    """Main entrypoint: run hyperparameter sweep and evaluate models"""
    import wandb
    
    sweep_config = SweepConfig()
    app_config = AppConfig()
    
    # Generate all hyperparameter combinations
    configs = generate_sweep_configs(sweep_config)
    
    # Filter for specific experiments (e.g., only 1e-4 learning rate)
    filtered_configs = [c for c in configs if c["learning_rate"] == 1e-4]
    
    print(f"Training {len(filtered_configs)} model variants...")
    
    # Initialize experiment tracking
    with wandb.init(
        project="flux-lora-sweep-bioicons",
        name="bioicons_sweep",
    ) as run:
        
        # Train each configuration
        for config in train.map(filtered_configs):
            print(f"Trained: {config['output_dir']}")
            
            # Test the trained model
            model_dir = f"lr_{config['learning_rate']}_steps_{config['max_train_steps']}_rank_{config['rank']}"
            results = {}
            
            # Generate test images
            for prompt in sweep_config.bioicon_test_prompts[:5]:  # Test subset
                try:
                    image, _ = Model(
                        hyperparameter_model_dir=model_dir
                    ).inference.remote(prompt, app_config.num_inference_steps)
                    results[prompt] = wandb.Image(image)
                except Exception as e:
                    print(f"Failed on {prompt}: {e}")
            
            # Log results to wandb
            if results:
                run.log({f"rank_{config['rank']}_steps_{config['max_train_steps']}": results})
    
    print("Hyperparameter sweep completed!")


if __name__ == "__main__":
    print("Bioicons FLUX training pipeline ready")
