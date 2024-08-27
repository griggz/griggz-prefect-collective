from typing import Dict, List, Union

import pandas as pd


def d_effer(
    source: Union[str, pd.DataFrame, dict, List[Dict]] = None, columns: List[str] = None
):
    df_ = None

    # Check if the source is a path to a CSV file (assuming a string is a file path)
    if isinstance(source, str):
        try:
            df_ = pd.read_csv(source)
        except Exception as exc:
            raise ValueError(f"Error reading CSV file: {exc}") from exc

    # Check if the source is a DataFrame
    elif isinstance(source, pd.DataFrame):
        if source.empty:
            raise ValueError("The provided DataFrame is empty")
        df_ = source.copy()

    # Check if the source is a dictionary
    elif isinstance(source, dict):
        df_ = pd.json_normalize(source, sep="_").fillna("")

    # Check if the source is an array of dictionaries
    elif isinstance(source, list) and all(isinstance(item, dict) for item in source):
        df_ = pd.DataFrame(source)

    # Raise an error if the source is none of the expected types
    else:
        if columns:
            df_ = pd.DataFrame(columns=columns)
        else:
            raise TypeError(
                """The source must be a file path, DataFrame, dictionary, a list of dictionaries or you must
                provide an array of columns to create an empty dataframe"""
            )

    # Clean DataFrame columns
    df_.columns = df_.columns.str.strip().str.replace(" ", "_").str.lower()

    # Remove NaNs
    df_.fillna("", inplace=True)

    return df_


def object_exists(obj, field, path=[]):
    """
    Checks if a given nested object (dictionary) has a specified field with a non-None value.

    :param obj: The object to check (dictionary).
    :param path: List of keys defining the path to the field's location.
    :param field: The field name to check for a non-None value.
    :return: True if field exists and has a non-None value, False otherwise.

    example:
    path_to_check = ['admin', 'user']
    field_to_check = 'id'
    """
    # Validate input is a dictionary
    if not isinstance(obj, dict):
        return False

    # Navigate the path to locate the field
    current_location = obj
    for key in path:
        if isinstance(current_location, dict) and key in current_location:
            current_location = current_location[key]
        else:
            return False  # Path is invalid

    # Check if the final field exists and has a non-None value
    return (
        isinstance(current_location, dict)
        and field in current_location
        and current_location[field] is not None
    )
