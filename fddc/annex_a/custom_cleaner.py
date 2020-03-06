import pandas as pd

# List of columns that cannot be duplicates
no_duplicates = {
    'List 1': ['Child Unique ID', 'Date of Contact', 'Contact Source'],
    'List 2': ['Child Unique ID', 'Assessment start date'],
    'List 3': ['Child Unique ID', 'Date of referral', 'Referral Source'],
    'List 4': ['Child Unique ID', 'Continuous Assessment Start Date'],
    'List 5': ['Child Unique ID', 'Strategy discussion initiating Section 47 Enquiry Start Date'],
    'List 6': ['Child Unique ID', 'CIN Start Date'],
    'List 7': ['Child Unique ID', 'Child Protection Plan Start Date'],
    'List 8': ['Child Unique ID', 'Date Started to be Looked After']
}


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
    
        # Only keep duplicates with the least null values
        data['null_values'] = data.isnull().sum(axis=1)
        data = data.sort_values('null_values')
        data.drop_duplicates(subset=no_duplicates[item], keep='first', inplace=True)
        data.drop(labels='null_values', axis=1, inplace=True)
        
        # Save cleaned sheet into excel sheet
        data.to_excel(writer_clean, sheet_name=item, index=False)
    
    # Save cleaned Annex A
    writer_clean.save()
    
    # Done
    print('Done!')