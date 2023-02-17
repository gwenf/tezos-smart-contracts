import smartpy as sp

@sp.module
def main():

    class StoreValue(sp.Contract):
       def __init__(self):
           self.data.storedValue = 0
    
       @sp.entrypoint
       def add(self,a):
           self.data.storedValue += a
          
       @sp.entrypoint
       def reset(self):
           self.data.storedValue = 0
    
       @sp.entrypoint
       def multiply(self,factor):
           self.data.storedValue *= factor

@sp.add_test(name = "Testing")
def test():
   c1 = main.StoreValue()
   scenario = sp.test_scenario(main)
   scenario += c1
   scenario.h3("Testing add entrypoint")
   c1.add(5)
   scenario.verify(c1.data.storedValue == 5)
   scenario.h3("Testing multiply entrypoint")
   c1.multiply(10)
   scenario.verify(c1.data.storedValue == 50)
