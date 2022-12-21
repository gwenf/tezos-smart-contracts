import smartpy as sp

class CountTheCalls(sp.Contract):
   def __init__(self):
       self.init(nb_calls = 0)

   @sp.entry_point
   def make_call(self):
       self.data.nb_calls += 1

@sp.add_test(name = "Testing")
def test():
   scenario = sp.test_scenario()
   contract = CountTheCalls()
   scenario += contract
   scenario.verify(contract.data.nb_calls == 0)
   contract.make_call()
   scenario.verify(contract.data.nb_calls == 1)
   scenario.verify(contract.data.nb_calls == 2) #should pass error
   contract.make_call()
   scenario.verify(contract.data.nb_calls == 2)
