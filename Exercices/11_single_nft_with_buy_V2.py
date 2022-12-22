#with claim() entrypoint
import smartpy as sp
class NftForSale(sp.Contract):

   def __init__(self, owner, metadata, price):
       self.init(owner = owner, metadata = "Gwen's NFT", price= price)
       
   @sp.entry_point
   def set_price(self, new_price):
       sp.verify(sp.sender == self.data.owner, "you cannot update the price")
       self.data.price = new_price

   @sp.entry_point
   def buy(self):
       sp.verify(sp.amount == self.data.price)
       sp.send(self.data.owner, self.data.price)
       self.data.owner = sp.sender
       self.data.price = sp.none
    
   @sp.add_test(name='Testing Update Price')
   def test():
       alice = sp.test_account('alice').address
       bob = sp.test_account('bob').address
       c1 = NftForSale(owner=alice, metadata='I am a string', price=sp.mutez(5000000))
       scenario = sp.test_scenario()
       scenario +=c1
       c1.set_price(sp.mutez(7000000)).run(sender=alice)
       c1.buy().run(sender=bob, amount=sp.mutez(7000000))