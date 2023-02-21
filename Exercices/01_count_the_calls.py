import smartpy as sp

@sp.module
def main():

    class CountTheCalls(sp.Contract):
       def __init__(self):
           self.data.nb_calls = 0
    
       @sp.entrypoint
       def make_call(self):
           self.data.nb_calls += 1

@sp.add_test(name="Testing")
def test():
   scenario = sp.test_scenario(main)
   contract = main.CountTheCalls()
   scenario += contract
   scenario.h3(" Testing make_call entrypoint")
   contract.make_call()
   contract.make_call()
