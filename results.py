# results.py

import sqlalchemy
from db import engine
import pandas as pd
from config import gen_sql_task_b_query, gen_sql_task_a_query

def analyze_user_sessions(connection):

    # Read HTTP log data
    http_log_df = pd.read_sql("SELECT * FROM http_log", connection)

    # Read campaign-reward mapping data
    campaign_reward_df = pd.read_sql("SELECT * FROM reward_campaign_relationship", connection)

    # Ensure timestamp is in datetime format
    http_log_df['timestamp'] = pd.to_datetime(http_log_df['timestamp'])

    # Sort the DataFrame by user_id and timestamp
    http_log_df = http_log_df.sort_values(by=['user_id', 'timestamp'])

    # Calculate the difference between consecutive timestamps for each user
    http_log_df['prev_timestamp'] = http_log_df.groupby('user_id')['timestamp'].shift(1)
    http_log_df['time_diff'] = (http_log_df['timestamp'] - http_log_df['prev_timestamp']).dt.total_seconds()

    # Identify session boundaries (more than 5 minutes gap)
    http_log_df['session_boundary'] = (http_log_df['time_diff'] > 300) | (http_log_df['prev_timestamp'].isnull())

    # Assign session IDs by cumulatively summing the session boundaries
    http_log_df['session_id'] = http_log_df.groupby('user_id')['session_boundary'].cumsum()

    # Aggregate session data
    user_sessions_df = http_log_df.groupby(['user_id', 'session_id']).agg(
        session_start=('timestamp', 'min'),
        session_end=('timestamp', 'max'),
        campaigns=('http_path', lambda x: list(x[http_log_df['http_method'] == 'GET'].str.split('/').str[2].astype(int))),
        rewards_issued=('http_path', lambda x: list(x[http_log_df['http_method'] == 'POST'].str.split('/').str[2].astype(int)))
    ).reset_index()

    # Create a campaign-reward mapping dictionary
    campaign_reward_map = campaign_reward_df.groupby('campaign_id')['reward_id'].apply(list).to_dict()

    # Define a function to check if rewards are driven by campaign views
    def check_rewards(campaigns, rewards):
        if not rewards or not campaigns:
            return False
        
        # Flatten the list of rewards for easier comparison
        flattened_rewards = [str(reward) for reward in rewards]
        
        for campaign in campaigns:
            str_campaign = str(campaign)
            if str_campaign in campaign_reward_map:
                # Check if any reward in rewards matches the map for the campaign
                if any(str(reward) in campaign_reward_map[str_campaign] for reward in flattened_rewards):
                    return True
        return False

    # Apply the function to the user sessions DataFrame
    user_sessions_df['reward_driven_by_campaign_view'] = user_sessions_df.apply(
        lambda row: check_rewards(row['campaigns'], row['rewards_issued']), axis=1)
    user_sessions_df['reward_driven_by_campaign_view'] = user_sessions_df['reward_driven_by_campaign_view'].astype(bool)

    # return the user sessions report
    return user_sessions_df


def results():    
    # Execute the queries and load the results into pandas DataFrames    
    with engine.connect() as conn:
        # Results for SQL Tasks a and b
        SQL_TASK_A_RESULT = pd.read_sql_query(gen_sql_task_a_query(), con=conn)
        SQL_TASK_B_RESULT = pd.read_sql_query(gen_sql_task_b_query(), con=conn)
        # Results for HTTP Log Analyze Task
        HTTP_LOG_ANALYZE_TASK_RESULT = analyze_user_sessions(conn)

    # Display the results
    print("\nResult of SQL Task A:")
    print(SQL_TASK_A_RESULT)

    print("\nResult of SQL Task B:")
    print(SQL_TASK_B_RESULT)

    print("\nResult of HTTP Log Analyze Task:")
    print(HTTP_LOG_ANALYZE_TASK_RESULT)

    # Insert the results into the database, replacing if the table exists
    with engine.connect() as conn:
        SQL_TASK_A_RESULT.to_sql('sql_task_a_result', con=conn, if_exists='replace', index=False)
        SQL_TASK_B_RESULT.to_sql('sql_task_b_result', con=conn, if_exists='replace', index=False)
        HTTP_LOG_ANALYZE_TASK_RESULT.to_sql('http_log_analyze_task_result', con=conn, if_exists='replace', index=False, dtype={
        'rewards_issued': sqlalchemy.types.JSON(),
        'campaigns': sqlalchemy.types.JSON()})
        conn.commit()

if __name__ == "__main__":
    results()


