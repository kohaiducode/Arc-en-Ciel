import os
import glob
from PIL import Image

def optimize_images(source_dir, target_dir, max_width=1920, quality=80):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # Walk through the source directory
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                source_path = os.path.join(root, file)
                
                # Maintain subfolder structure
                rel_path = os.path.relpath(root, source_dir)
                dest_sub_dir = os.path.join(target_dir, rel_path)
                if not os.path.exists(dest_sub_dir):
                    os.makedirs(dest_sub_dir)
                
                # new file name
                filename_without_ext = os.path.splitext(file)[0]
                target_path = os.path.join(dest_sub_dir, f"{filename_without_ext}.webp")

                # If already exists and optimized, skip (basic check)
                if os.path.exists(target_path):
                    continue
                
                try:
                    with Image.open(source_path) as img:
                        # Convert to RGB if necessary (e.g. RGBA png to webp)
                        if img.mode in ('RGBA', 'P'):
                            img = img.convert('RGB')
                        
                        # Resize if too large
                        if img.width > max_width:
                            ratio = max_width / img.width
                            new_size = (max_width, int(img.height * ratio))
                            img = img.resize(new_size, Image.Resampling.LANCZOS)
                        
                        img.save(target_path, 'WEBP', quality=quality)
                        print(f"Optimized: {file} -> {target_path}")
                except Exception as e:
                    print(f"Error processing {file}: {e}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    photos_dir = os.path.join(base_dir, "Photos")
    assets_img_dir = os.path.join(base_dir, "docs", "assets", "img")
    
    print(f"Optimizing images from {photos_dir} to {assets_img_dir}...")
    optimize_images(photos_dir, assets_img_dir)
    print("Image optimization complete.")
