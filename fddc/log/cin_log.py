from lxml import etree
import pandas as pd
import re

# Function to pull all the files data into a unique dataframe
# We recommend including all of the events into the cin log: it is the default list included below in build_cinrecord
# You can edit if you only need certain events

def build_cinrecord(files, include_cincensus, tag_list=['CINreferralDate', 'CINclosureDate', 'DateOfInitialCPC', 'AssessmentActualStartDate', 
              'AssessmentAuthorisationDate', 'S47ActualStartDate', 'CPPstartDate', 'CPPendDate']):
    
    if include_cincensus == True:
        data_list = []
        for i, file in enumerate(files):
            # Upload files and set root
            tree = etree.parse(file)
            root = tree.getroot()
            NS = get_namespace(root)
            children = root.find('Children', NS)
            # Get data
            print('Extracting data from file {} out of {} from CIN Census'.format(i+1, len(files)))
            file_data = buildchildren(children, tag_list, NS)
            data_list.append(file_data)
        cinrecord = pd.concat(data_list, sort=False)
        return cinrecord
    
    else:
        return None


# Functions to build dataframes containing information of the child within each file

def buildchildren(children, tag_list, NS):
    df_list = []
    for child in children:
        data = buildchild(child, tag_list, NS)
        df_list.append(data)
    children_data = pd.concat(df_list, sort=False)    
    return children_data


def buildchild(child, tag_list, NS):
    '''
    Creates a dataframe storing all the events (specified in tag_list) that happened to the child
    Pass if no ChildIdentifiers, ChildCharacteristics and CINdetails
    '''
    df_list = []
    if 'ChildIdentifiers' in get_childrentags(child) and \
    'ChildCharacteristics' in get_childrentags(child) and \
    'CINdetails' in get_childrentags(child):
        for group in child:
            if group.tag.endswith('ChildIdentifiers'):
                childidentifiers = get_ChildIdentifiers(group)
            if group.tag.endswith('ChildCharacteristics'):
                childcharacteristics = get_ChildCharacteristics(group, NS)
            if group.tag.endswith('CINdetails'):
                for tag in tag_list:
                    event_list = group.findall('.//{}'.format(tag), NS)
                    for event in event_list:
                        event_group = get_group(event, NS)
                        df = pd.DataFrame(event_group)
                        df_list.append(df)        
        child_data = pd.concat(df_list, sort=False)
        for key, value in childidentifiers.items() :
            child_data[key] = value
        for key, value in childcharacteristics.items() :
            child_data[key] = value
        return(child_data)
    
    return None


# Functions to store the information at child level

def get_ChildIdentifiers(element, NS=None):
    childidentifiers = {}
    for group in element:
        column = etree.QName(group).localname
        value = group.text
        childidentifiers[column] = value
    return childidentifiers


def get_ChildCharacteristics(element, NS):
    childcharacteristics = {}
    for group in element:
        if group.tag.endswith('Ethnicity'):
            column = etree.QName(group).localname
            value = group.text
        elif group.tag.endswith('Disabilities'):
            column = etree.QName(group).localname
            value = get_list(group, 'Disability', NS)
        childcharacteristics[column] = value
    return childcharacteristics


# Functions to get information at element level

def get_list(element, tag, NS):
    '''
    Starting from the 'element', makes a list of the contents of 'tag' nieces (siblings' children sharing the same tag)
    and returns a string
    '''
    value_list = []
    values = element.getparent().findall('.//{}'.format(tag), NS)
    for value in values:
        value_list.append(value.text.strip())
    value_list = (',').join(value_list)
    value_list = value_list.replace(' ', '')
    return value_list


def get_group(element, NS):
    group = {}
    # Load our reference element
    group['Date'] = element.text
    group['Type'] = etree.QName(element).localname
    # Get the other elements on the same level (siblings)
    siblings = element.getparent().getchildren()
    for sibling in siblings:
        if len(sibling.getchildren())==0: # if siblings don't have children, just get their value
            column = etree.QName(sibling).localname
            value = sibling.text
            group[column] = [value]
    # If we're in the Assessment or ChildProtectionPlans modules, we need to get down one level
    # to collect all AssessmentFactors and CPPreviewDate
    if element.getparent().tag.endswith('Assessments'):
        group['Factors'] = get_list(element, 'AssessmentFactors', NS)
    if element.getparent().tag.endswith('ChildProtectionPlans'):
        group['CPPreview'] = get_list(element, 'CPPreviewDate', NS)
    return group


def get_childrentags(element):
    '''
    Returns the list of tags of the element's children
    '''
    children = element.getchildren()
    tags = []
    for child in children:
        tags.append(etree.QName(child).localname)
    return tags


# Function to dentify namespace

def get_namespace(root):
    regex = r'{(.*)}.*' # pattern to pick up namespace
    namespace = re.findall(regex, root.tag)
    if len(namespace)>0:
        namespace = namespace[0]
    else:
        namespace = None
    NS = {None: namespace}
    return NS