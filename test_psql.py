import psycopg2
import sys, os
import numpy as np
import pandas as pd
import example_psql as creds
import pandas.io.sql as psql

conn_string = "host="+ creds.HOST +" port="+ "5432" +" dbname="+ creds.DATABASE +" user=" + creds.USER \
+" password="+ creds.PASSWORD

conn=psycopg2.connect(conn_string)
conn.autocommit = True
print("Connected!")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS ads;")

conn.commit()

create_table_sql = """CREATE TABLE IF NOT EXISTS ads(
  ad_id serial PRIMARY KEY,
  username TEXT, 
  user_behavior TEXT,
  video_title TEXT,
  video_length_seconds TEXT,
  num_ads SMALLINT,
  skippable BOOLEAN,
  ad_length_seconds INT,
  advertiser TEXT,
  ad_type TEXT,
  logged_in BOOLEAN,
  time_logged TIMESTAMP
);"""
cursor.execute(create_table_sql)

# cursor.execute("ALTER TABLE ads RENAME COLUMN num_ads TO num_initial_ads;")

# cursor.execute("DELETE FROM ads")
# conn.commit()

# cursor.execute("ALTER TABLE ads ADD COLUMN logged_in BOOLEAN;")

ad_entry = ['jcurl', 'always skip', 'cute rabbit video', 13219, 2, True, 120, 'expedia.com', 'OVERLAY', True]

def upload_data(ad_entry, cursor):
    
    insert_statement = """
    INSERT INTO ads(username, user_behavior, video_title, video_length_seconds, num_ads, skippable, ad_length_seconds, advertiser, ad_type, logged_in, time_logged)
    VALUES ('{}', '{}', '{}', {}, {}, {}, {}, '{}', '{}', {}, CURRENT_TIMESTAMP);
    """.format(ad_entry[0], ad_entry[1], ad_entry[2], ad_entry[3], ad_entry[4], ad_entry[5], ad_entry[6], ad_entry[7], ad_entry[8], ad_entry[9])

    cursor.execute(insert_statement)

# upload_data(ad_entry, cursor)

cursor.close()
conn.close()
