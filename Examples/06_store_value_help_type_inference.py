import smartpy as sp

class StoreValue(sp.Contract):
   def __init__(self):
       #using sp.nat()
       self.init(storedValue = sp.nat(42))

   @sp.entry_point
   def add(self, a):
       #helping with sp.set_type()
      sp.set_type(a, sp.TNat)
      self.data.storedValue += a

   @sp.entry_point
   def reset(self):
       self.data.storedValue = 0

@sp.add_test(name = "Testing")
def test():
   scenario = sp.test_scenario()
   contract = StoreValue()
   scenario += contract
    #helping with sp.nat() in scenario
   contract.add(sp.nat(5))
    
