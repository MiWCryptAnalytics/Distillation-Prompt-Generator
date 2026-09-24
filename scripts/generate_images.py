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
                "cyberpunk neon data streams",
                "ethereal bioluminescent web",
                "minimalist sacred geometry",
                "holographic 3d projection",
                "macro photography of glowing crystals",
                "intricate fractal mathematics",
                "fluid dynamic particle simulation",
                "starlight nebula clouds",
                "dark matter void with intense energy lines",
                "glassmorphism floating prisms"
            ]
            
            palettes = [
                "deep space blues and purples",
                "neon pink and cyan vaporwave",
                "emerald green and brilliant gold",
                "crimson, copper, and obsidian",
                "monochrome slate with electric silver highlights",
                "vibrant cosmic rainbow"
            ]
            
            compositions = [
                "centered symmetrical composition",
                "dynamic flowing curved lines",
                "orbiting spheres and scattered particles",
                "intricate interconnected network",
                "floating geometric monoliths"
            ]
            
            style = random.choice(styles)
            palette = random.choice(palettes)
            comp = random.choice(compositions)

            # Create a rich prompt suitable for Flux
            prompt = (
                f"A breathtaking, highly detailed abstract digital art representation of the academic discipline: "
                f"'{discipline_name}'. Visual theme: {style}. Color palette: {palette}. Composition: {comp}. "
                f"Deep space aesthetic, glowing accents, 4k resolution, masterpiece, trending on artstation, "
                f"conceptual art."
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
