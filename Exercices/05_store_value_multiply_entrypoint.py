import smartpy as sp

class StoreValue(sp.Contract):
   def __init__(self):
       self.init(storedValue = 0)

   @sp.entry_point
   def add(self,a):
       self.data.storedValue += a
      
   @sp.entry_point
   def reset(self):
       self.data.storedValue = 0

   @sp.entry_point
   def multiply(self,factor):
       self.data.storedValue *= factor

   @sp.add_test(name = "Testing")
   def test():
       c1= StoreValue()
       scenario = sp.test_scenario()
       scenario += c1
       scenario.h3("Testing add entrypoint")
       c1.add(5)
       scenario.verify(c1.data.storedValue == 5)
       scenario.h3("Testing multiply entrypoint")
       c1.multiply(10)
       scenario.verify(c1.data.storedValue == 50)
