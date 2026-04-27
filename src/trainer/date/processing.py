import pandas as pd
import pandera.pandas as pa
from src.trainer.db import PhotoId
from src.server.db import Photo

def first_filter(photos: pa.typing.DataFrame[Photo]) -> pa.typing.DataFrame[PhotoId]:
    pass
    

