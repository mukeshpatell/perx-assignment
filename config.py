# config.py

from dataclasses import dataclass
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class Config:
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "admin")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "admin123")
    PG_HOST: str = os.getenv("PG_HOST", "perx_test_db_container")
    PG_PORT: str = os.getenv("PG_PORT", "5432")
    PGDATA: str = os.getenv("PGDATA", "/var/lib/postgresql/data")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "perx_test_db")

@dataclass
class DataUrls:
    CAMPAIGNS_DATA_URL: str = (
        "https://media.githubusercontent.com/media/PerxTech/data-interview/master/data/campaign.csv"
    )
    REWARD_CAMPAIGNS_DATA_URL: str = (
        "https://media.githubusercontent.com/media/PerxTech/data-interview/master/data/reward_campaign.csv"
    )
    REWARD_TRANSACTIONS_DATA_URL: str = (
        "https://media.githubusercontent.com/media/PerxTech/data-interview/master/data/reward_transaction.csv"
    )
    HTTP_LOGS_DATA_URL: str = (
        "https://media.githubusercontent.com/media/PerxTech/data-interview/master/data/http_log.txt"
    )
    REWARD_CAMPAIGN_RELATIONSHIPS_DATA_URL: str = (
        "https://media.githubusercontent.com/media/PerxTech/data-interview/master/data/campaign_reward_mapping.csv"
    )



def gen_sql_task_a_query(start_date: str = '2019-08-01', end_date: str = '2019-08-30') -> str:
    SQL_TASK_A_QUERY = f"""
    WITH transactions_in_range AS (
        SELECT 
            rt.id,
            rt.reward_campaign_id,
            rt.updated_at AT TIME ZONE 'UTC' AS utc_time,
            rt.updated_at AT TIME ZONE 'UTC' AT TIME ZONE 'SGT' AS sgt_time,
            rc.campaign_id
        FROM reward_transaction rt
        JOIN reward_campaign rc ON rt.reward_campaign_id = rc.id
        WHERE rt.updated_at AT TIME ZONE 'UTC' AT TIME ZONE 'SGT' BETWEEN '{start_date}' AND '{end_date}'
    ),
    campaign_transactions AS (
        SELECT 
            tr.reward_campaign_id,
            c.name AS campaign_name,
            COUNT(tr.id) AS no_of_transactions,
            DATE_TRUNC('day', tr.sgt_time) AS date,
            DATE_TRUNC('hour', tr.sgt_time) AS time
        FROM transactions_in_range tr
        JOIN campaign c ON tr.campaign_id = c.id
        GROUP BY tr.reward_campaign_id, c.name, DATE_TRUNC('day', tr.sgt_time), DATE_TRUNC('hour', tr.sgt_time)
    ),
    max_transactions AS (
        SELECT 
            reward_campaign_id,
            MAX(no_of_transactions) AS max_transactions
        FROM campaign_transactions
        GROUP BY reward_campaign_id
    )
    SELECT 
        ct.campaign_name,
        ct.no_of_transactions,
        ct.date,
        ct.time
    FROM campaign_transactions ct
    JOIN max_transactions mt ON ct.reward_campaign_id = mt.reward_campaign_id AND ct.no_of_transactions = mt.max_transactions
    ORDER BY ct.no_of_transactions DESC;
    """
    return SQL_TASK_A_QUERY

def gen_sql_task_b_query()-> str:
    SQL_TASK_B_QUERY = """
    WITH weekly_counts AS (
        SELECT 
            rt.reward_campaign_id,
            rc.reward_name,
            DATE_TRUNC('week', rt.updated_at::timestamp) AS week_start,
            COUNT(*) AS total_redeemed
        FROM 
            reward_transaction rt
        JOIN
            reward_campaign rc
        ON
            rt.reward_campaign_id = rc.id
        WHERE 
            rt.status = 'redeemed'
        GROUP BY 
            rt.reward_campaign_id, 
            rc.reward_name,
            week_start
    ),

    weekly_counts_with_diff AS (
        SELECT 
            reward_campaign_id,
            reward_name,
            total_redeemed,
            week_start,
            LAG(total_redeemed) OVER (PARTITION BY reward_campaign_id ORDER BY week_start) AS prev_week_total_redeemed
        FROM 
            weekly_counts
    )

    SELECT
        reward_name AS "Reward Name",
        total_redeemed AS "Reward Redeemed Count",
        COALESCE(
            ROUND(
                ((total_redeemed - prev_week_total_redeemed) * 100.0) / NULLIF(prev_week_total_redeemed, 0), 2
            ), 
            0
        ) AS "Percentage Difference as per Previous Week",
        week_start AS "Week"
    FROM
        weekly_counts_with_diff
    ORDER BY
        reward_campaign_id,
        week_start;
    """
    return SQL_TASK_B_QUERY
