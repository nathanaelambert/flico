import pandas as pd
import os
from pathlib import Path

def aggregate_flickr_commons():
    # Get directory containing THIS script (analysis/processing/)
    script_dir = Path(__file__).parent
    # Navigate: processing/ -> analysis/ -> project root
    project_root = script_dir.parent.parent  
    metadata_dir = project_root / "metadata"
    output_dir = project_root / "metadata_combined"
    
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "flickr_commons_pictures.csv"
    
    all_dfs = []
    
    # Find all CSV files in metadata/
    csv_files = list(metadata_dir.glob("*.csv"))
    
    # Add institution column from filename
    for csv_file in csv_files:
        institution = csv_file.stem
        df = pd.read_csv(csv_file)
        df['institution'] = institution
        cols = ['institution', 'id', 'secret', 'title', 'description', 
                'date_taken', 'date_uploaded', 'latitude', 'longitude', 
                'comments', 'size', 'image_url', 'notes', 'tags']
        df = df[cols]
        all_dfs.append(df)
    
    # Concatenate all dataframes and saves
    combined_df = pd.concat(all_dfs, ignore_index=True)
    combined_df.to_csv(output_path, index=False)
    print(f"Aggregated {len(csv_files)} institutions into {output_path}")
    print(f"Total pictures: {len(combined_df)}")

if __name__ == "__main__":
    aggregate_flickr_commons()
