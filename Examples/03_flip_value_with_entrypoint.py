import smartpy as sp

class FlipValue(sp.Contract):
    def __init__(self):
        self.init(
            bestDigit = 0
        )
    
    @sp.entry_point
    def flip(self):
        self.data.bestDigit = 1 - self.data.bestDigit