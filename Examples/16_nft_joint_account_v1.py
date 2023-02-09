import smartpy as sp

class NftForSale(sp.Contract):

   def __init__(self, owner, metadata, price):
       self.init(owner = owner, metadata = metadata, price= price)

   @sp.entry_point
   def set_price(self, new_price):
       sp.verify(sp.sender == self.data.owner, "you cannot update the price")
       self.data.price = new_price

   @sp.entry_point
   def buy(self):
       sp.verify(sp.amount == self.data.price, "wrong price")
       sp.send(self.data.owner, self.data.price)
       self.data.owner = sp.sender
    
class NFTJointAccount(sp.Contract):
    def __init__(self, owner1, owner2):
        self.init(owner1 = owner1, owner2 = owner2)

    @sp.entry_point
    def buyNFT(self, nft_address):
        sp.verify( (sp.sender == self.data.owner1) | (sp.sender == self.data.owner2))
        c = sp.contract(sp.TUnit,nft_address,entry_point="buy").open_some()
        sp.transfer(sp.unit,sp.amount,c)

@sp.add_test(name='Testing set_price and buy')
def test():
   alice = sp.test_account("alice").address
   bob = sp.test_account("bob").address
   eve = sp.test_account("eve").address
   c1 = NftForSale(owner = alice, metadata = "Gwen's first NFT", price = sp.mutez(5000000))
   c2 = NFTJointAccount(bob, eve)
   scenario = sp.test_scenario()
   scenario +=c1
   scenario +=c2
   scenario.h3(" Testing set_price entrypoint")
   #testing set price
   c1.set_price(sp.mutez(7000000)).run(sender = alice)
   c2.buyNFT(c1.address).run(sender = bob, amount=sp.tez(7))
   c1.set_price(sp.mutez(7000000)).run(sender = eve, valid = False)
   scenario.verify(c1.data.price != sp.mutez(6000000))
   scenario.verify(c1.data.price == sp.mutez(7000000))
   c2.buyNFT(c1.address).run(sender = eve, amount=sp.tez(7), valid = False)
   c2.buyNFT(c1.address).run(sender = alice, amount=sp.tez(6), valid = False)
        
