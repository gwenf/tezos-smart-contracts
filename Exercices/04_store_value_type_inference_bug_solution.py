import smartpy as sp

@sp.module
def main():

    class StoreValue(sp.Contract):
       def __init__(self):
           self.data.stored_value = sp.int(24)
    
       @sp.entrypoint
       def add(self, a):
          self.data.stored_value += a
    
       @sp.entrypoint
       def sub(self, b):
           #you can help type inference with set.type to sp.TInt
           #sp.cast(b, sp.int)
           self.data.stored_value -= b

@sp.add_test(name = "Testing")
def test():
   scenario = sp.test_scenario(main)
   contract = main.StoreValue()
   scenario += contract
   scenario.h3(" Helping type inference ")
#replace sp.nat(5) with sp.int(5)
   contract.add(sp.int(5))
   contract.sub(5)
