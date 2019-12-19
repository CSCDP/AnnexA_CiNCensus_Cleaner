import logging
import re
import os
import pandas as pd
from fddc.regex import parse_regex

logger = logging.getLogger('spreadsheetcleaner')


# Functions to categorise data

def make_category(config):
    def categorize(series):
        for c in config:
            if series == c['code']:
                return c['code']
            elif c['code'] in str(series):
                return c['code']
            elif c['name'] in str(series):
                return c['code']

            for r in c.get('regex',[]):
                p = parse_regex(r)
                if p.match(str(series)) is not None:
                    return c['code']
                
        return 'not matched'
    return categorize

def make_map(original, new):
    '''
    Creates map of {original value:new value}
    '''
    values = dict(zip(original, new))
    return values



# Main function to go through spreadsheet and replace data

def clean(input_file, output_file, matching_report_file, data_config, **args):
    '''Replaces values in spreadsheet by standardized values following rules in data_config. 
    Saves clean spreadsheet in clean_path and matching report in matching_path'''
    
    # Set up writers to write both clean spreadsheet and matching report in unique spreadsheets
    writer_clean = pd.ExcelWriter(output_file, engine='xlsxwriter')
    writer_matching = pd.ExcelWriter(matching_report_file, engine='xlsxwriter')
    
    # Run through sheets within spreadsheet (matching items in data_config)
    for item in data_config:
        data = pd.read_excel(input_file, sheet_name=item)
        df = data.copy()
        settings = data_config[item]
        matching_report = pd.DataFrame(columns=['column', 'former_value', 'new_value'])
        logger.debug("Going through {}".format(item))
        
        # Run through config criteria for that sheet
        for c in settings:
            if df[df[c].notnull()].shape[0] > 0: # Only look at non-empty columns
                
                # Map current value to match value
                categorize = make_category(settings[c])
                df[c] = df[c].str.strip()
                unique = df[c].unique()
                clean_series = pd.Series(unique).apply(categorize).tolist()
                match = make_map(unique, clean_series)
                
                # Replace values in sheet
                df[c] = df[c].replace(match)
                
                # Log match of current loop into match_report
                match_report = pd.DataFrame({'former_value': list(match.keys()), 'new_value': list(match.values())})
                match_report['list'] = item
                match_report['column'] = c
                
                # Save match_report to global matching_report
                matching_report = pd.concat([matching_report, match_report])
                
        # Save cleaned sheet into excel sheet
        df.to_excel(writer_clean, sheet_name=item, index=False)
        
        # Re-order matching report and save to excel sheet
        matching_report = matching_report[['column', 'former_value', 'new_value']]
        matching_report.to_excel(writer_matching, sheet_name=item, index=False)
        logger.debug("{} finished".format(item))

    writer_clean.save()
    writer_matching.save()