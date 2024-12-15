import pandas as pd
import re
from fuzzywuzzy import process

# Fuzzy matching function
def get_best_match(name, name_list, threshold=80):
    result = process.extractOne(name, name_list)
    best_match, score, _ = result  # Unpacking into 3 variables, ignoring the index
    if score >= threshold:
        return best_match
    return None

# Helper function to update Canvas grades based on DeltaMath scores
def update_grades(canvas_df, deltamath_df, canvas_columns_mapping):    
    # Loop through each row in deltamath_df using iterrows
    for index, row in deltamath_df.iterrows():
        deltamath_name = row['Student']

        # Check if the value is NaN
        if pd.isna(deltamath_name):
            # Handle NaN case (replace with empty string or placeholder)
            deltamath_df.at[index, 'Student'] = ""  # Or another placeholder value
        else:
            # Apply fuzzy matching to find the best match in canvas_df
            best_match = get_best_match(deltamath_name, canvas_df['Student'])
            if best_match:
                # Replace the deltamath_name with the matched canvas_name
                deltamath_df.at[index, 'Student'] = best_match

    # Step 3: Merge the DataFrames based on the updated 'Student' name in DeltaMath and Canvas
    updated_df = pd.merge(canvas_df, deltamath_df, on='Student', how='left')

    # Step 4: Identify homework columns with '_x' (Canvas) and '_y' (DeltaMath)
    homework_columns = [col for col in updated_df.columns if '_x' in col or '_y' in col]
    homework_base_names = set(re.sub(r'(_x|_y)$', '', col) for col in homework_columns)

    # Step 5: Loop through each base homework name and compare Canvas and DeltaMath scores
    for base_name in homework_base_names:
        col_x = f"{base_name}_x"  # Canvas homework column
        col_y = f"{base_name}_y"  # DeltaMath homework column

        # Step 6: Check if both Canvas and DeltaMath columns exist for this homework
        if col_x in updated_df.columns and col_y in updated_df.columns:

            # Step 7: Update Canvas score only if DeltaMath score is higher, unless Canvas score is "EX"
            for index, row in updated_df.iterrows():
                # Skip row if Canvas score is "EX"
                if row[col_x] == 'EX':
                    continue
                
                # Update Canvas score if DeltaMath score exists and is higher
                if pd.notna(row[col_y]) and row[col_y] > row[col_x]:  # Ensure DeltaMath score is valid and higher
                    updated_df.at[index, col_x] = row[col_y]  # Update Canvas score with DeltaMath score

    # Step 8: Remove DeltaMath (_y) columns from the DataFrame
    updated_df = updated_df.drop(columns=[col for col in updated_df.columns if col.endswith('_y')])

    # Step 9: Revert homework column names to original Canvas names
    reverted_columns = []
    for col in updated_df.columns:
        # Remove '_x' suffix from the column name
        clean_col = re.sub(r'(_x)$', '', col)

        # Step 10: If the cleaned column name is in the mapping, use the original Canvas name
        if clean_col in canvas_columns_mapping:
            reverted_columns.append(canvas_columns_mapping[clean_col])
        else:
            # Otherwise, keep the column name as is
            reverted_columns.append(col)

    # Step 11: Update the DataFrame's column names to the reverted names
    updated_df.columns = reverted_columns

    return updated_df
