import smartpy as sp

@sp.module
def main():

    class StoreValue(sp.Contract):
        
        def __init__(self, min_value, max_value):
            self.data.min_value = min_value
            self.data.max_value = max_value
    
        @sp.entrypoint
        def set(self, new_min_value, new_max_value):
            self.data.min_value = new_min_value
            self.data.max_value = new_max_value
                
        @sp.entrypoint
        def addNumber(self, a):
            self.data.min_value += a
            self.data.max_value += a
            
@sp.add_test(name = "testing")
def test():
        c1 = main.StoreValue(min_value = 0, max_value = 5)
        scenario = sp.test_scenario(main)
        scenario += c1
        scenario.h3(" Setting Min and Max")
        c1.set(new_min_value = 5, new_max_value = 10)
        scenario.verify(c1.data.min_value == 5)
        scenario.verify(c1.data.max_value == 10)
        #show that you have errors when not naming params in entrypoint call
        #c1.set(5, 10)
        scenario.h3(" Testing Add Number and Verify")
        c1.addNumber(20)
        scenario.verify(c1.data.min_value == 25)
        scenario.verify(c1.data.max_value == 30)
        c1.addNumber(-50)
        scenario.verify(c1.data.min_value == -25)
        scenario.verify(c1.data.max_value == -20)
