import pandas as pd
import re

def build_log(annexa, cin, output_file, config):
    
    # Tidy up dataframes independently
    
    if cin is not None:
        # Align CIN Census columns to Annex A
        cin.rename(columns=config['cin_to_annexa_cols'], inplace=True)
        # Add a source column to remember where the data came from
        cin['Source'] = 'CIN'
        # Rename CUID
        cin.rename(columns={'Child Unique ID':'CUID'}, inplace=True)
    
    if annexa is not None:
        # Align Annex A content to CIN Census codes
        content = config['annexa_to_cin_content']
        for col in content:
            value_map = {}
            unique = annexa[col].unique()
            if 'regex' in content[col]:
                for value in unique:
                    if isinstance(value, str):
                        new_value = re.findall(content[col]['regex'], value)
                        if len(new_value)>0:
                            value_map[value] = new_value[0]
                annexa[col] = annexa[col].replace(value_map)
            else:
                annexa[col] = annexa[col].replace(content[col])
        # Add a source column to remember where the data came from
        annexa['Source'] = 'AA'
        # Rename CUID
        annexa.rename(columns={'Child Unique ID':'CUID'}, inplace=True)
    
    
    # Create master log file
    
    if cin is not None and annexa is not None:
        # Concatenate both dataframes
        log = pd.concat([cin, annexa], sort=False)

    elif annexa is None:
        log = cin.copy()
        
    elif cin is None:
        log = annexa.copy()
        
    # Re-arrange columns
    firstcols = ['CUID', 'Date', 'Type', 'Source']
    newcols = firstcols + [col for col in list(log.columns) if col not in firstcols]
    log = log[newcols]
    
    log.to_csv(output_file, index=False)
    print('Done!')
    return log