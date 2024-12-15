import pandas as pd
from file_processing import load_and_clean
from grade_updating import update_grades

canvas_test = '2024-11-29T2249_Grades-ALGEBRA_2-BALDUCCI.csv'
deltamath_test = 'Multiple-Assignments-(11-27-24).xlsx'
test_finalout = 'test_final.csv'

def process_grades(canvas_file, deltamath_file, final_output):
    # Load and clean the data
    canvas_df, deltamath_df, canvas_columns_mapping, first_row = load_and_clean(canvas_file, deltamath_file)

    # TESTING
    canvas_df.to_csv('canvas_test_df.csv')
    deltamath_df.to_excel('dm_test_df.xlsx')

    # Update the grades:
    updated_df = update_grades(canvas_df, deltamath_df, canvas_columns_mapping)

    # Add the original first row for updated_df to ensure compatibility
    first_row_df = pd.DataFrame([first_row])  # Convert the row into a DataFrame
    updated_df = pd.concat([first_row_df, updated_df], ignore_index=True)  # Concatenate and reset the index
    updated_df.to_csv(final_output)

process_grades(canvas_test, deltamath_test, test_finalout)

# TODO:
# Fix str comparing to float - Due to an issue in spreadsheets of 'points possible' and possibly more
# Use fuzzy matching for non-conventional student names (confirm it worked?)