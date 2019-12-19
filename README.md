# READ ME

Welcome!

This code was originally developed by Celine Gross, Chris Owens ans Kaj Siebert at Social Finance as part of a grant funded programme to support Local Authorities to collaborate on data analysis. The programme was called the ‘Front Door Data Collaboration’. It was supported financially by the Christie Foundation and Nesta (through the ‘What Worls Centre for Children’s Social Care’) and the LAs whose staff guided its development were Bracknell Forest, West Berkshire, Southampton, and Surrey. It also benefitted from advice from the National Performance and Information Managers Group.

We are happy to share this code hoping that other data analysts may benefit from a quick way to standardize Annex A to conduct more analysis. We will be sharing additional code to analyse Annex A soon - stay tuned!

You can find more info about Social Finance Digital Labs on our website: https://www.sfdl.org.uk/

# How to run this programme

To run this programme, you will need to have installed Python and created a conda environment aligned with requirements.txt.

Once that is done, follow the steps detailed below:
1. Create a local configuration file
2. Run the 10-MERGE step
3. Run the 20-CLEAN step

You're done!

## Step 1: Create a local configuration file

You will need to create a file called '01-CONFIG-local.yml' and save it to this folder. 

This file will hold information on where to find the files to use and where to download the output. Please copy-paste the example below and fill in the required information indicated in the comments (starting with a #).


```python
output_folder:  # Include here the path to the folder in which the outputs will be downloaded 
                # the path should be between apostrophes, e.g. 'C:\Users\username\folder 1\folder 2'

merged_annex-a_filename: "{output_folder}/annex-a-merged.xlsx"
error_report_filename: "{output_folder}/annex-a-error-report.xlsx"
column_report_filename: "{output_folder}/annex-a-column-report.xlsx"

cleaned_annex-a_filename: "{output_folder}/annex-a-cleaned.xlsx"
matching_report_filename: "{output_folder}/matching-report.xlsx"

input_files:

    - root: # Include here the path to get to the folder with all the annex A files - the path should be between apostrophes
      include: "**/*.xlsx"
```

## Step 2: 10-MERGE

The 10-MERGE file uploads all the Annex A files and merges them into a unique one. In the process, it checks column titles and data type within the columns. This programme will ouput three items:
- The annex-a-merged: a unique Annex A file
- The annex-a-column-report: a list of "column_name" from the Annex A guidance matched with the "header_name" found in your file. You may see that some columns were not matched if their titles were not aligned with the Annex A guidance.
- The annex-a-error-report: a list of values that were discarded because they didn't match the normal column type - e.g. a field with "Yes" where a date was expected.

To run this step, open the 10-MERGE notebook and run all the cells. 
You can find the three output files in the output_folder you defined in 01-CONFIG-local.yml.

## Step 3: 20-CLEAN

The 20-CLEAN file goes over the annex-a-merged and aligns the values within the columns with the 2019 Annex A guidance. E.g. 'White British' (Ethnicity column) will be converted to 'a) WBRI'. This programme will output two items:
- The annex-a-cleaned: new Annex A file with values aligned with the 2019 Annex A guidance
- The matching-report: list of former values matched with Annex A-aligned values. Those that were not matched are shown as 'not matched'.

To run this step, open the 20-CLEAN notebook and run all the cells. You can find the two output files in the output_folder you defined in 01-CONFIG-local.yml.

## Final step: use the annex-a-clean

You can now use the annex-a-clean for your analysis, without a need to clean the column inputs to standardize them.
