import smartpy as sp

@sp.module
def main():

    class StoreValue(sp.Contract):
       def __init__(self):
           self.data.storedValue = sp.nat(42)
    
       @sp.entrypoint
       def add(self, a):
          sp.cast(a, sp.nat)
          self.data.storedValue += a
    
       @sp.entrypoint
       def reset(self):
           self.data.storedValue = 0

@sp.add_test(name="Testing")
def test():
   scenario = sp.test_scenario(main)
   contract = main.StoreValue()
   scenario += contract
   scenario.h3("Helping with type inference")
   contract.add(sp.nat(5))
