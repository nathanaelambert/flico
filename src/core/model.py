from sqlalchemy import (Table, Column, BigInteger, Text, Integer, Boolean, Float,
                        ForeignKeyConstraint, MetaData)
from pgvector.sqlalchemy import VECTOR

metadata = MetaData()

ml_photo_table = Table(
    "machine_learning_photo",
    metadata,
    
    Column("owner_nsid", Text, primary_key=True),
    Column("id", BigInteger, primary_key=True),
    Column("geo_cluster_id", Integer),
    Column("is_building", Boolean),
    Column("p_building", Float),

    Column("is_test_set", Boolean),  # deprecated ?

    Column("is_date_test", Boolean),
    Column("is_date_train", Boolean),

    Column("sig_lip_vect_n", VECTOR(768)),
    Column("sig_lip_vect_o", VECTOR(768)),
    Column("clip_vect_224", VECTOR(512)),

    Column("reg_n_pred_date", Integer),
    Column("qwen3_pred_date", Integer),
    Column("descr_pred_date", Integer),

    ForeignKeyConstraint(
        ["owner_nsid", "id"],
        ["photo.owner_nsid", "photo.id"]
    ),
    # ForeignKeyConstraint(
    #     ["geo_cluster_id"],
    #     ["geo_cluster.id"]
    # ),
)