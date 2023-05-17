import smartpy as sp

@sp.module
def main():

    class StoreValue(sp.Contract):
       def __init__(self):
           self.data.stored_value = 42
    
       @sp.entrypoint
       def add(self, a):
           self.data.stored_value += a
    
       @sp.entrypoint
       def reset(self):
           self.data.stored_value = 0

@sp.add_test(name="Testing")
def test():
   scenario = sp.test_scenario(main)
   contract = main.StoreValue()
   scenario += contract
   scenario.h3("Testing Add entrypoint with 5 as parameter")
   contract.add(5)
   #you should not pass param when entrypoint with one parameter
   #contract.add(a=5)
   scenario.verify(contract.data.stored_value==47)
