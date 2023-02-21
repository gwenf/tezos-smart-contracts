import smartpy as sp

@sp.module
def main():

    class CountTheCalls(sp.Contract):
       def __init__(self):
           self.data.nb_calls = 0
    
       @sp.entrypoint
       def make_call(self):
           self.data.nb_calls += 1

@sp.add_test(name = "Testing")
def test():
   scenario = sp.test_scenario(main)
   contract = main.CountTheCalls()
   scenario += contract
   scenario.verify(contract.data.nb_calls == 0)
   scenario.h3(" Testing verification and error ")
   contract.make_call()
   scenario.verify(contract.data.nb_calls == 1)
   scenario.verify(contract.data.nb_calls == 2) #should pass error
   contract.make_call()
   scenario.verify(contract.data.nb_calls == 2)
