import smartpy as sp
class StoreValue(sp.Contract):
   def __init__(self):
       self.init(stored_value=0)

   @sp.entry_point
   def add(self,a):
       self.data.stored_value += a
      
   @sp.entry_point
   def reset(self):
       self.data.stored_value = 0

   @sp.entry_point
   def multiply(self,factor):
       self.data.stored_value *= factor

   @sp.add_test(name='Add')
   def test():
       c1= StoreValue()
       scenario = sp.test_scenario()
       scenario += c1
       c1.add(5)
       c1.multiply(10)
       scenario.verify(c1.data.stored_value==50)