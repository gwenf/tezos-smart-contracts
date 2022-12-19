import smartpy as sp

class StoreValue(sp.Contract):
   def __init__(self):
       self.init(storedValue = 42)

   @sp.entry_point
   def add(self, a):
       self.data.storedValue += a

   @sp.entry_point
   def reset(self):
       self.data.storedValue = 0

@sp.add_test(name="Testing")
def test():
   scenario = sp.test_scenario()
   contract = StoreValue()
   scenario += contract
   contract.add(5)
   #you should not pass param when entrypoint with one parameter
   #contract.add(a=5)
   scenario.verify(contract.data.storedValue==47)