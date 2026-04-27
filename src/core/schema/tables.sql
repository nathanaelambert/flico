\c "flickr_commons_metadata";

CREATE TABLE institution (
    nsid TEXT PRIMARY KEY,
    name TEXT,
    date_launch BIGINT, -- unix time
    website TEXT,
    license TEXT,
    flickr_page TEXT,
    --icon_server
    icon_farm INT,
    icon_server TEXT,

    -- TODO: --
    --status (sync level with flickr)
    downloaded INT, --number of pics in the db
    available INT,  --number of pics on flickr
    most_recent_upload BIGINT, --timestamp of the most recent entry in the db
    least_recent_upload BIGINT
);
--http://farm{icon_farm}.staticflickr.com/{icon_server}/buddyicons/{nsid}.jpg

CREATE TABLE license (
    id INT PRIMARY KEY,
    name TEXT,
    url TEXT
);

CREATE TABLE photo (
    PRIMARY KEY (owner_nsid, id),
    FOREIGN KEY (owner_nsid) REFERENCES institution(nsid),
    FOREIGN KEY (license_id) REFERENCES license(id),
    -- photo page at https://www.flickr.com/photos/{owner_nsid}/{id}
    id BIGINT,
    owner_nsid TEXT,
    secret TEXT,
    server INT,
    farm INT,
    title TEXT,
    is_public BOOLEAN,
    is_friend BOOLEAN,
    is_family BOOLEAN,
    --license
    license_id INT,
    --description
    description TEXT,
    --o_dims
    original_width INT,
    original_height INT,
    --date_upload
    date_upload BIGINT,          --unix timestamp (number of seconds since Jan 1st 1970 GMT.)
    --last_update
    last_update BIGINT,          --unix timestamp
    --date_taken
    date_taken TIMESTAMP,        --in owner time zone
    date_taken_granularity INT,  --"0": Y-m-d H:i:s, "4": Y-m, "6": Y, "8": Circa...
    date_taken_unknown BOOLEAN,
    --owner_name
    owner_name TEXT,
    --views
    views INT,
    --tags
    tags TEXT,
    --machine_tags
    machine_tags TEXT,
    --original_format
    original_secret TEXT,
    original_format TEXT,
    --geo
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    accuracy INT,               --"0": no geo data, "1": unprecise, "16":very precise            
    context INT,                --"0": not defined, "1": indoors, "2": outdoors
    --media
    media TEXT,
    media_status TEXT,
    --path_alias
    path_alias TEXT,            --??
    --url_sq
    url_sq TEXT,                --cropped 75px square
    height_sq INT,
    width_sq INT,
    --url_t
    url_t TEXT,                 --longest edge 100px
    height_t INT,
    width_t INT,
    --url_s
    url_s TEXT,                 --longest edge 240px
    height_s INT,
    width_s INT,
    --url_q
    url_q TEXT,                 --cropped 150px square
    height_q INT,
    width_q INT,
    --url_m
    url_m TEXT,                 --longest edge 240px
    height_m INT,
    width_m INT,
    --url_n
    url_n TEXT,                 --longest edge 320px
    height_n INT,
    
     INT,
    --url_z
    url_z TEXT,                 --longest edge 640px
    height_z INT,
    width_z INT,
    --url_c
    url_c TEXT,                 --longest edge 800px
    height_c INT,
    width_c INT,
    --url_l
    url_l TEXT,                 --longest edge 1024px
    height_l INT,
    width_l INT,
    --url_o
    url_o TEXT,                 --original dimensions
    height_o INT,
    width_o INT
);

CREATE TABLE machine_learning_photo (
    PRIMARY KEY (owner_nsid, id),
    FOREIGN KEY (owner_nsid, id) REFERENCES photo(owner_nsid, id),
    FOREIGN KEY (geo_cluster_id) REFERENCES geo_cluster(id),
    
    id BIGINT,
    owner_nsid TEXT,
    geo_cluster_id INT,
   
    is_test_set BOOLEAN,

    sig_lip_vect_n VECTOR(768), --embedding of 320px pic
    reg_n_pred_date INT, --date predicted by SVR 50 on latent space of siglip encoding with 320px input

    qwen3_pred_date INT, --date predicted by QWEN 3 with 320px input (for benchmarking image pipeline)

    descr_pred_date INT  --date predicted by NLP algo reading the text description

);

CREATE TABLE geo_cluster (
    id INT PRIMARY KEY,
    min_latitude DOUBLE PRECISION,
    avg_latitude DOUBLE PRECISION,
    max_latitude DOUBLE PRECISION,
    min_longitude DOUBLE PRECISION,
    avg_longitude DOUBLE PRECISION,
    max_longitude DOUBLE PRECISION
);

