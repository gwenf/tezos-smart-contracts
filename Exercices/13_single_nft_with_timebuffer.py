import smartpy as sp

@sp.module
def main():

    class NftForSale(sp.Contract):
    
       def __init__(self, owner, metadata, price, buy_date):
           self.data.owner = owner
           self.data.metadata = metadata
           self.data.price= price
           self.data.buy_date = buy_date
           
       @sp.entrypoint
       def set_price(self, new_price):
           assert sp.sender == self.data.owner, "you cannot update the price"
           self.data.price = new_price
    
       @sp.entrypoint
       def buy(self):
           assert sp.amount == self.data.price
           assert sp.now >= sp.add_days(self.data.buy_date, 5)  , "5 days between each buy"
           sp.send(self.data.owner, self.data.price)
           self.data.owner = sp.sender
           self.data.buy_date = sp.now
    
@sp.add_test(name='Testing Update Price')
def test():
    alice = sp.test_account("alice").address
    bob = sp.test_account("bob").address
    eve = sp.test_account("eve").address
    c1 = main.NftForSale(owner=alice, metadata='my first NFT', price=sp.mutez(5000000), buy_date = sp.timestamp(0))
    scenario = sp.test_scenario(main)
    scenario += c1
    scenario.h3("only owner can set price")
    c1.set_price(sp.mutez(7000000)).run(sender=alice)
    c1.set_price(sp.mutez(8000000)).run(sender=bob, valid = False)
    scenario.h3("Checking deadline")
    c1.buy().run(sender=eve, amount=sp.mutez(7000000), now= sp.timestamp(4*24*3600), valid = False)
    c1.buy().run(sender=bob, amount=sp.mutez(7000000), now= sp.timestamp(6*24*3600), valid = True)
    scenario.verify(c1.data.owner == bob)
