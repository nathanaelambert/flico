import pandas as pd
from typing import List
import src.trainer.db as db
import src.server.db as server_db
import src.trainer.date as date
import src.utils.colors as c
import src.crawler as crawler
import geo_clustering
import geo_grouping
# import geo_mapillary

def cache_geo_images():
    print(f"{c.BLUE}Getting relevant geo pictures from the database...{c.RESET}")
    df = db.photo_relevant_geo()
    db.mark_photo(df)
    print(f"{c.BLUE}Found {len(df)} pictures.\n Caching them...{c.RESET}")
    df, cache = crawler.download_df_images(df)

def add_all():
    print(f"{c.BLUE}Getting all pictures from the database...{c.RESET}")
    all_pics = db.flickr_photo_id()
    print(f"{c.BLUE}Found {len(all_pics)} pictures.\n Preparing table...{c.RESET}")
    db.mark_photo(all_pics)

def add_geo():
    print(f"{c.BLUE}Getting all pictures with geo from the database...{c.RESET}")
    all_pics = db.photo_to_dbscan()
    print(f"{c.BLUE}Found {len(all_pics)} pictures.\n Preparing table...{c.RESET}")
    db.mark_photo(all_pics)



def geo_embedding():
    while True:    
        print(f"{c.BLUE}Looking for pics needing a clip embedding...{c.RESET}")
        need_clip = db.photo_to_embed_with_clip()
        print(f"{c.BLUE}Found {len(need_clip)} pictures. \n{c.RESET}")
        if len(need_clip) > 0:
            print(f"{c.BLUE} Generating embeddings...{c.RESET}")
            db.update_ml_photo(geo_clustering.embedding.clip(need_clip), 'clip_vect_224')
        else:
            break

def building_labeling():
    print(f"{c.BLUE}Looking for pics needing a building label...{c.RESET}")
    need_label = db.photo_to_label_as_building()
    print(f"{c.BLUE}Found {len(need_label)} pictures. \n Labeling buidings and non-buildings...{c.RESET}")
    labeled = geo_clustering.clustering.label_buildings(need_label)
    db.update_ml_photo(labeled, 'is_building')
    db.update_ml_photo(labeled, 'p_building')

def clustering():
    print(f"{c.BLUE}Deleting previous clusters{c.RESET}")
    db.rm_data_ml_photo('geo_cluster_id')
    print(f"{c.BLUE}Looking for pics needing geographical clustering...{c.RESET}")
    need_clustering = db.photo_to_dbscan()
    print(f"{c.BLUE}Found {len(need_clustering)} pictures. \n Clustering buildings of same geographical area (DBSCAN)...{c.RESET}")
    db.update_ml_photo(geo_clustering.clustering.cluster(need_clustering), 'geo_cluster_id')
    print(f"{c.BLUE}Looking for pics to group (same building together)...{c.RESET}")

def grouping():
    to_group = db.photo_to_group()
    print(f"{c.BLUE}Found {len(to_group)} pictures. \n Computing photogrametry matching between pictures...{c.RESET}")
    grouped = geo_grouping.grouping(to_group)
    db.update_ml_photo(grouped, 'geo_group_id')
    db.update_ml_photo(grouped, 'is_central')

def date_embedding():
    print(f"{c.BLUE}Looking for pics needing a siglip embedding...{c.RESET}")
    need_siglip = db.photo_to_embed_with_siglip()
    print(f"{c.BLUE}Found {len(need_siglip)} pictures. \n Generating embeddings...{c.RESET}")
    db.update_ml_photo(date.embedding.siglip(need_siglip), 'sig_lip_vect_n')


def _dating_training():
    valid_dates = date.processing.filter(db.flickr_photo())
    db.use_for_date(valid_dates)
    date_embedding()
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



def _predict_date_visual():
    db.mark_photo(photos)
    to_embedd = db.flickr_mlphoto_to_embed()
    date_embeddings = date.embedding.siglip(to_embedd)
    db.update_ml_photo(date_embeddings, 'sig_lip_vect_n')
    to_predict = db.flickr_photo_to_predict().merge(photos[['owner_nsid', 'id']], on= ['owner_nsid', 'id'], how='inner')
    date_predictions = date.regression.svr50_predictions(to_predict)
    db.update_ml_photo(date_predictions, 'reg_n_pred_date')

def _predict_date_description():
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


if __name__ == "__main__":    
    # geo_embedding()
    # building_labeling()
    # clustering()
    # add_all()
    # date_embedding()
    # grouping()

    # add_geo()
    # geo_embedding()
    cache_geo_images()



    # slow (loads millions of pics)
    #flickr_photos = db.flickr_photo()
    # db.rm_data_ml_photo('descr_pred_date')
    # predict_date_description()
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