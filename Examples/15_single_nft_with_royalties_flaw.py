import smartpy as sp

class SingleNftWithFlaw(sp.Contract):
    def __init__(self,owner, metadata, price, author):
        self.init(owner = owner, metadata = metadata, price= price, author = author, author_rate = sp.nat(5))

    @sp.entry_point
    def buy(self):
       sp.verify(sp.amount == self.data.price)
       author_share = sp.split_tokens(self.data.price, self.data.author_rate, 100)
       owner_share = self.data.price - author_share
       sp.send(self.data.owner, owner_share)
       sp.send(self.data.author, author_share)
       self.data.price += sp.split_tokens(self.data.price, 10, 100) 
       self.data.owner = sp.sender


@sp.add_test(name='Testing')
def test():
       alice = sp.test_account("alice").address
       bob = sp.test_account("bob").address
       eve = sp.test_account("eve").address
       author = sp.test_account("author").address
       c1 = SingleNftWithFlaw(owner = alice, metadata = "Gwen's first NFT", price = sp.mutez(5000000), author = author,)
       scenario = sp.test_scenario()
       scenario +=c1    
       #testing buy entrypoint
       scenario.h3(" Testing buy entrypoint with correct and incorrect prices")
       c1.buy().run(sender=bob, amount=sp.mutez(5000000))
       c1.buy().run(sender=eve, amount=sp.mutez(5500000))
