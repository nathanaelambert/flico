import pandas as pd
from typing import List
import src.trainer.db as db
import src.server.db as server_db
import src.trainer.date as date
import src.trainer.geo as geo



def learn_to_date(flickr_photos: pd.DataFrame):
    # DATE TRAINING PIPELINE

    #   initial filtering and sampling
    valid_dates = date.processing.filter(flickr_photos)
    db.use_for_date(valid_dates)

    # embeddings
    date_embeddings = date.embedding.siglip(db.flickr_mlphoto_to_embed())
    db.update_ml_photo(date_embeddings, 'sig_lip_vect_n')

    # benchmark
    # benchmark_predictions = date.benchmark.qwen3(db.flickr_mlphoto_with_date_pred())
    # db.update_ml_photo(benchmark_predictions, 'qwen3_pred_date')

    # regression (training)
    df = db.flickr_photo_to_predict()
    ## WARNING: UNTESTED
    date.regression.train_model(df.loc(df['is_date_train']), df.loc(df['is_date_test']))

    # regression (prediction)
    date_predictions = date.regression.svr50_predictions(df)
    db.update_ml_photo(date_predictions, 'reg_n_pred_date')

    

def learn_to_locate(flickr_photos: pd.DataFrame):
    # GEO PIPELINE
    #   initial filtering and sampling
    valid_geo = geo.processing.filter(flickr_photos)
    db.use_for_geo(valid_geo)
    # clustering images
    cluster_ids = geo.clustering.vision_and_keywords(db.flickr_photo_to_cluster())
    db.update_ml_photo(cluster_ids, 'geo_cluster_id')
    # aggregating clusters metadata
    clusters = geo.clustering.metadata(clusters_id)
    db.save_clusters(clusters)

def predict_date(photos: pd.DataFrame) -> List[int]:
    db.use_for_date(photos)
    to_embedd = db.flickr_mlphoto_to_embed().merge(photos[['owner_nsid', 'id']], on= ['owner_nsid', 'id'], how='inner')
    date_embeddings = date.embedding.siglip(to_embedd)
    db.update_ml_photo(date_embeddings, 'sig_lip_vect_n')
    to_predict = db.flickr_photo_to_predict().merge(photos[['owner_nsid', 'id']], on= ['owner_nsid', 'id'], how='inner')
    date_predictions = date.regression.svr50_predictions(to_predict)
    db.update_ml_photo(date_predictions, 'reg_n_pred_date')


def predict_geo(photo: pd.DataFrame) -> List[tuple[float, float]]:
    pass

if __name__ == "__main__":    
    # db.rm_data_ml_photo('is_date_train')
    # db.rm_data_ml_photo('is_date_test')


    # slow (loads millions of pics)
    flickr_photos = db.flickr_photo()
    predict_date(flickr_photos)
    # date.description.explore()
    
    # learn_to_date(flickr_photos)

    # """
    # start the app
    # - shows status
    # - check flickr for updates
    # - download new pics

    # - load data
    # - filtered_status
    # - filter

    # """