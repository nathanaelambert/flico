# Flico : a Dataset for Dating Historical Pictures Based on Flickr Commons

Flico (from Flickr Commons) is a large-scale dataset of 1,893,415 historical images with year-level date annotations. The dataset was designed to support research in historical image dating, computer vision, digital humanities, and quantitative historical analysis. It substantially expands the temporal and visual diversity available in existing historical image datasets.

## Comparison of Flico with the DEW and DEW-B datasets

|                | **DEW (2017)**      | **DEW-B (2024)**         | **Flico (2026)**   |
| -------------- | ------------------- | ------------------------ | ------------------ |
| **Source**     | Flickr              | DEW, Europeana, LAION-5B | Flickr Commons     |
| **Access**     | Largely copyrighted | Largely copyrighted      | Open access        |
| **Type**       | Photographs         | Photographs              | Various types      |
| **Time frame** | 1930–1999           | 1930–1999                | 1000–2026          |
| **Filtering**  | Year as keyword     | Prediction model         | Prediction model   |
| **Correction** | None                | None                     | Textual extraction |
| **Size**       | 1,029,710           | 1,444,587                | 1,893,415          |

[DEW](https://research.uni-hannover.de/de/publications/when-was-this-picture-taken-image-date-estimation-in-the-wild) (Müller-Budack et al., 2017)

[DEW-B](https://link.springer.com/chapter/10.1007/978-3-031-56063-7_9) (Net et al., 2024)

[Flico](flico_master_thesis_n_lambert.pdf) See the report.

## Access
This dataset is acceccible as a Postgres database by contacting the author.
The database contains 4 tables. Tables `institution`, `license`, and `photo` are raw data extracted from [Flickr Commons](https://www.flickr.com/commons) via the Flickr [API](https://www.flickr.com/services/api/). Table `machine_learning_photo` contains computed fields relative to date correction, as well as pictures and embeddings, and fields relative to geographic data correction and building identification. See the related projects: https://github.com/Amine-Zouzou/final_version_flickr, https://github.com/ghassanbaroudi/flickr-filtering-db-integration, and https://github.com/kimoal276/flickr-project.

## Database content

### institution
| Field               | Type   | Description                                     |
| ------------------- | ------ | ----------------------------------------------- |
| nsid                | TEXT   | Flickr institution identifier (primary key)     |
| name                | TEXT   | Institution name                                |
| date_launch         | BIGINT | Institution launch date (Unix timestamp)        |
| website             | TEXT   | Institution website                             |
| license             | TEXT   | License information                             |
| flickr_page         | TEXT   | Flickr Commons page URL                         |
| icon_farm           | INT    | Flickr icon farm identifier                     |
| icon_server         | TEXT   | Flickr icon server identifier                   |
| downloaded          | INT    | Number of pictures downloaded into the database |
| available           | INT    | Number of pictures available on Flickr          |
| most_recent_upload  | BIGINT | Timestamp of most recent image in database      |
| least_recent_upload | BIGINT | Timestamp of oldest image in database           |

### license
| Field | Type | Description                      |
| ----- | ---- | -------------------------------- |
| id    | INT  | License identifier (primary key) |
| name  | TEXT | License name                     |
| url   | TEXT | License URL                      |

### photo
(id, owner_nsid) is primary key.

| Field                  | Type             | Description                                                                |
| ---------------------- | ---------------- | -------------------------------------------------------------------------- |
| id                     | BIGINT           | Flickr photo identifier                                                    |
| owner_nsid             | TEXT             | Institution identifier (foreign key to `institution`)                      |
| secret                 | TEXT             | Flickr secret token                                                        |
| server                 | INT              | Flickr server identifier                                                   |
| farm                   | INT              | Flickr farm identifier                                                     |
| title                  | TEXT             | Photo title                                                                |
| is_public              | BOOLEAN          | Whether the image is public                                                |
| is_friend              | BOOLEAN          | Whether visibility is restricted to friends                                |
| is_family              | BOOLEAN          | Whether visibility is restricted to family                                 |
| license_id             | INT              | License identifier (foreign key to `license`)                              |
| description            | TEXT             | Image description                                                          |
| original_width         | INT              | Original image width                                                       |
| original_height        | INT              | Original image height                                                      |
| date_upload            | BIGINT           | Upload date (Unix timestamp)                                               |
| last_update            | BIGINT           | Last metadata update timestamp                                             |
| date_taken             | TIMESTAMP        | Date image was taken (owner timezone) (*unreliable*)                       |
| date_taken_granularity | INT              | Precision of `date_taken` (`0`: second, `4`: month, `6`: year, `8`: circa) |
| date_taken_unknown     | BOOLEAN          | Whether the capture date is considered unknown (*unreliable*)              |
| owner_name             | TEXT             | Flickr owner display name                                                  |
| views                  | INT              | Number of views                                                            |
| tags                   | TEXT             | User-provided tags                                                         |
| machine_tags           | TEXT             | Flickr machine tags                                                        |
| original_secret        | TEXT             | Original file secret                                                       |
| original_format        | TEXT             | Original file format                                                       |
| latitude               | DOUBLE PRECISION | Latitude coordinate                                                        |
| longitude              | DOUBLE PRECISION | Longitude coordinate                                                       |
| accuracy               | INT              | Geographic precision (`0`: none, `16`: very precise) (*unreliable*)        |
| context                | INT              | Environment (`0`: unknown, `1`: indoors, `2`: outdoors)                    |
| media                  | TEXT             | Media type (photo, video, etc.)                                            |
| media_status           | TEXT             | Media processing status                                                    |
| path_alias             | TEXT             | Flickr path alias                                                          |
| url_sq                 | TEXT             | 75×75 cropped square image URL                                             |
| height_sq              | INT              | Height of square thumbnail                                                 |
| width_sq               | INT              | Width of square thumbnail                                                  |
| url_t                  | TEXT             | Thumbnail URL (100 px longest edge)                                        |
| height_t               | INT              | Thumbnail height                                                           |
| width_t                | INT              | Thumbnail width                                                            |
| url_s                  | TEXT             | Small image URL (240 px longest edge)                                      |
| height_s               | INT              | Small image height                                                         |
| width_s                | INT              | Small image width                                                          |
| url_q                  | TEXT             | 150×150 cropped square image URL                                           |
| height_q               | INT              | Square image height                                                        |
| width_q                | INT              | Square image width                                                         |
| url_m                  | TEXT             | Medium image URL (240 px longest edge)                                     |
| height_m               | INT              | Medium image height                                                        |
| width_m                | INT              | Medium image width                                                         |
| url_n                  | TEXT             | Image URL (320 px longest edge)                                            |
| height_n               | INT              | Height of 320 px image                                                     |
| width_n                | INT              | Width of 320 px image                                                      |
| url_z                  | TEXT             | Image URL (640 px longest edge)                                            |
| height_z               | INT              | Height of 640 px image                                                     |
| width_z                | INT              | Width of 640 px image                                                      |
| url_c                  | TEXT             | Image URL (800 px longest edge)                                            |
| height_c               | INT              | Height of 800 px image                                                     |
| width_c                | INT              | Width of 800 px image                                                      |
| url_l                  | TEXT             | Image URL (1024 px longest edge)                                           |
| height_l               | INT              | Height of 1024 px image                                                    |
| width_l                | INT              | Width of 1024 px image                                                     |
| url_o                  | TEXT             | Original-resolution image URL                                              |
| height_o               | INT              | Original image height                                                      |
| width_o                | INT              | Original image width                                                       |

### machine_learning_photo
(id, owner_nsid) is primary key and matches entries in `photo`.

| Field                   | Type             | Description                                                |
| ----------------------- | ---------------- | ---------------------------------------------------------- |
| id                      | BIGINT           | Photo identifier                                           |
| owner_nsid              | TEXT             | Institution identifier                                     |
| geo_cluster_id          | INT              | Geographic cluster identifier                              |
| is_building             | BOOLEAN          | Whether the image depicts a building                       |
| p_building              | DOUBLE PRECISION | Probability that the image depicts a building              |
| geo_group_id            | INT              | Geographic group identifier                                |
| is_central              | BOOLEAN          | Whether the image is the representative image of its group |
| mapillary_id            | BIGINT           | Matching Mapillary image identifier                        |
| p_match                 | DOUBLE PRECISION | Probability that Flickr and Mapillary images match         |
| mapillary_lon           | DOUBLE PRECISION | Longitude of matched Mapillary image                       |
| mapillary_lat           | DOUBLE PRECISION | Latitude of matched Mapillary image                        |
| mapillary_compass_angle | DOUBLE PRECISION | Camera orientation angle                                   |
| mapillary_captured_at   | BIGINT           | Capture timestamp of Mapillary image                       |
| mapillary_pic_url       | TEXT             | URL of matched Mapillary image                             |
| p_building_given_descr  | DOUBLE PRECISION | Building probability estimated from description text       |
| mapillary_candidates    | INT              | Number of nearby Mapillary candidates                      |
| sig_lip_vect_n          | VECTOR(768)      | SigLIP embedding of 320 px image                           |
| sig_lip_vect_o          | VECTOR(768)      | SigLIP embedding of original-resolution image              |
| clip_vect_224           | VECTOR(512)      | OpenCLIP embedding of cropped image                        |
| is_date_train           | BOOLEAN          | Used in visual date-prediction training set                |
| is_date_test            | BOOLEAN          | Used in visual date-prediction evaluation set              |
| reg_n_pred_date         | INT              | Date predicted by SVR model on SigLIP embeddings           |
| qwen3_pred_date         | INT              | Date predicted by Qwen3-VL                                 |
| descr_pred_date         | INT              | Best textual date prediction                               |
| descr_pred_date_1       | INT              | Second-best textual date prediction                        |
| descr_pred_date_2       | INT              | Third-best textual date prediction                         |
| p_descr_date            | DOUBLE PRECISION | Confidence of best textual prediction                      |
| p_descr_date_1          | DOUBLE PRECISION | Confidence of second-best prediction                       |
| p_descr_date_2          | DOUBLE PRECISION | Confidence of third-best prediction                        |
| human_pred_date         | INT              | Human-annotated year                                       |
| corrected_year          | INT              | Final corrected year after aggregation                     |
| is_slow_download        | BOOLEAN          | Whether image download was unusually slow                  |
