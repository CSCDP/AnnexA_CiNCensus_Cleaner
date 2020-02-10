from lxml import etree
from datetime import datetime
import re
import glob
import os   
from lxml import etree

# Main cleaner function

def cleanfiles(input_folder, output_folder, config):
    cin_files = glob.glob(os.path.join(input_folder, "*.xml"))
    for i, file in enumerate(cin_files):
        filename = file.replace(input_folder + '\\', '')
        # Upload files and set root
        print('Cleaning file {} out of {}'.format(i+1, len(cin_files)))
        tree = etree.parse(file)
        root = tree.getroot()
        NS = get_namespace(root)
        children = root.find('Children', NS)
        for child in children:
            child = cleanchild(child, config)
        tree.write(os.path.join(output_folder, "cleaned-{}".format(filename)))
    return 


# Cleaner functions depending on XML tag for each file

def cleanchild(value, config):
    for group in value:
        if group.tag.endswith('ChildIdentifiers'):
            group = childidentifiers(group, config['ChildIdentifiers'])
        elif group.tag.endswith('ChildCharacteristics'):
            group = childcharacteristics(group, config['ChildCharacteristics'])
        elif group.tag.endswith('CINdetails'):
            group = cindetails(group, config['CINdetails'])
    return value

# Child Identifiers functions
def childidentifiers(value, config):
    for group in value:
        if group.tag.endswith('LAchildID'):
            group = lachildid(group)
        if group.tag.endswith('UPN'):
            group = upn(group)
        if group.tag.endswith('FormerUPN'):
            group = formerupn(group)
        if group.tag.endswith('UPNunknown'):
            group = upnunknown(group, config['UPNunknown'])
        if group.tag.endswith('PersonBirthDate'):
            group = personbirthdate(group, config['PersonBirthDate'])
        if group.tag.endswith('ExpectedPersonBirthDate'):
            group = expectedpersonbirthdate(group, config['ExpectedPersonBirthDate'])
        if group.tag.endswith('GenderCurrent'):
            group = gendercurrent(group, config['GenderCurrent'])
        if group.tag.endswith('PersonDeathDate'):
            group = persondeathdate(group, config['PersonDeathDate'])
    return value

def lachildid(value, config=None):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip()
    # If time, add config and test that len<=10 and type = alphanumeric
    return value

def upn(value, config=None):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip().upper()
    # If time, add config and test that len==13 and regex follows pattern
    return value

def formerupn(value, config=None):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip().upper()
    # If time, add config and test that len==13 and regex follows pattern
    return value

def upnunknown(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip().upper()
        value.text = to_category(value.text, config['category'])
    return value

def personbirthdate(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip()
        value.text = to_date(value.text, config['date'])
    return value

def expectedpersonbirthdate(value, config):
    if value.text is None:
        node = value.getparent()
        try:
            node.remove(value)
        except:
            pass
    else:
        value.text = value.text.strip()
        value.text = to_date(value.text, config['date'])
    return value
# If time, add logical test to check there is just one birth date

def gendercurrent(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip()
        value.text = to_category(value.text, config['category'])
    return value

def persondeathdate(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip()
        value.text = to_date(value.text, config['date'])
    return value

# Child Characteristics functions
def childcharacteristics(value, config):
    for group in value:
        if group.tag.endswith('Ethnicity'):
            group = ethnicity(group, config['Ethnicity'])
        if group.tag.endswith('Disabilities'):
            group = disabilities(group, config['Disabilities'])
    return value

def ethnicity(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip().upper()
        value.text = to_category(value.text, config['category'])
    return value

def disabilities(value, config):
    for group in value:
        if group.tag.endswith('Disability'):
            group = disability(group, config['Disability'])
        else:
            pass #Here add a flag if we are getting something else
    return value

def disability(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip().upper()
        value.text = to_category(value.text, config['category'])
    return value

# CIN Details functions
def cindetails(value, config):
    for group in value:
        if group.tag.endswith('CINreferralDate'):
            group = cinreferraldate(group, config['CINreferralDate'])
        if group.tag.endswith('ReferralSource'):
            group = referralsource(group, config['ReferralSource'])
        if group.tag.endswith('PrimaryNeedCode'):
            group = primaryneedcode(group, config['PrimaryNeedCode'])
        if group.tag.endswith('CINclosureDate'):
            group = cinclosuredate(group, config['CINclosureDate'])
        if group.tag.endswith('ReasonForClosure'):
            group = reasonforclosure(group, config['ReasonForClosure'])
        if group.tag.endswith('ReferralNFA'):
            group = referralnfa(group, config['ReferralNFA'])
        if group.tag.endswith('DateOfInitialCPC'):
            group = dateofinitialcpc(group, config['DateOfInitialCPC'])
        if group.tag.endswith('Assessments'):
            group = assessments(group, config['Assessments'])
        if group.tag.endswith('Section47'):
            group = section47(group, config['Section47'])
        if group.tag.endswith('ChildProtectionPlans'):
            group = childprotectionplans(group, config['ChildProtectionPlans'])
    return value

def cinreferraldate(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip()
        value.text = to_date(value.text, config['date'])
    return value

def referralsource(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip().upper()
        value.text = to_category(value.text, config['category'])
    return value

def primaryneedcode(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip().upper()
        value.text = to_category(value.text, config['category']) 
    return value

def cinclosuredate(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip()
        value.text = to_date(value.text, config['date'])
    return value

def reasonforclosure(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip().upper()
        value.text = to_category(value.text, config['category'])
    return value

def referralnfa(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip().capitalize()
        value.text = to_category(value.text, config['category'])
    return value

def dateofinitialcpc(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip()
        value.text = to_date(value.text, config['date'])
    return value

def assessments(value, config):
    for group in value:
        if group.tag.endswith('AssessmentActualStartDate'):
            group = assessmentactualstartdate(group, config['AssessmentActualStartDate'])
        if group.tag.endswith('AssessmentInternalReviewDate'):
            group = assessmentinternalreviewdate(group, config['AssessmentInternalReviewDate'])
        if group.tag.endswith('AssessmentAuthorisationDate'):
            group = assessmentauthorisationdate(group, config['AssessmentAuthorisationDate'])
        if group.tag.endswith('FactorsIdentifiedAtAssessment'):
            group = factorsidentifiedatassessment(group, config['FactorsIdentifiedAtAssessment'])
    return value

def assessmentactualstartdate(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip()
        value.text = to_date(value.text, config['date'])
    return value

def assessmentinternalreviewdate(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip()
        value.text = to_date(value.text, config['date'])
    return value

def assessmentauthorisationdate(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip()
        value.text = to_date(value.text, config['date'])
    return value

def factorsidentifiedatassessment(value, config):
    for group in value:
        if group.tag.endswith('AssessmentFactors'):
            group = assessmentfactors(group, config['AssessmentFactors'])
        else:
            pass # if time, flag whatever else we find here
    return value    

def assessmentfactors(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip().upper()
        value.text = to_category(value.text, config['category'])
    return value

def section47(value, config):
    for group in value:
        if group.tag.endswith('S47ActualStartDate'):
            group = s47actualstartdate(group, config['S47ActualStartDate'])
        if group.tag.endswith('InitialCPCtarget'):
            group = initialcpctarget(group, config['InitialCPCtarget'])
        if group.tag.endswith('DateOfInitialCPC'):
            group = dateofinitialcpc(group, config['DateOfInitialCPC'])
        if group.tag.endswith('ICPCnotRequired'):
            group = icpcnotrequired(group, config['ICPCnotRequired'])
    return value

def s47actualstartdate(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip()
        value.text = to_date(value.text, config['date'])
    return value

def initialcpctarget(value, config):
    if value.text is not None: #if time, automate the reading of 'canbeblank'
        value.text = value.text.strip()
        value.text = to_date(value.text, config['date'])
    return value

def dateofinitialcpc(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip()
        value.text = to_date(value.text, config['date'])
    return value

def icpcnotrequired(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip().capitalize()
        value.text = to_category(value.text, config['category'])
    return value

def childprotectionplans(value, config):
    for group in value:
        if group.tag.endswith('CPPstartDate'):
            group = cppstartdate(group, config['CPPstartDate'])
        if group.tag.endswith('InitialCategoryOfAbuse'):
            group = initialcategoryofabuse(group, config['InitialCategoryOfAbuse'])
        if group.tag.endswith('LatestCategoryOfAbuse'):
            group = latestcategoryofabuse(group, config['LatestCategoryOfAbuse'])
        if group.tag.endswith('NumberOfPreviousCPP'):
            group = numberofpreviouscpp(group)
        if group.tag.endswith('CPPendDate'):
            group = cppenddate(group, config['CPPendDate'])
        if group.tag.endswith('Reviews'):
            group = reviews(group, config['Reviews'])
    return value

def cppstartdate(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip()
        value.text = to_date(value.text, config['date'])
    return value

def initialcategoryofabuse(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip().upper()
        value.text = to_category(value.text, config['category'])
    return value

def latestcategoryofabuse(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip().upper()
        value.text = to_category(value.text, config['category'])
    return value

def numberofpreviouscpp(value, config=None):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip()
        value.text = to_integer(value.text)
    return value

def cppenddate(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip()
        value.text = to_date(value.text, config['date'])
    return value

def reviews(value, config):
    for group in value:
        if group.tag.endswith('CPPreviewDate'):
            group = cppreviewdate(group, config['CPPreviewDate'])
        else:
            pass # if time, flag whatever else we find here
    return value

def cppreviewdate(value, config):
    if value.text is None:
        node = value.getparent()
        node.remove(value)
    else:
        value.text = value.text.strip()
        value.text = to_date(value.text, config['date'])
    return value


# Generic cleaner functions

def to_category(string, categories):
    for code in categories:
        if str(string).lower() == str(code['code']).lower():
            return code['code']
        elif str(code['code']).lower() in str(string).lower():
            return code['code']
        elif 'name' in code:
            if str(code['name']).lower() in str(string).lower():
                return code['code']
    return 'Not in proper format: {}'.format(string)
    # If time, add here the matching report

def to_date(string, dateformat):
    try:
        datetime.strptime(string, dateformat) # Check this is possible
    except:
        string = 'Not in proper format: {}'.format(string)
    return string
    # If time, add here the matching report
    
def to_integer(string):
    try:
        int(string) # Check this is possible
    except:
        string = 'Not in proper format: {}'.format(string)
        # If time, add here the matching report

        
# Find namespace

def get_namespace(root):
    regex = r'{(.*)}.*' # pattern to pick up namespace
    namespace = re.findall(regex, root.tag)
    if len(namespace)>0:
        namespace = namespace[0]
    else:
        namespace = None
    NS = {None: namespace}
    return NS