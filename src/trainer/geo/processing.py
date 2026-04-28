import pandas as pd
import pandera.pandas as pa
from src.trainer.db import PhotoId
from src.server.db import Photo

def filter(photos: pa.typing.DataFrame[Photo]) -> pa.typing.DataFrame[PhotoId]:
    photos = photos[photos['accuracy'] != 0]
    return photos[['owner_nsid', 'id']]
