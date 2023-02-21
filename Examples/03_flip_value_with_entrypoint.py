import smartpy as sp

@sp.module
def main():

    class FlipValue(sp.Contract):
        def __init__(self):
            self.data.bestDigit = 0
        
        @sp.entrypoint
        def flip(self):
            self.data.bestDigit = 1 - self.data.bestDigit
