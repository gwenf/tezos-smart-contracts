import smartpy as sp

@sp.module
def main():

    class StoreValue(sp.Contract):
        
        def __init__(self, minValue, maxValue):
            self.data.minValue = minValue
            self.data.maxValue = maxValue
    
        @sp.entrypoint
        def set(self, newMinValue, newMaxValue):
            self.data.minValue = newMinValue
            self.data.maxValue = newMaxValue
                
        @sp.entrypoint
        def addNumber(self, a):
            self.data.minValue += a
            self.data.maxValue += a
            
@sp.add_test(name = "testing")
def test():
        c1 = main.StoreValue(minValue = 0, maxValue = 5)
        scenario = sp.test_scenario(main)
        scenario += c1
        scenario.h3(" Setting Min and Max")
        c1.set(newMinValue = 5, newMaxValue = 10)
        scenario.verify(c1.data.minValue == 5)
        scenario.verify(c1.data.maxValue == 10)
        #show that you have errors when not naming params in entrypoint call
        #c1.set(5, 10)
        scenario.h3(" Testing Add Number and Verify")
        c1.addNumber(20)
        scenario.verify(c1.data.minValue == 25)
        scenario.verify(c1.data.maxValue == 30)
        c1.addNumber(-50)
        scenario.verify(c1.data.minValue == -25)
        scenario.verify(c1.data.maxValue == -20)
