import smartpy as sp

@sp.module
def main():

    def new_price(old_price):
        return old_price + sp.split_tokens(old_price, 10, 100) 

    def new_price2(old_price):
        return old_price + sp.tez(1)
    
    class NftForSale(sp.Contract):
        
       def __init__(self, owner, metadata, price):
           self.data.author = owner
           self.data.owner = owner
           self.data.metadata = metadata
           self.data.price = price
           self.data.price_update_rule = new_price
    
       @sp.entrypoint
       def buy(self):
           assert sp.amount == self.data.price
           sp.send(self.data.owner, self.data.price)
           self.data.owner = sp.sender
           self.data.price = self.data.price_update_rule(self.data.price)

       @sp.entrypoint
       def change_rule(self, newRule):
           self.data.price_update_rule = newRule

@sp.add_test(name='Testing Update Price')
def test():
    alice = sp.test_account("alice")
    bob = sp.test_account("bob")
    eve = sp.test_account("eve")
    c1 = main.NftForSale(owner = alice, metadata = "Gwen's nft", price=sp.mutez(5000000))
    scenario = sp.test_scenario(main)
    scenario +=c1
    scenario.h3(" Testing increasing price")
    c1.buy().run(sender = bob, amount = sp.mutez(5000000))
    c1.buy().run(sender = eve, amount = sp.mutez(5500000))
    c1.buy().run(sender = alice, amount = sp.mutez(6000000), valid = False)
    scenario.verify(c1.data.price == sp.mutez(6050000))
    c1.change_rule(main.new_price2).run(sender = alice)
    c1.buy().run(sender = bob, amount = sp.mutez(6050000))
    scenario.verify(c1.data.price == sp.mutez(7050000))
