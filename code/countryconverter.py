from countrymerger import *
import pandas as pd
import numpy as np
import warnings

def convert_country_df(data: pd.DataFrame, data_id_col: str, separator: str = None, standard_to_convert: str = "STATE_en_UN", warning = True, replace_missing='keep'):
    """ Function to convert a series of country ids to a different standard

    ---
    Parameters:
        data (Pandas.DataFrame): Data with country identifiers
        data_id_col (str) : Country id column name
        separator (str): separator of country identifiers in a cell (can be string or None)
        standard_to_convert (str): standard to convert to from the list pf supported standrds, to see the list consult countrymerger.KEY_COLUMNS. Default is STATE_EN_UN for UN standard country names (http://unterm.un.org).
        warning (bool): issue warnings when unable to idntify country id.
        replace_missing (str or None): what to replace missing values with

    ---
    Returns:
        converted_country_series (Pandas.Series): country_series in a new format
    """
    replacement_dict = get_id_dict(data[data_id_col], separator, standard_to_convert, warning, replace_missing=replace_missing)
    data_replaced = data.copy()
    for i in replacement_dict.items():
        print(i[0], i[1])
        data_replaced[data_id_col] = data_replaced[data_id_col].apply(lambda x: str(x).replace(str(i[0]),str(i[1])))
    return data_replaced


def get_id_set(country_series: pd.Series, separator: str = None):
    """Returns a set of countries from a series of country ids (possibly with separators)
    """
    def _add_to_country_list(country_list, country_ids, separator):
        if pd.isna(country_ids): return None
        country_ids = str(country_ids)
        #print(country_ids)
        if separator is None:
            country_list += [country_ids.strip()]
        elif separator in country_ids:
            #print([country_id.strip() for country_id in country_ids.split(separator)])
            country_list += [country_id.strip() for country_id in country_ids.split(separator)]
        else:
            #print(country_ids.strip())
            country_list += [country_ids.strip()]
    country_list = list()
    country_series.apply(lambda x: _add_to_country_list(country_list, x, separator))
    #print(country_list)
    country_set = set(country_list)
    return country_set

def get_id_dict(country_series: pd.Series, separator: str, standard_to_convert: str = "STATE_en_UN", warning = True, replace_missing='keep'):
    """Returns a dict of old country ids and new ones
    from a series of country ids (possibly with separators)
    """
    country_set = get_id_set(country_series, separator)

    keys_df = loadKeyDf(load_extra=True)
    converting_x = keys_df.columns.get_loc(standard_to_convert)
    keys = keys_df.values
    keys_lower = keys_df.applymap(lambda s: s.lower() if type(s) == str else s)
    conversion_dict = {}
    
    for country in country_set:
        country_lower = country.lower()
        try:
            i = np.where(keys_lower == country_lower)[0][0]
            country_converted = keys[i, converting_x]
            conversion_dict[country] = country_converted
        except IndexError:
            if replace_missing == 'keep':
                if warning: warnings.warn(f"Unknown identifier {country}, keeping as is")
                conversion_dict[country] = country  # keeping country as is
            else:
                if warning: warnings.warn(f"Unknown identifier {country}, replacing with {replace_missing}")
                conversion_dict[country] = replace_missing
    return conversion_dict