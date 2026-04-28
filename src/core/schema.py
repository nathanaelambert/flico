import pandas as pd
import pandera.pandas as pa
from pandera.typing import Series
from typing import List
import numpy as np
  

class MLPhoto(pa.DataFrameModel):
    owner_nsid: str
    id: int
    geo_cluster: int = pa.Field(nullable=True, coerce=True)
    is_test_set: bool = pa.Field(nullable=True)
    is_date_test: bool = pa.Field(nullable=True)
    is_date_train: bool = pa.Field(nullable=True)
    sig_lip_vect_n: List[float] = pa.Field(nullable=True, coerce=True)
    @pa.dataframe_check
    def check_siglip_length(cls, df):
        return df['sig_lip_vect_n'].dropna().apply(len).eq(768)

class PhotoId(pa.DataFrameModel):
    owner_nsid : str
    id : int
 
class Photo(pa.DataFrameModel):
    owner_nsid : str
    id : int
    secret : str
    server : int
    farm : int
    title : str
    is_public : bool
    is_friend : bool
    is_family : bool
    license_id : int
    description : str
    original_width : int
    original_height : int
    date_upload : int
    last_update : int
    date_taken : pd.Timestamp
    date_taken_granularity: int
    date_taken_unknown: bool
    owner_name: str 
    views: int
    tags: str
    machine_tags: str
    original_secret: str
    original_format: str  
    latitude: float
    longitude: float
    accuracy: int
    context: int
    media: str
    media_status: str
    path_alias: str             = pa.Field(nullable=True)
    url_sq: str
    height_sq: int
    width_sq: int
    url_t: str
    height_t: int
    width_t: int
    url_s: str
    height_s: int
    width_s: int
    url_q: str
    height_q: int
    width_q: int
    url_m: str                  = pa.Field(nullable=True)
    height_m: int               = pa.Field(nullable=True, coerce=True)
    width_m: int                = pa.Field(nullable=True, coerce=True)
    url_n: str
    height_n: int
    url_z: str                  = pa.Field(nullable=True)
    height_z: int               = pa.Field(nullable=True, coerce=True)
    width_z: int                = pa.Field(nullable=True, coerce=True)
    url_c: str                  = pa.Field(nullable=True)
    height_c: int               = pa.Field(nullable=True, coerce=True)
    width_c: int                = pa.Field(nullable=True, coerce=True)
    url_l: str                  = pa.Field(nullable=True)
    height_l: int               = pa.Field(nullable=True, coerce=True)
    width_l: int                = pa.Field(nullable=True, coerce=True)
    url_o: str
    height_o: int
    width_o: int