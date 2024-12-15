import pandas as pd
import re

# Function to extract all homework names of the pattern: "Homework #-#"
def extract_homework_key(hw_name):
    # Regular expression pattern to match Homework #-# (e.g., "Homework 2-3", "Homework 12-20")
    match = re.match(r"^Homework\s*\d+-\d+", hw_name)  # Match "Homework 1-2" or similar
    return match.group(0) if match else None  # Return the matched Homework #-# if valid, or None if not

def load_and_clean(canvas_file, deltamath_file):
    # Load the Canvas CSV file
    canvas_df = pd.read_csv(canvas_file)
    # Cut out the first row for later
    first_row = canvas_df.iloc[0]
    canvas_df = canvas_df.iloc[1:]

    # Load the DeltaMath Excel file
    deltamath_df = pd.read_excel(deltamath_file)

    # Clean blank cells (if any column contains blank, replace it with NaN)
    canvas_df.replace("", float("NaN"), inplace=True)
    deltamath_df.replace("", float("NaN"), inplace=True)

    # Combine DeltaMath names into one full name column (Last, First)
    deltamath_df['Student'] = deltamath_df['Last'] + ', ' + deltamath_df['First']

    # Standardize 'Student' columns to uppercase
    deltamath_df['Student'] = deltamath_df['Student'].str.upper()

    # Remove dashes and strip spaces from student names in both datasets
    deltamath_df['Student'] = deltamath_df['Student'].str.replace('-', ' ', regex=True).str.strip()
    canvas_df['Student'] = canvas_df['Student'].str.replace('-', ' ', regex=True).str.strip()

    # Initialize an empty mapping for Canvas column names
    canvas_columns_mapping = {}

    # Loop through all columns in the Canvas DataFrame
    for col in canvas_df.columns:
        # Check if the column name matches the "Homework #-#" pattern
        homework_key = extract_homework_key(col)

        if homework_key:
            # If the column matches the pattern, map the standardized key to the original column name
            canvas_columns_mapping[homework_key] = col
            
            # Update the column name to match the standardized homework name
            canvas_df.columns = [homework_key if c == col else c for c in canvas_df.columns]

    # Standardize homework names in DeltaMath DataFrame (same logic as Canvas)
    for col in deltamath_df.columns:
        homework_key = extract_homework_key(col)

        if homework_key:
            # Update the column name to match the standardized homework name
            deltamath_df.columns = [homework_key if c == col else c for c in deltamath_df.columns]

    # Divide all homework scores in DeltaMath by 10, to match with Canvas scoring
    dm_homework_columns = [col for col in deltamath_df.columns if extract_homework_key(col)]
    
    # First, identify the non-numeric cells ('EX')
    for col in dm_homework_columns:
        deltamath_df[col] = deltamath_df[col].apply(lambda x: x if isinstance(x, str) and x == "EX" else pd.to_numeric(x, errors='coerce'))
    
    # Now, safely divide the numeric scores by 10, replacing any 'EX' with NaN, which can be handled later
    deltamath_df[dm_homework_columns] = deltamath_df[dm_homework_columns].apply(pd.to_numeric, errors='coerce') / 10

    cv_homework_columns = [col for col in canvas_df.columns if extract_homework_key(col)]

    # Ensure Canvas homework columns are numeric as well, while keeping 'EX' values intact
    for col in cv_homework_columns:
        canvas_df[col] = canvas_df[col].apply(lambda x: x if isinstance(x, str) and x == "EX" else pd.to_numeric(x, errors='coerce'))

    # Replace NaN values in homework columns with 0 in the DeltaMath DataFrame (already done for Canvas)
    deltamath_df[dm_homework_columns] = deltamath_df[dm_homework_columns].fillna(0)

    # Keep only the required columns in Canvas (Student, IDs, Section, and valid Homework columns)
    canvas_df = canvas_df[['Student', 'ID', 'SIS User ID', 'SIS Login ID', 'Section'] + cv_homework_columns]  # Only columns with valid "Homework #-#" keys

    # Keep only the required columns in DeltaMath (Student, Class, and valid Homework columns)
    deltamath_df = deltamath_df[['Student', 'Class'] + dm_homework_columns]

    return canvas_df, deltamath_df, canvas_columns_mapping, first_row

