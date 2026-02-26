"""Data processing utilities for metadata CSV files."""

from pathlib import Path

class PictureTooltip:
    def __init__(self, id: int, institution:str, title: str, description: str, date_taken: str, date_uploaded: str, image_url: str):
        self.id = id,
        self.institution = institution,
        self.title = title
        self.description = description
        self.date_taken = date_taken
        self.date_uploaded = date_uploaded
        self.image_url = image_url

    def __repr__(self):
        return f"PictureTooltip(title={self.title!r}, image_url={self.image_url!r})"

class PicturePoint:
    def __init__(self, id: int, institution:str, longitude: float, lattitude: float):
        self.id =id,
        self.institution = institution,
        self.longitude = longitude,
        self.latitude = latitude
    
    def __repr__(self):
        return f"PicturePoint(id={self.id}, institution={self.institution!r}, longitude={self.longitude}, latitude={self.latitude})"

def get_institutions() -> list[str]:
    """
    Get list of institution names from metadata CSV filenames.
    
    Returns:
        List of strings like ["Médiathèques Valence Romans agglomération", ...]
    """
    metadata_dir = Path(__file__).parent.parent / "metadata"
    csv_files = list(metadata_dir.glob("*.csv"))
    
    # Extract names: remove .csv extension
    institutions = [f.stem for f in csv_files]
    
    return sorted(institutions)  # alphabetical for consistency

def get_picture_tooltip(pic: int, institutions: str) -> PictureTooltip:
    ##TODO
    

def get_pics_id_with_location(institution: str) -> list[PicturePoint]
    """
    Find all the pictures with non zero latitude and longitude
    for a given institution
    """
    ##TODO



