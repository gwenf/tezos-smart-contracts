import smartpy as sp

@sp.module
def main():

    class Calculator(sp.Contract):
        def __init__(self):
            self.data.int_value = sp.to_int(1)
            self.data.nat_value = sp.nat(0)
        
        @sp.entrypoint
        def add(self, x, y):
            self.data.int_value = x + y
            #if both operands not the same type use sp.to_int(nat_value) or sp.add(x,y)
        
        @sp.entrypoint
        def sub(self, x, y):
            self.data.int_value = x - y
        
        @sp.entrypoint
        def multiply(self, x, y):
            self.data.int_value = x * y
            #if both operands not the same type use sp.to_int(nat_value) or sp.mul(x,y)
    
        @sp.entrypoint
        def negation(self, x):
            self.data.int_value = -x 
            
        @sp.entrypoint
        def divide(self, x, y):
            self.data.nat_value = x / y
            #if both operands not the same type use sp.to_int(nat_value) or sp.ediv(x,y)
    
        @sp.entrypoint
        def modulo(self, x, y):
            self.data.nat_value = sp.mod(x, y)
        
        @sp.entrypoint
        def shorthand(self, x):
            self.data.int_value += x
            #self.data.value -= x
            #self.data.value *= x



@sp.add_test(name="testing operations")
def test():
    c1 = main.Calculator()
    sc = sp.test_scenario(main)
    sc += c1
    c1.add(x = 5, y = 3)
    c1.sub(x = 5, y = 3)
    c1.multiply(x =  5, y = 3)
    c1.negation(3)
    c1.divide(x = 5, y = 3)
    c1.modulo(x = 8, y = 3)
    c1.shorthand(3)
