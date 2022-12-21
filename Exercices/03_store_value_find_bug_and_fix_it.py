#Exercise: find out why we have an error here, and how to fix it. 
#Note that we don’t want to be able to use add to decrease the value, 
#or to use sub to increase it.

import smartpy as sp

class StoreValue(sp.Contract):
   def __init__(self):
       self.init(storedValue = sp.int(24))

   @sp.entry_point
   def add(self, a):
      self.data.storedValue += a

   @sp.entry_point
   def sub(self, b):
       sp.set_type(b, sp.TNat)
       self.data.storedValue -= b

@sp.add_test(name = "Testing")
def test():
   scenario = sp.test_scenario()
   contract = StoreValue()
   scenario += contract
   contract.add(sp.nat(5))
   contract.sub(5)
