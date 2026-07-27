import os
from PIL import Image

def optimize_images():
    src_dir = 'Photos'
    dest_dir = os.path.join('src', 'assets', 'images')
    
    if not os.path.exists(src_dir):
        print(f"⚠️ Le dossier source '{src_dir}' n'existe pas.")
        return
        
    os.makedirs(dest_dir, exist_ok=True)
    
    max_width = 1920
    
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                src_path = os.path.join(root, file)
                
                # Nom de fichier sans extension
                base_name = os.path.splitext(file)[0]
                dest_path = os.path.join(dest_dir, f"{base_name}.webp")
                
                # Skip if already exists
                if os.path.exists(dest_path):
                    continue
                
                try:
                    with Image.open(src_path) as img:
                        # Convert to RGB if necessary (e.g. PNG with alpha)
                        if img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")
                            
                        # Resize if larger than max_width
                        if img.width > max_width:
                            ratio = max_width / img.width
                            new_height = int(img.height * ratio)
                            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                            
                        # Save as WebP
                        img.save(dest_path, "WEBP", quality=80)
                        print(f"-> Optimisé : {file} -> {base_name}.webp")
                except Exception as e:
                    print(f"X Erreur avec {file}: {e}")

if __name__ == "__main__":
    optimize_images()
