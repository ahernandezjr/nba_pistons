import os, sys
import pandas as pd
import torch

from ..utils.config import settings
from ..utils.logger import getLogger


# Set configs from settings
DATA_DIR = settings.DATA_DIR
DATA_FILE_NAME = settings.DATA_FILE_NAME
DATA_FILE_5YEAR_NAME = settings.DATA_FILE_5YEAR_NAME
DATA_FILE_5YEAR_JSON_NAME = settings.DATA_FILE_5YEAR_JSON_NAME


# Create logger
logger = getLogger(__name__)


def extract_positions(df):
    """
    Clean the positions column in the given DataFrame.

    Args:
        df (pandas.DataFrame): The DataFrame containing the positions column.

    Returns:
        pandas.DataFrame: The DataFrame with the positions column cleaned.
    """
    logger.debug(f"Extracting positions...")

    df['positions'] = df['positions'].str.extract("<Position\.(.*): '.*'>", expand=False)

    logger.debug(f"Positions extracted: {df['positions'].unique()}")

    return df


def extract_team(df):
    """
    Cleans the 'team' column in the given DataFrame.

    Args:
        df (pandas.DataFrame): The DataFrame containing the 'team' column.

    Returns:
        df (pandas.DataFrame): The DataFrame with the 'team' column cleaned.
    """
    logger.debug(f"Extracting teams...")

    filtered_df = df.copy()

    filtered_df['team'] = filtered_df['team'].str.extract("Team\.(.*)", expand=False)
    
    logger.debug(f"Teams extracted: {filtered_df['team'].unique()}.")

    return df


def clean_columns(df):
    """
    Removes the 'is_combined_totals' column from the given DataFrame.

    Args:
        df (pandas.DataFrame): The DataFrame to clean.

    Returns:
        pandas.DataFrame: The cleaned DataFrame without the 'is_combined_totals' column.
    """
    logger.debug(f"Cleaning columns...")

    columns_to_drop = ['is_combined_totals']
    filtered_df = df.drop(columns=columns_to_drop)

    logger.debug(f"Cleaned columns: {columns_to_drop}.")

    return filtered_df


def clean_rows(df):
    """
    Clean the rows of a DataFrame by removing rows with missing values and duplicate values.
    
    Args:
        df (pandas.DataFrame): The DataFrame to be cleaned.
        
    Returns:
        pandas.DataFrame: The cleaned DataFrame.
    """
    logger.debug("Cleaning rows...")

    filtered_df= df.copy()

    # Remove rows with missing values
    filtered_df = filtered_df.dropna()
    
    # Remove rows with duplicate values
    filtered_df = filtered_df.drop_duplicates()

    return filtered_df


def filter_players_over_5_years(df):
    """
    Filters the given DataFrame to include only players who have played for more than 5 years.

    Args:
        df (pandas.DataFrame): The input DataFrame containing player data.

    Returns:
        pandas.DataFrame: The filtered DataFrame containing players who have played for more than 5 years.
    """
    logger.debug("Filtering players who have played for more than 5 years...")

    # Create a dictionary of players with a unique key of player id and a value of a list of their years played
    player_years_dict = df.groupby('slug')['Year'].apply(list).to_dict()

    # Remove a player from the dictionary if the player has played:
        # 1. for less than 5 years;
        # 2. during 2001, remove that player from the dictionary; and
        # 3. has continuous years (checks for a gap or trades).
    player_years_dict = {player : years for player, years in player_years_dict.items() if \
                          len(years) >= 5 and \
                          2001 not in years and \
                          list(range(years[0], years[len(years) - 1] + 1)) == years[0:len(years)]}

    # Filter the dataframe for players in the dictionary
    df_filtered = df[df['slug'].isin(player_years_dict.keys())]
    
    # Sort the DataFrame by player year and id
    df_filtered = df_filtered.sort_values(by=['slug', 'Year'])

    # For each player in the dataframe, keep only the first 5 years
    df_filtered = df_filtered.groupby('slug').head(5)

    return df_filtered


def filter_5Year_dataset(df):
    """
    Creates a dataset with player statistics for players who have played at least 5 years in the NBA.

    Args:
        df (pandas.DataFrame): The input dataframe containing player statistics.

    Returns:
        pandas.DataFrame: The filtered dataframe with player statistics for players who have played at least 5 years in the NBA.
        dict: A dictionary where the key is the player's slug and the value is a list of the player's statistics.
    """
    logger.debug("Filtering dataset for players who have played for more than 5 years...")

    df_filtered = df.copy()

    df_filtered = clean_rows(df_filtered)
    df_filtered = clean_columns(df_filtered)
    df_filtered = extract_positions(df_filtered)
    df_filtered = extract_team(df_filtered)
    df_filtered = filter_players_over_5_years(df_filtered)
    # df_filtered = filter_nontensor_values(df_filtered)

    # Create a dictionary where the key is the slug and the value is the rows of the filtered dataset
    df_dict = df_filtered.groupby('slug').apply(lambda x: x.to_dict(orient='records'))

    return df_filtered, df_dict


# TO BE IMPLEMENTED AT DEPTH IN FUTURE
def filter_nontensor_values(df):
    """
    Filters the given DataFrame to remove non-tensor values.

    Args:
        df (pandas.DataFrame): The input DataFrame.

    Returns:
        pandas.DataFrame: The filtered DataFrame.
    """
    logger.debug("Filtering non-tensor values...")

    # Convert values to proper types (i.e. str should be converted to int or float)
    df_filtered = df.apply(pd.to_numeric, errors='coerce')

    # Filter the DataFrame to remove non-tensor values
    df_filtered = df.select_dtypes(include=['number'])

    # TO DO: Implement further data cleaning steps here
        # One hot encoding for categorical values etc...

    return df_filtered


def print_summary(df, df_filtered):
    """
    Prints a summary of the given DataFrame and its filtered version.

    Parameters:
    - df (pandas.DataFrame): The original DataFrame.
    - df_filtered (pandas.DataFrame): The filtered DataFrame.

    Returns:
    None
    """
    logger.debug("Printing summary...")

    # Print the head of the filtered DataFrame
    print(df_filtered.head())

    # Print the number of entries and the number of unique players in the original dataframe
    print(f"Original DataFrame: Entries={len(df)}, Unique Players={len(df['slug'].unique())}")

    # Print the number of entries and the number of unique players in the filtered dataframe
    print(f"Filtered DataFrame: Entries={len(df_filtered)}, Unique Players={len(df_filtered['slug'].unique())}")


def save_df_and_dict(df, df_dict):
    """
    Saves the given DataFrame to a CSV file.

    Args:
        df (pandas.DataFrame): The DataFrame to save.
        filename (str): The name of the file to save the DataFrame to.

    Returns:
        None
    """
    logger.debug(f"Saving dataset to '{DATA_FILE_5YEAR_NAME}'...")

    # Create df filename
    # filename_df = os.path.join(DATA_DIR, f"{filename}.csv")
    # Create df_dict filename
    # filename_dict = filename_df = os.path.join(DATA_DIR, f"{filename}.json")


    # Save the filtered dataset and dictionary to a csv and json file
    df.to_csv(DATA_FILE_5YEAR_NAME, index=False)
    df_dict.to_json(DATA_FILE_5YEAR_JSON_NAME, indent=4)

    logger.debug(f"Filtered dataset saved to: '{DATA_FILE_5YEAR_NAME}'.")
    logger.debug(f"Filtered dictionary saved to: '{DATA_FILE_5YEAR_JSON_NAME}.json'.")


def run_processing():
    # Load the data
    df = pd.read_csv('data/nba_player_stats.csv')

    # Create a dataframe of players who have played for more than 5 years
    df_filtered, df_dict = filter_5Year_dataset(df)

    # Save the filtered dataframe and dictionary
    save_df_and_dict(df_filtered, df_dict)

    return df, df_filtered


if __name__ == '__main__':
    run_processing()    