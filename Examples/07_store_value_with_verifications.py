import smartpy as sp

@sp.module
def main():

    class StoreValue(sp.Contract):
      def __init__(self):
          self.data.stored_value = 0
          
      @sp.entry_point
      def add(self,a):
        #assert a < 10
        #assert a <= 9
        #assert a < 10, "Number less than 10"
        #assert a < 10 and a > 0, would fail because of priorities
        assert (a < 10) and (a > 0), "Number strictly between 0 and 10"
        self.data.stored_value += a
      
@sp.add_test(name = 'Add')
def test():
   c1 = main.StoreValue()
   scenario = sp.test_scenario(main)
   scenario += c1
   scenario.h3("Testing add entrypoint")
   c1.add(1)
   c1.add(9)
   scenario.verify(c1.data.stored_value == 10)
   scenario.h3("Testing wrong conditions produce invalid transactions")
   c1.add(10).run(valid = False)
   c1.add(0).run(valid = False)
