import pandas as pd

def custom_clean(input_file, input_matching, output_file, data_config, **args):
    '''
    Cleans the input_file based on changes in the input_matching report
    Outputs the results in output_file
    '''
    writer_clean = pd.ExcelWriter(output_file, engine='xlsxwriter') # create object to store clean data
    
    for item in data_config:
        # Load data and matching information for each list
        data = pd.read_excel(input_file, sheet_name=item)
        matching = pd.read_excel(input_matching, sheet_name=item)

        for col in data.columns: # Look at each column in our data
            if col in matching.column.unique(): # If the column exists in the matching report i.e. has matching information
                df = matching[matching.column == col]
                match = dict(zip(df.former_value, df.new_value)) # Create dict of matching values
                data[col] = data[col].replace(match)
    
        # Save cleaned sheet into excel sheet
        data.to_excel(writer_clean, sheet_name=item, index=False)
    
    # Save cleaned Annex A
    writer_clean.save()
    
    # Done
    print('Done!')