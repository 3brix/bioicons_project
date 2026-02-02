#using: https://modal.com/docs/reference/modal.Volume#batch_upload

from pathlib import Path
import modal

# define app
app = modal.App("bioicons-flux")

# define the volume
volume = modal.Volume.from_name("bioicons", create_if_missing=True)

LOCAL_DATASET = Path("static/png")

# @app.local_entrypoint() decorator
@app.local_entrypoint()
def main():
    if not LOCAL_DATASET.exists():
        print(f"Error: {LOCAL_DATASET} folder not found locally.")
        return

    print(f"Uploading files from {LOCAL_DATASET} to volume...")
    
    with volume.batch_upload() as batch:
        count = 0
        for file_path in LOCAL_DATASET.glob("*.*"):
            if file_path.suffix in {".png", ".txt"}:
                # put_file(local_path, remote_path)
                batch.put_file(file_path, file_path.name)
                count += 1
        
    print(f"Upload complete! {count} files uploaded to 'bioicons'.")

# CLI
# run: modal run upload_dataset.py
# sanity check: modal volume ls bioicons-animals
