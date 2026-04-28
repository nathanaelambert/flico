import pandas as pd
import pandera.pandas as pa
from pandera.typing import DataFrame
from typing import List
import src.trainer.db as db
import src.server.db as server_db
import src.core.schema as schema
import src.trainer.date as date
import src.trainer.geo as geo



def learn_to_date(flickr_photos: DataFrame[schema.Photo]):
    # DATE TRAINING PIPELINE
    #   initial filtering and sampling
    valid_dates = date.processing.filter(flickr_photos)
    db.use_for_date(valid_dates)
    #   embeddings
    # date_embeddings = date.embedding.siglip(src.core.db.view(flickr_photos, valid_dates))
    # db.update_column('sig_lip_vect_n')(date_embeddings)
    #   regression
    # TODO
    # store model somewhere
    #   prediction

def learn_to_locate(flickr_photos: DataFrame[schema.Photo]):
    # GEO PIPELINE
    #   initial filtering and sampling
    valid_geo = geo.processing.filter(flickr_photos)
    # db.use_for_geo(valid_geo)
    #   @Ghassan add pipeline steps
    #   clustering


def predict_date(photo: DataFrame[schema.Photo]) -> List[int]:
    pass

def predict_geo(photo: DataFrame[schema.Photo]) -> List[tuple[float, float]]:
    pass

if __name__ == "__main__":    
    # slow (loads millions of pics)
    flickr_photos = db.flickr_photo()
    learn_to_date(flickr_photos)

    db.rm_data_ml_photo('is_date_train')
    db.rm_data_ml_photo('is_date_test')
    # """
    # start the app
    # - shows status
    # - check flickr for updates
    # - download new pics

    # - load data
    # - filtered_status
    # - filter

    # """