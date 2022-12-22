import smartpy as sp

class StoreValue(sp.Contract):
   def __init__(self, owner):
       self.init(storedValue = 42, owner = owner)

   @sp.entry_point
   def add(self, a):
      self.data.storedValue += a

   @sp.entry_point
   def reset(self):
       sp.verify(sp.sender == self.data.owner, "only owner can reset")
       self.data.storedValue = 0

@sp.add_test(name="Testing")
def test():
   alice = sp.test_account("Alice").address
   bob = sp.test_account("Bob").address
   contract = StoreValue(owner = alice)
   scenario = sp.test_scenario()
   scenario += contract
   contract.add(5)
   scenario.verify(contract.data.storedValue == 47)
   contract.reset().run(sender = bob, valid = False)
   contract.reset().run(sender = alice)
   scenario.verify(contract.data.storedValue == 0)
   
   
