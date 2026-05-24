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
    cache = crawler.PersistentImageCache("flickr_commons") 
    print(f"{c.BLUE}Getting relevant geo pictures from the database...{c.RESET}")
    df = db.photo_relevant_geo()
    db.mark_photo(df)
    print(f"{c.BLUE}Found {len(df)} pictures.\n Caching them...{c.RESET}")
    df = crawler.download_df_images(df, cache)

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

def fast_geo_pipeline():
    cache = crawler.PersistentImageCache("flickr_commons") 
    batch = 0
    while True:
        batch += 1  
        print(f"{c.BLUE}Looking for pics needing a clip embedding...{c.RESET}")
        need_clip = db.sample_500_photo_to_embed_with_clip()
        print(f"{c.BLUE}Sampled {len(need_clip)} pictures. \n{c.RESET}")
        if len(need_clip) <= 0:
            break
        print(f"{c.BLUE} Caching pictures{c.RESET} batch {batch}...")
        pics = crawler.download_df_images(need_clip, cache, download_missing=True, fast_cache=True)
        slow_df = (need_clip.merge(pics[['owner_nsid', 'id']], on=['owner_nsid', 'id'], how='left', indicator=True).query('_merge == "left_only"').drop(columns=['_merge']))
        slow_df['is_slow_download'] = True
        db.update_ml_photo(slow_df, 'is_slow_download')
        print(f"{c.BLUE} Generating embeddings for {len(pics)} pictures...{c.RESET}")
        with_clip = geo_clustering.embedding.clip(pics, cache)
        with_clip = with_clip[with_clip["clip_vect_224"].notna()]
        db.update_ml_photo(with_clip, 'clip_vect_224')
        print(f"{c.BLUE}Looking for pics needing a building label...{c.RESET}")
        need_label = with_clip[with_clip['is_building'].isna()]
        print(f"{c.BLUE}Found {len(need_label)} pictures. \n Labeling buidings and non-buildings...{c.RESET}")
        labeled = geo_clustering.clustering.label_buildings(need_label, cache)
        labeled = labeled[labeled["is_building"].notna()]
        db.update_ml_photo(labeled, 'is_building')
        db.update_ml_photo(labeled, 'p_building')
        cache.clear_ram()


def fast_missing_buildings():
    cache = crawler.PersistentImageCache("flickr_commons") 
    print(f"{c.BLUE}Looking for pics needing a building label...{c.RESET}")
    need_label = db.photo_to_label_as_building()
    print(f"{c.BLUE}Found {len(need_label)} pictures. \n{c.RESET}")
    if len(need_label) <= 0:
        return
    print(f"{c.BLUE} Getting pictures from cache {c.RESET}")
    pics = crawler.download_df_images(need_label, cache, download_missing=False, fast_cache=False)
    missed_df = (need_label.merge(pics[['owner_nsid', 'id']], on=['owner_nsid', 'id'], how='left', indicator=True).query('_merge == "left_only"').drop(columns=['_merge']))
    print(f"Cache missed: {c.RED} {len(missed_df)} {c.RESET} pictures")
    downloaded = crawler.download_df_images(missed_df, cache, download_missing=True, fast_cache=False)
    print(f"{c.BLUE}Found {len(downloaded)} pictures. \n Labeling buidings and non-buildings...{c.RESET}")
    labeled = geo_clustering.clustering.label_buildings(downloaded, cache)
    labeled = labeled[labeled["is_building"].notna()]
    db.update_ml_photo(labeled, 'is_building')
    db.update_ml_photo(labeled, 'p_building')
    cache.clear_ram()

# def per_cluster_pipeline():
    # print(f"{c.BLUE}Deleting previous clusters{c.RESET}")
    # print(f"{c.BLUE}Found {len(labeled)} pictures. \n Clustering buildings of same geographical area (DBSCAN)...{c.RESET}")
    # clusters = geo_clustering.clustering.cluster(labeled)
    # clusters = clusters[clusters['geo_cluster_id'].notna()]
    # db.update_ml_photo(clusters, 'geo_cluster_id')
    # print(f"{c.BLUE}Looking for pics to group (same building together)...{c.RESET}")
    # print(f"{c.BLUE}Found {len(clusters)} pictures. \n Computing photogrametry matching between pictures...{c.RESET}")
    # grouped = geo_grouping.grouping(clusters)
    # grouped = grouped[grouped['geo_group_id'].notna()]
    # db.update_ml_photo(grouped, 'geo_group_id')
    # db.update_ml_photo(grouped, 'is_central')
    # print(f"{c.BLUE}Matching {len(grouped)} pictures with mapillary candidates...{c.RESET}")
    # matched = geo_mapillary.find_matches(grouped)


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

def grouping():
    cache = crawler.PersistentImageCache("flickr_commons") 
    print(f"{c.BLUE}Looking for pics to group (same building together)...{c.RESET}")
    to_group = db.photo_to_group()
    print(f"{c.BLUE}Found {len(to_group)} pictures.{c.RESET}")
    pics = crawler.download_df_images(to_group, cache, download_missing=True, fast_cache=False)
    print(f"{c.BLUE}Downloaded {len(pics)} pictures. \n Computing photogrametry matching between pictures...{c.RESET}")
    grouped = geo_grouping.grouping(pics)
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
    clustering()
    # add_all()
    # date_embedding()
    # grouping()

    # add_geo()
    # geo_embedding()
    # cache_geo_images()
    # fast_missing_buildings()



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