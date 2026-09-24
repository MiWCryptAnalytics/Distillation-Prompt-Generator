import os
import json
import re
from pathlib import Path

def parse_audits(audits_file):
    audits = []
    if not os.path.exists(audits_file):
        return audits
        
    with open(audits_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # Find table start
    in_table = False
    for line in lines:
        if line.strip().startswith('| Catalog |'):
            in_table = True
            continue
        if in_table and line.strip().startswith('|---'):
            continue
        if in_table and line.strip().startswith('|'):
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 4:
                audits.append({
                    "catalog": parts[0],
                    "type": parts[1],
                    "swept": parts[2],
                    "outcome": parts[3]
                })
        elif in_table and not line.strip():
            break
            
    return audits

def build_taxonomy_data(base_dir, output_file):
    taxonomy_path = Path(base_dir)
    data = {
        "catalogs": parse_audits(taxonomy_path / '_audits.md'),
        "domains": []
    }
    domain_map = {}

    for domain_dir in taxonomy_path.iterdir():
        if not domain_dir.is_dir() or domain_dir.name.startswith('_'):
            continue
            
        domain_id = domain_dir.name
        
        for discipline_file in domain_dir.glob('*.json'):
            if discipline_file.name.startswith('_'):
                continue
                
            with open(discipline_file, 'r', encoding='utf-8') as f:
                try:
                    disc_data = json.load(f)
                except json.JSONDecodeError:
                    print(f"Error parsing JSON in {discipline_file}")
                    continue
            
            domain_name = disc_data.get('domain', domain_id.replace('_', ' ').title())
            discipline_name = disc_data.get('discipline', discipline_file.stem.replace('_', ' ').title())
            concepts = disc_data.get('concepts', [])
            
            if domain_id not in domain_map:
                domain_obj = {
                    "id": domain_id,
                    "name": domain_name,
                    "disciplines": []
                }
                domain_map[domain_id] = domain_obj
                data["domains"].append(domain_obj)
            
            domain_map[domain_id]["disciplines"].append({
                "id": discipline_file.stem,
                "name": discipline_name,
                "concepts": concepts
            })
            
    # Sort domains and disciplines alphabetically for consistent rendering
    data["domains"].sort(key=lambda x: x["name"])
    for domain in data["domains"]:
        domain["disciplines"].sort(key=lambda x: x["name"])

    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"Successfully generated taxonomy data with {len(data['catalogs'])} catalogs and {len(data['domains'])} domains.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Build taxonomy JSON for visualization.")
    parser.add_argument("--taxonomy-dir", default="taxonomy", help="Path to taxonomy directory")
    parser.add_argument("--output", default="taxonomy-viz/public/taxonomy_data.json", help="Path to output JSON")
    args = parser.parse_args()
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    build_taxonomy_data(args.taxonomy_dir, args.output)
