import smartpy as sp

@sp.module
def main():

    class FlipValue(sp.Contract):
        def __init__(self):
            self.data.best_digit = 0
        
        @sp.entrypoint
        def flip(self):
            self.data.best_digit = 1 - self.data.best_digit

@sp.add_test(name = "Testing")
def test():
    scenario = sp.test_scenario(main)
    contract = main.FlipValue()
    scenario += contract
    scenario.h2("Testing flip entrypoint")
    contract.flip()
    contract.flip()
    contract.flip()
