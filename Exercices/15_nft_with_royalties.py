import smartpy as sp

class NftForSale(sp.Contract):
   def __init__(self, owner, metadata, price, author_fee, author):
       self.init(owner = owner, metadata = metadata, price = price, author_fee = author_fee, author = author)

   @sp.entry_point
   def buy(self):
       sp.verify(sp.amount == self.data.price)
       author_fee = sp.split_tokens(self.data.price, 5, 100)
       self.data.author_fee += author_fee
       owner_fee = self.data.price - author_fee
       sp.send(self.data.owner, owner_fee)
       self.data.price+=sp.split_tokens(sp.amount, 10, 100)
       self.data.owner = sp.sender
       

   @sp.entry_point
   def claim_author_fee(self, requestedAmount):
        sp.verify(sp.sender == self.data.author, " not your money ")
        sp.send( self.data.author, requestedAmount)

@sp.add_test(name='Testing')
def test():
       alice = sp.test_account("alice").address
       bob = sp.test_account("bob").address
       eve = sp.test_account("eve").address
       author = sp.test_account("author").address
       c1 = NftForSale(owner = alice, metadata = "Gwen's nft", 
       price=sp.mutez(5000000), author=author, author_fee = sp.mutez(1000000))
       scenario = sp.test_scenario()
       scenario +=c1
       scenario.h3(" Testing increasing price")
       c1.buy().run(sender = bob, amount = sp.mutez(5000000))
       c1.buy().run(sender = eve, amount = sp.mutez(5500000))
       c1.buy().run(sender = alice, amount = sp.mutez(6000000), valid = False)
       
       scenario.verify(c1.data.price == sp.mutez(6050000))
       scenario.h3("Testing author fee claim")
       c1.claim_author_fee(sp.tez(1)).run(sender = alice, valid = False)
       c1.claim_author_fee(sp.mutez(525000)).run(sender = author)
