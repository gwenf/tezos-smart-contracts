import smartpy as sp

@sp.module
def main():

    class NftForSale(sp.Contract):
    
       def __init__(self, owner, metadata, price):
           self.data.owner = owner
           self.data.metadata = metadata
           self.data.price = price
           
       @sp.entrypoint
       def set_price(self, new_price):
           assert sp.sender == self.data.owner, "you cannot update the price"
           self.data.price = new_price
    
       @sp.entrypoint
       def buy(self):
           assert sp.Some(sp.amount) == self.data.price
           sp.send(self.data.owner, sp.amount)
           self.data.owner = sp.sender
           self.data.price = None
    
@sp.add_test(name='Testing Update Price')
def test():
    alice = sp.test_account('alice').address
    bob = sp.test_account('bob').address
    c1 = main.NftForSale(owner=alice, metadata = "Gwen's NFT", price=sp.some(sp.mutez(5000000)))
    scenario = sp.test_scenario(main)
    scenario +=c1
    c1.set_price(sp.some(sp.mutez(7000000))).run(sender=alice)
    c1.buy().run(sender=bob, amount=sp.mutez(7000000))
    #scenario.verify(c1.data.owner == alice)
