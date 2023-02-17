#Exercise: find out why we have an error here, and how to fix it. 
#Note that we don’t want to be able to use add to decrease the value, 
#or to use sub to increase it.

import smartpy as sp

@sp.module
def main():

    class StoreValue(sp.Contract):
       def __init__(self):
           self.data.storedValue = sp.int(24)
    
       @sp.entrypoint
       def add(self, a):
          self.data.storedValue += a
    
       @sp.entrypoint
       def sub(self, b):
           sp.cast(b, sp.nat)
           self.data.storedValue -= b

@sp.add_test(name = "Testing")
def test():
   scenario = sp.test_scenario(main)
   contract = main.StoreValue()
   scenario += contract
   contract.add(sp.nat(5))
   contract.sub(5)
