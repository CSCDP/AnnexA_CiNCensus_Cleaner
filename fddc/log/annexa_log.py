import pandas as pd

# We recommend including all of the events into the cin log: it is the default list included below in build_annexarecord
# You can edit if you only need certain events
def build_annexarecord(input_file, events = {'contact': {'List 1':'Date of Contact'},
                                             'early_help_assessment_start': {'List 2':'Assessment start date'},
                                             'early_help_assessment_completion': {'List 2':'Assessment completion date'},
                                             'referral': {'List 3':'Date of referral'},
                                             'assessment_start': {'List 4':'Continuous Assessment Start Date'},
                                             'assessment_end':{'List 4':'Continuous Assessment Date of Authorisation'},
                                             's47': {'List 5': 'Strategy discussion initiating Section 47 Enquiry Start Date'},
                                             'cin_start': {'List 6': 'CIN Start Date'},
                                             'cin_end': {'List 6': 'CIN Closure Date'},
                                             'cpp_start': {'List 7': 'Child Protection Plan Start Date'},
                                             'cpp_start': {'List 7': 'Child Protection Plan Start Date'},
                                             'lac_start': {'List 8': 'Date Started to be Looked After'},
                                             'lac_end': {'List 8': 'Date Ceased to be Looked After'}}): 

    # Create empty dataframe in which we'll drop our events
    df_list = []

    # Loop over our dictionary to populate the log
    for event in events:
        contents = events[event]
        list_number = list(contents.keys())[0]
        print('Loading {} from Annex A'.format(contents))
        date_column = contents[list_number]
        df = pd.read_excel(input_file, sheet_name=list_number)  
        df = df[df[date_column].notnull()]
        df['Type'] = event
        df['Date'] = df[date_column]
        df_list.append(df)
    annexarecord = pd.concat(df_list, sort=False)
    return annexarecord