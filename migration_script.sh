#!/bin/bash
source .env  

# This copies data from localhost to remote DB
# The column and table must exist on both schemas
TABLE='machine_learning_photo'
COLUMN='qwen3_pred_date'

PGPASSWORD="$LOCAL_PWDDEV" \
psql -h localhost -U dev -d flickr_commons_metadata -W -t -v TABLE="$TABLE" -v COLUMN="$COLUMN" -c "
SELECT 'UPDATE $TABLE SET $COLUMN = ''' || COALESCE($COLUMN::text, 'NULL') || ''' WHERE id = ' || id || ';'
FROM $TABLE WHERE $COLUMN IS NOT NULL;" | \
PGPASSWORD="$PWDAPP" \
psql -h flickr-dev.postgresql.dbaas.intranet.epfl.ch -U app -d app -v ON_ERROR_STOP=1