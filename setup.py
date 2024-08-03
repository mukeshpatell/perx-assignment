# setup.py

import pandas as pd
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from config import DataUrls
import models
from db import engine

# Functions to load csv files from remote URLs
def load_campaigns_data(url: str = DataUrls.CAMPAIGNS_DATA_URL) -> pd.DataFrame:
    df = pd.read_csv(url, encoding='utf-8', header=0, 
                names=models.Campaign.get_columns())
    return df

def load_reward_campaigns_data(url: str = DataUrls.REWARD_CAMPAIGNS_DATA_URL) -> pd.DataFrame:
    df = pd.read_csv(url, encoding='utf-8', header=0, 
                names=models.RewardCampaign.get_columns())
    return df

def load_reward_transactions_data(url: str = DataUrls.REWARD_TRANSACTIONS_DATA_URL) -> pd.DataFrame:
    df = pd.read_csv(url, encoding='utf-8', header=0, 
                names=models.RewardTransaction.get_columns())
    return df

def load_http_logs_data(url: str = DataUrls.HTTP_LOGS_DATA_URL) -> pd.DataFrame:
    df = pd.read_csv(url, sep=r'\s+', header=None, 
                names=['timestamp', 'http_method', 'http_path', 'user_id'])
    return df

def load_reward_campaign_relationships_data(url: str = DataUrls.REWARD_CAMPAIGN_RELATIONSHIPS_DATA_URL) -> pd.DataFrame:
    df = pd.read_csv(url, encoding='utf-8', header=0, 
                names=['campaign_id', 'reward_id'])
    return df

def setup():
    # Load data
    campaigns_data_df = load_campaigns_data()
    reward_campaigns_data_df = load_reward_campaigns_data()
    reward_transactions_data_df = load_reward_transactions_data()
    http_logs_data_df = load_http_logs_data()
    reward_campaign_relationships_data_df = load_reward_campaign_relationships_data()

    with engine.connect() as conn:
        # List of DataFrames and corresponding table names
        data_frames = [
            (campaigns_data_df, models.Campaign.get_table()),
            (reward_campaigns_data_df, models.RewardCampaign.get_table()),
            (reward_transactions_data_df, models.RewardTransaction.get_table()),
            (http_logs_data_df, models.HTTPLog.get_table()),
            (reward_campaign_relationships_data_df, models.RewardCampaignRelationship.get_table())
        ]
        
        for df, table_name in data_frames:
            try:
                # Truncate the tables (start with empty tables)
                conn.execute(text(f"TRUNCATE TABLE {table_name} CASCADE"))
                # Insert data into the table
                df.to_sql(table_name, con=conn, if_exists='append', index=False)
                print(f"Data loaded into table: {table_name}")
            except IntegrityError as e:
                print(f"IntegrityError occurred while loading data into table: {table_name}")
                print(f"Error details: {e}")
            except Exception as e:
                print(f"An error occurred while loading data into table: {table_name}")
                print(f"Error details: {e}")

        print('All data loading attempts completed.')
        print('Setup complete.')
        conn.commit()
