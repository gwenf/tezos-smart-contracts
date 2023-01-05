
import smartpy as sp
class NftForSale(sp.Contract):

   def __init__(self, owner, metadata, price, buy_date):
       self.init(owner = owner, metadata = metadata, price= price, buy_date = buy_date)
       
   @sp.entry_point
   def set_price(self, new_price):
       sp.verify(sp.sender == self.data.owner, "you cannot update the price")
       self.data.price = new_price

   @sp.entry_point
   def buy(self):
       sp.verify(sp.amount == self.data.price)
       sp.verify(sp.now.add_days(5) - self.data.buy_date >= 5  , "5 days between each buy")
       sp.send(self.data.owner, self.data.price)
       self.data.owner = sp.sender
       self.data.buy_date = sp.now
    
   @sp.add_test(name='Testing Update Price')
   def test():
       alice = sp.test_account("alice").address
       bob = sp.test_account("bob").address
       eve = sp.test_account("eve").address
       c1 = NftForSale(owner=alice, metadata='my first NFT', price=sp.mutez(5000000), buy_date = sp.now)
       scenario = sp.test_scenario()
       scenario +=c1
       scenario.h3("only owner can set price")
       c1.set_price(sp.mutez(7000000)).run(sender=alice)
       c1.set_price(sp.mutez(8000000)).run(sender=bob, valid = False)
       scenario.h3("Checking deadline")
       c1.buy().run(sender=eve, amount=sp.mutez(7000000), now= sp.now.add_days(1), valid = False)
       c1.buy().run(sender=bob, amount=sp.mutez(7000000), now= sp.now.add_days(1), valid = False)
       scenario.verify(c1.data.owner == bob)