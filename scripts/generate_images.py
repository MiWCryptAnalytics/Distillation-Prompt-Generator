import os
import json
import random
from pathlib import Path

def generate_images_for_taxonomy(taxonomy_data_path, output_dir, batch_output_file="batch_prompts.json"):
    """
    Generates a batch list of prompts for flux-gen-studio to process.
    """
    with open(taxonomy_data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    os.makedirs(output_dir, exist_ok=True)
    
    batch_prompts = []
    
    for domain in data.get("domains", []):
        for discipline in domain.get("disciplines", []):
            discipline_id = discipline["id"]
            discipline_name = discipline["name"]
            
            # The expected path for the image in the web app
            image_path = os.path.abspath(os.path.join(output_dir, f"{discipline_id}.jpg"))
            
            if os.path.exists(image_path):
                print(f"Image already exists for {discipline_name} ({discipline_id})")
                continue
                
            styles = [
                "cinematic lighting",
                "oil painting style",
                "hyper-realistic digital illustration",
                "detailed concept art",
                "soft studio lighting",
                "dramatic chiaroscuro",
                "vibrant watercolor",
                "vintage photograph style",
                "retro-futuristic illustration",
                "modern minimalist illustration"
            ]
            
            palettes = [
                "warm earthy tones",
                "cool blues and silver",
                "vibrant contrasting colors",
                "muted pastel colors",
                "rich jewel tones",
                "monochrome with a pop of bright color"
            ]
            
            compositions = [
                "over-the-shoulder shot",
                "wide angle environmental portrait",
                "close up on the hands and tools",
                "dramatic low angle",
                "bird's-eye view"
            ]
            
            style = random.choice(styles)
            palette = random.choice(palettes)
            comp = random.choice(compositions)
            
            concepts = discipline.get("concepts", [])
            # Select up to 3 concepts to keep the prompt under the 77 token limit
            concept_str = ", ".join(random.sample(concepts, min(3, len(concepts)))) if concepts else "specialized tools"

            # Create a concise prompt suitable for Flux (77 token limit)
            prompt = (
                f"Detailed illustration of '{discipline_name}'. A focused person actively working with: "
                f"{concept_str}. {style}, {palette}, {comp}."
            )
            
            batch_prompts.append({
                "output_path": image_path,
                "prompt": prompt
            })

    # Write the batch list to file
    with open(batch_output_file, 'w', encoding='utf-8') as f:
        json.dump(batch_prompts, f, indent=2)
        
    print(f"Successfully generated {len(batch_prompts)} prompts to {batch_output_file}.")
    print("You can now pass this file to flux-gen-studio to generate the images in batch!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate images for taxonomy disciplines.")
    parser.add_argument("--data", default="taxonomy-viz/public/taxonomy_data.json", help="Path to taxonomy_data.json")
    parser.add_argument("--output-dir", default="taxonomy-viz/public/images/disciplines", help="Directory to save images")
    parser.add_argument("--batch-file", default="batch_prompts.json", help="Path to output the batch JSON file")
    args = parser.parse_args()
    
    generate_images_for_taxonomy(args.data, args.output_dir, args.batch_file)
