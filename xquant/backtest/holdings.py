from xquant.portfolio import Portfolio
import pickle

class Holdings():

    def __init__(self, holding:dict) -> None:
        self.holding = holding
    
    