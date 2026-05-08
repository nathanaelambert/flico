import pandas as pd


def vision_and_keywords(df: pd.DataFrame) -> pd.DataFrame:
    """
    Assign pictures to a cluster id
    input df: columns from photo, and some columns from machine_learning_photo
    output df: the same columns and geo_cluster_id

    """

def metadata(df: pd.DataFrame)-> pd.DataFrame:
    """
    Computes metrics on each cluster
    imput df: columns from photo and machine_learning_photo, including geo_cluster_id
    output_df: columns (id INT PRIMARY KEY,
                        min_latitude DOUBLE PRECISION,
                        avg_latitude DOUBLE PRECISION,
                        max_latitude DOUBLE PRECISION,
                        min_longitude DOUBLE PRECISION,
                        avg_longitude DOUBLE PRECISION,
                        max_longitude DOUBLE PRECISION)
    """
    
