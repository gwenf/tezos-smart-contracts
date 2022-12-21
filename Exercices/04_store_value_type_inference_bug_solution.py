import smartpy as sp

class StoreValue(sp.Contract):
   def __init__(self):
       self.init(storedValue = sp.int(24))

   @sp.entry_point
   def add(self, a):
      self.data.storedValue += a

   @sp.entry_point
   def sub(self, b):
       #you can help type inference with set.type to sp.TInt
       #sp.set_type(b, sp.TInt)
       self.data.storedValue -= b

@sp.add_test(name = "Testing")
def test():
   scenario = sp.test_scenario()
   contract = StoreValue()
   scenario += contract
#replace sp.nat(5) with sp.int(5)
   contract.add(sp.int(5))
   contract.sub(5)
