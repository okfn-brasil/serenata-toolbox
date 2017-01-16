from datetime import datetime

# Utilities for extracting data from XML files

def xml_extract_text(node, xpath):
    """
    :param node: the node to be queried
    :param xpath: the path to fetch the child node that has the wanted text
    """
    text = node.find(xpath).text
    if text != None:
        text = text.strip()
    return text

def xml_extract_date(node, xpath):
    """
    :param node: the node to be queried
    :param xpath: the path to fetch the child node that has the wanted date
    """
    return datetime.strptime(xml_extract_text(node, xpath), "%d/%m/%Y")

def xml_extract_datetime(node, xpath):
    """
    :param node: the node to be queried
    :param xpath: the path to fetch the child node that has the wanted datetime
    """
    return datetime.strptime(xml_extract_text(node, xpath), "%d/%m/%Y %H:%M:%S")

# Utilities for dealing with Datasets

def translate_column(df, column, translations):
    """
    :param df: (pandas.Dataframe) the dataframe to be translated
    :param column: (str) the column to be translated
    :param translations: (dict) a dictionary of the strings to be categorized and translated
    """
    df[column] = df[column].astype('category')
    translations = [translations[cat]
                   for cat in df[column].cat.categories]

    df[column].cat.rename_categories(translations,
                                     inplace=True)
