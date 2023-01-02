import smartpy as sp

class StoreValue(sp.Contract):
   def __init__(self):
       self.init(storedValue = sp.nat(42))

   @sp.entry_point
   def add(self, a):
      sp.set_type(a, sp.TNat)
      self.data.storedValue += a

   @sp.entry_point
   def reset(self):
       self.data.storedValue = 0

@sp.add_test(name="Testing")
def test():
   scenario = sp.test_scenario()
   contract = StoreValue()
   scenario += contract
   scenario.h3("Helping with type inference")
   contract.add(sp.nat(5))
