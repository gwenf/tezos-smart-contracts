import smartpy as sp

@sp.module
def main():

    class NftForSale(sp.Contract):
        def __init__(self, owner, metadata, price, author_rate, author):
            self.data.owner = owner
            self.data.metadata = metadata
            self.data.price = price
            self.data.author_rate = sp.nat(5)
            self.data.author = author
               
        @sp.entrypoint
        def buy(self):
           assert sp.amount == self.data.price
           owner_share = sp.split_tokens(self.data.price, abs(100 - self.data.author_rate), 100)
           sp.send(self.data.owner, owner_share)
           self.data.price += sp.split_tokens(sp.amount, 10, 100)
           self.data.owner = sp.sender
    
        @sp.entrypoint
        def claim_author_rate(self):
            assert sp.sender == self.data.author, " not your money "
            sp.send(self.data.author, sp.balance)

@sp.add_test(name='Testing')
def test():
       alice = sp.test_account("alice").address
       bob = sp.test_account("bob").address
       eve = sp.test_account("eve").address
       author = sp.test_account("author").address
       c1 = main.NftForSale(owner = alice, metadata = "Gwen's nft", 
       price=sp.mutez(5000000), author=author, author_rate = sp.mutez(1000000))
       scenario = sp.test_scenario(main)
       scenario +=c1
       scenario.verify(c1.data.price == sp.mutez(5000000) )
       scenario.h3(" Testing increasing price")
       c1.buy().run(sender = bob, amount = sp.mutez(5000000))
       scenario.verify(c1.data.price == sp.mutez(5500000) )
       scenario.verify(c1.balance == sp.mutez(250000) )
       c1.buy().run(sender = eve, amount = sp.mutez(5500000))
       c1.buy().run(sender = alice, amount = sp.mutez(6000000), valid = False)
       scenario.verify(c1.data.price == sp.mutez(6050000))
       scenario.h3("Testing author fee claim")
       c1.claim_author_rate().run(sender = alice, valid = False)
       c1.claim_author_rate().run(sender = author)
