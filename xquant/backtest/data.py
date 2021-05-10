import pandas as pd

class Data():

    # constructor
    def __init__(self, data:dict) -> None:
        '''
        Parameters
        ----------
        data : a dict with dataset names as keys and pandas DataFrames as values

        Example
        -------
        `
        data = Data({'prices':df_prices, 'volume':df_volume})
        `
        '''
        assert isinstance(data, dict) and bool(
            data), 'data must be a non-empty dictionary'
        self.data = data

    def get_data(self, key:str) -> pd.DataFrame:
        '''getter function'''
        assert key in self.data.keys(), 'attribute "data" has no matching key'
        return self.data[key]

    def set_data(self, key:str, df:pd.DataFrame) -> None:
        '''setter function'''
        assert isinstance(df, pd.DataFrame), 'df must be a pandas DataFrame'
        self.data[key] = df
