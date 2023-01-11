import smartpy as sp

class ComputingTez(sp.Contract):
    def __init__(self):
        self.init(financial_value = sp.mutez(1000000))
    
    @sp.entry_point
    def add(self, x, y):
        self.data.financial_value = sp.utils.nat_to_tez(x) + sp.utils.nat_to_tez(y)
    
    
    @sp.entry_point
    def sub(self, x, y):
        self.data.financial_value = sp.utils.nat_to_tez(x) - sp.utils.nat_to_tez(y)
        #WARNING sp.tez(<natural number>), sp.mutez(<natural number>): No negative value
   
    @sp.entry_point
    def multiply(self, x, y):
        self.data.financial_value = sp.mul(x, y)
        #x being of type mutez and y of type nat
        
    @sp.entry_point
    def divide(self, x, y):
        self.data.financial_value = sp.fst(sp.ediv(x, y).open_some())
        #x being of type mutez and y of type nat
        #it returns and option of a pair and you can use open_some() to open the option
        # and then sp.fst to get the first element of the pair and sp.snd to get the rest


@sp.add_test(name="testing operations")
def test():
    c1 = ComputingTez()
    sc = sp.test_scenario()
    sc += c1
    c1.add(x = 5, y = 3)
    c1.sub(x = 5, y = 3)
    c1.multiply(x =  sp.tez(5), y = sp.nat(3))
    c1.divide(x =  sp.tez(5), y = sp.nat(3))