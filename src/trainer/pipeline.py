import pandas as pd
from typing import List
from tqdm import tqdm
import src.trainer.db as db
import src.server.db as server_db
import src.trainer.date as date
import src.trainer.geo as geo
import src.utils.colors as c
import src.crawler as crawler
import geo_clustering
import geo_grouping
import geo_mapillary

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

def geo_description():
    db.rm_data_ml_photo("p_building_given_descr")
    geo.predict_is_building_given_descr()

def _fast_geo_pipeline():
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
        slow_df = (need_clip.merge(pics[['owner_nsid', 'id']], on=['owner_nsid', 'id'], 
            how='left', indicator=True).query('_merge == "left_only"').drop(columns=['_merge']))
        slow_df['is_slow_download'] = True
        db.update_ml_photo(slow_df, 'is_slow_download')
        print(f"{c.BLUE} Generating embeddings for {len(pics)} pictures...{c.RESET}")
        with_clip = geo_clustering.embedding.clip(pics, cache)
        with_clip = with_clip[with_clip["clip_vect_224"].notna()]
        db.update_ml_photo(with_clip, 'clip_vect_224')
        print(f"{c.BLUE}Looking for pics needing a building label...{c.RESET}")
        need_label = with_clip[with_clip['is_building'].isna()]
        filtered = geo_clustering.clustering._filter(need_label)
        print(f"{c.BLUE}Kept {len(filtered)} pictures from {len(need_label)}{c.RESET}")
        print(f"{c.BLUE}Labeling buidings and non-buildings...{c.RESET}")
        labeled = geo_clustering.clustering.label_buildings(filtered, cache)
        labeled = labeled[labeled["is_building"].notna()]
        db.update_ml_photo(labeled, 'is_building')
        db.update_ml_photo(labeled, 'p_building')
        cache.clear_ram()


def fast_missing_buildings(batch_size=500):
    cache = crawler.PersistentImageCache("flickr_commons") 
    print(f"{c.BLUE}Looking for pics needing a building label...{c.RESET}")
    need_label = db.photo_to_label_as_building()
    total = len(need_label)
    print(f"{c.BLUE}Found {total} pictures.\n{c.RESET}")
    if total == 0:
        return
    for batch_id, start in enumerate(range(0, total, batch_size), start=1):
        end = min(start + batch_size, total)
        batch_to_label = need_label.iloc[start:end]
        print(
            f"{c.BLUE}Caching pictures batch {batch_id} "
            f"({start:,}-{end:,} of {total:,})...{c.RESET}"
        )
        downloaded = crawler.download_df_images(batch_to_label, cache, download_missing=True,
            fast_cache=True, disk_save=True)
        print(f"{c.BLUE}Downloaded {len(downloaded)} pictures.{c.RESET}")
        filtered = geo_clustering.clustering._filter(downloaded)
        print(f"{c.BLUE}Kept {len(filtered)} pictures from {len(downloaded)}"
              f"\nLabeling buidings and non-buildings...{c.RESET}")
        labeled = geo_clustering.clustering.label_buildings(filtered, cache)
        labeled = labeled[labeled["is_building"].notna()]
        db.update_ml_photo(labeled, 'is_building')
        db.update_ml_photo(labeled, 'p_building')
        cache.clear_ram()

def fast_grouping(max_batch_size=500):
    cache = crawler.PersistentImageCache("flickr_commons") 
    print(f"{c.BLUE}Looking for pics to group (same building together)...{c.RESET}")
    clusters = db.photo_to_group()
    for cluster_id, df_cluster in clusters.groupby("geo_cluster_id"):
        print(f"{c.BLUE}Processing cluster {c.RESET}{cluster_id}")
        cached_pics = crawler.download_df_images(df_cluster, cache, download_missing=True, 
            fast_cache=len(df_cluster)<=max_batch_size, disk_save=True)
        grouped = geo_grouping.grouping(cached_pics, cache)
        grouped = grouped[grouped['geo_group_id'].notna()]
        db.update_ml_photo(grouped, 'geo_group_id')
        db.update_ml_photo(grouped, 'is_central')

def fast_mapillary():
    cache = crawler.PersistentImageCache("flickr_commons") 
    print(f"{c.BLUE}Looking for pics to match...{c.RESET}")
    clusters = db.photo_to_mapillary()
    sorted_clusters = clusters.sort_values(by="p_building_given_descr", ascending=False)
    for i in tqdm(range(len(sorted_clusters)), total=len(sorted_clusters), desc="Matching images", disable=False):
        df_with_one_row = sorted_clusters.iloc[[i]]
        try:
            matched = geo_mapillary.find_matches(df_with_one_row, cache)
        except:
            continues
        db.update_ml_photo(matched, 'mapillary_candidates')
        if "p_match" not in matched.columns:
            continue
        if matched["p_match"].isna().all():
            continue
        db.update_ml_photo(matched, 'mapillary_id')
        db.update_ml_photo(matched, 'p_match')
        db.update_ml_photo(matched, 'mapillary_lon')
        db.update_ml_photo(matched, 'mapillary_lat')
        db.update_ml_photo(matched, 'mapillary_captured_at')
        db.update_ml_photo(matched, 'mapillary_compass_angle')
        db.update_ml_photo(matched, 'mapillary_pic_url')

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
    cache = crawler.PersistentImageCache("flickr_commons") 
    print(f"{c.BLUE}Looking for pics needing a siglip embedding...{c.RESET}")
    need_siglip = db.photo_to_embed_with_siglip()
    print(f"{c.BLUE}Found {len(need_siglip)} pictures. \n Generating embeddings...{c.RESET}")
    date.siglip(need_siglip, cache)

    

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
    # add_all()
    # date_embedding()
    # grouping()

    # fast_geo_pipeline()
    # fast_missing_buildings()
    # clustering()
    # fast_grouping()

    # geo_description()
    fast_mapillary()
    # date.svr50_predictions()
    # date.context_predictions()
    # date.combined_predictions()
    # fast_missing_buildings()
    # add_geo()
    # geo_embedding()
    # cache_geo_images()
    # batch_buildings_label()

    # db.rm_data_ml_photo("geo_group_id")
    # db.rm_data_ml_photo("is_central")


    # slow (loads millions of pics)
    #flickr_photos = db.flickr_photo()
    # predict_date_description()
    # date.description.explore()
    
    # learn_to_date(flickr_photos)