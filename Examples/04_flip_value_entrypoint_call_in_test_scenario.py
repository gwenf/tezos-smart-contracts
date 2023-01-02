import smartpy as sp

class FlipValue(sp.Contract):
    def __init__(self):
        self.init(
            bestDigit = 0
        )
    
    @sp.entry_point
    def flip(self):
        self.data.bestDigit = 1 - self.data.bestDigit

@sp.add_test(name = "Testing")
def test():
    scenario = sp.test_scenario()
    contract = FlipValue()
    scenario += contract
    scenario.h2("Testing flip entrypoint")
    contract.flip()
    contract.flip()
    contract.flip()
