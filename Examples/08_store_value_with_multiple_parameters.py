import smartpy as sp

class StoreValue(sp.Contract):

    def __init__(self, minValue, maxValue):
        self.init(minValue = minValue, maxValue = maxValue)

    @sp.entry_point
    def set(self, newMinValue, newMaxValue):
            self.data.minValue = newMinValue
            self.data.maxValue = newMaxValue
            
    @sp.entry_point
    def addNumber(self, a):
            self.data.minValue += a
            self.data.maxValue += a
            
@sp.add_test(name = "testing")
def test():
        c1 = StoreValue(minValue = 0, maxValue = 5)
        scenario = sp.test_scenario()
        scenario += c1
        c1.set(newMinValue = 5, newMaxValue = 10)
        #show that you have errors when not naming params in entrypoint call
        #c1.set(5, 10)
        c1.addNumber(20)
        scenario.verify(c1.data.minValue == 25)
        scenario.verify(c1.data.maxValue == 30)
        c1.addNumber(-50)
        scenario.verify(c1.data.minValue == -25)
        scenario.verify(c1.data.maxValue == -20)
