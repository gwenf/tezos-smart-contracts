import smartpy as sp

@sp.module
def main():

    class StoreValue(sp.Contract):
       def __init__(self, owner):
           self.data.store_value = 42
           self.data.owner = owner
    
       @sp.entrypoint
       def add(self, a):
          self.data.store_value += a
    
       @sp.entrypoint
       def reset(self):
           assert sp.sender == self.data.owner, "only owner can reset"
           self.data.store_value = 0

@sp.add_test(name="Testing")
def test():
   alice = sp.test_account("Alice").address
   bob = sp.test_account("Bob").address
   contract = main.StoreValue(owner = alice)
   scenario = sp.test_scenario(main)
   scenario += contract
   scenario.h3("Testing add entrypoint")
   contract.add(5)
   scenario.verify(contract.data.store_value == 47)
   scenario.h3(" Testing reset entrypoint, only owner can reset")
   contract.reset().run(sender = bob, valid = False)
   contract.reset().run(sender = alice)
   scenario.verify(contract.data.store_value == 0)
