import smartpy as sp

class StoreValue(sp.Contract):
  def __init__(self):
      self.init(storedValue = 0)
      
  @sp.entry_point
  def add(self,a):
    #sp.verify(a < 10)
    #sp.verify(a <= 9)
    #sp.verify(a < 10,"Number less than 10")
    #sp.verify(a < 10 & a > 0), would fail because of priorities
    sp.verify((a < 10) & (a > 0), "Number strictly between 0 and 10")
    self.data.storedValue += a
      
@sp.add_test(name = 'Add')
def test():
   c1 = StoreValue()
   scenario = sp.test_scenario()
   scenario += c1
   scenario.h3("Testing add entrypoint")
   c1.add(1)
   c1.add(9)
   scenario.verify(c1.data.storedValue == 10)
   scenario.h3("Testing wrong conditions produce invalid transactions")
   c1.add(10).run(valid = False)
   c1.add(0).run(valid = False)
