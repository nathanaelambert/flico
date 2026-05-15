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

def predict_date_visual():
    db.mark_photo(photos)
    to_embedd = db.flickr_mlphoto_to_embed()
    date_embeddings = date.embedding.siglip(to_embedd)
    db.update_ml_photo(date_embeddings, 'sig_lip_vect_n')
    to_predict = db.flickr_photo_to_predict().merge(photos[['owner_nsid', 'id']], on= ['owner_nsid', 'id'], how='inner')
    date_predictions = date.regression.svr50_predictions(to_predict)
    db.update_ml_photo(date_predictions, 'reg_n_pred_date')

def predict_date_description():
    to_predict = db.flickr_mlphoto_with_date_pred()
    print(f"Predicting dates for {len(to_predict)} pictures.")
    predictions = date.description.predictions(to_predict)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.width', None)
    pd.set_option('display.expand_frame_repr', False)
    predictions['page'] = predictions.apply(lambda r : f"https://www.flickr.com/photos/{r['owner_nsid']}/{r['id']}", axis=1 )
    predictions['year'] = pd.to_datetime(predictions['date_taken'], errors='coerce').dt.year
    predictions["diff"] = (predictions["year"] - predictions["descr_pred_date"]).abs()
    predictions = predictions.sort_values("diff", ascending=False).drop(columns="diff")
    print(predictions[['reg_n_pred_date','descr_score', 'descr_pred_date', 'year', 'page']].head(50))
    predictions= predictions.dropna(subset=['descr_pred_date'])
    db.update_ml_photo(predictions, 'descr_pred_date')
    # db.mark_photo(to_predict)

def predict_geo(photo: pd.DataFrame) -> List[tuple[float, float]]:
    pass

if __name__ == "__main__":    


    # slow (loads millions of pics)
    #flickr_photos = db.flickr_photo()
    db.rm_data_ml_photo('descr_pred_date')
    predict_date_description()
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