import smartpy as sp

@sp.module
def main():

    def new_price(old_price):
        return old_price + sp.split_tokens(old_price, 10, 100) 

    def new_price2(old_price):
        return old_price + sp.tez(1)
    
    class NftForSale(sp.Contract):
        def __init__(self, owner, metadata, price, author_rate, author):
            self.data.owner = owner
            self.data.metadata = metadata
            self.data.price = price
            self.data.author_rate = sp.nat(5)
            self.data.author = author
            self.data.price_update_rule = new_price
               
        @sp.entrypoint
        def buy(self):
           assert sp.amount == self.data.price
           owner_share = sp.split_tokens(self.data.price, abs(100 - self.data.author_rate), 100)
           sp.send(self.data.owner, owner_share)
           self.data.price = self.data.price_update_rule(self.data.price)
           self.data.owner = sp.sender
    
        @sp.entrypoint
        def claim_author_rate(self):
            assert sp.sender == self.data.author, " not your money "
            sp.send(self.data.author, sp.balance)

        @sp.entrypoint
        def changeRule(self, new_rule):
            assert sp.sender == self.data.author
            self.data.price_update_rule = new_rule

@sp.add_test(name='Testing')
def test():
       alice = sp.test_account("alice")
       bob = sp.test_account("bob")
       eve = sp.test_account("eve")
       author = sp.test_account("author")
       c1 = main.NftForSale(owner = alice.address, metadata = "Gwen's nft", 
       price=sp.mutez(5000000), author = author.address, author_rate = sp.mutez(1000000))
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

       scenario.h3("Test contract upgrade")
       c1.changeRule(main.new_price2).run(sender = alice, valid = False)
       c1.changeRule(main.new_price2).run(sender = author)
       c1.buy().run(sender = eve, amount = sp.mutez(6050000))
       scenario.verify(c1.data.price == sp.mutez(7050000))

       scenario.h3("Testing author fee claim")
       c1.claim_author_rate().run(sender = alice, valid = False)
       c1.claim_author_rate().run(sender = author)

