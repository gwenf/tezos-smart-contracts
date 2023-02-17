import smartpy as sp

@sp.module
def main():

    entrypoint_type : type = sp.record(new_price = sp.mutez, deadline = sp.timestamp)
    
    class NftForSale(sp.Contract):
    
       def __init__(self, owner, metadata, price):
           self.data.owner = owner
           self.data.metadata = metadata
           self.data.price = price
           self.data.deadline = sp.timestamp(0)
    
       @sp.entrypoint
       def set_price(self, new_price, deadline):
           assert sp.sender == self.data.owner, "you cannot update the price"
           self.data.price = new_price
           self.data.deadline = deadline
    
       @sp.entrypoint
       def buy(self):
           assert sp.amount == self.data.price, "wrong price"
           assert sp.now <= self.data.deadline
           sp.send(self.data.owner, self.data.price)
           self.data.owner = sp.sender
        
    class NFTJointAccount(sp.Contract):
        def __init__(self, owner1, owner2):
            self.data.owner1 = owner1
            self.data.owner2 = owner2
    
        @sp.entrypoint
        def buyNFT(self, nft_address):
            assert (sp.sender == self.data.owner1) or (sp.sender == self.data.owner2)
            nft_contract = sp.contract(sp.unit, nft_address, entrypoint="buy").unwrap_some()
            sp.transfer((), sp.amount, nft_contract)
    
        @sp.entrypoint
        def set_priceNFT(self, nft_address, new_price, deadline):
            assert (sp.sender == self.data.owner1) or (sp.sender == self.data.owner2)
            
            nft_contract = sp.contract(entrypoint_type, nft_address, entrypoint="set_price").unwrap_some()
            sp.transfer(sp.record(new_price = new_price, deadline = deadline), sp.tez(0), nft_contract)

@sp.add_test(name='Testing set_price and buy')
def test():
   alice = sp.test_account("alice").address
   bob = sp.test_account("bob").address
   eve = sp.test_account("eve").address
   dan = sp.test_account("dan").address
   c1 = main.NftForSale(owner = alice, metadata = "Gwen's first NFT", price = sp.mutez(5000000))
   c2 = main.NFTJointAccount(bob, eve)
   scenario = sp.test_scenario(main)
   scenario += c1
   scenario += c2
   scenario.h3(" Testing set_price entrypoint")
   #testing set price
   c1.set_price(new_price = sp.mutez(7000000), deadline = sp.timestamp(10)).run(sender = alice)
   c2.buyNFT(c1.address).run(sender = bob, amount=sp.tez(5), valid=False)
   c2.buyNFT(c1.address).run(sender = bob, amount=sp.tez(7), now = sp.timestamp(10))
   c1.buy().run(sender = dan, amount = sp.mutez(7000000), now = sp.timestamp(11), valid = False)
   c2.set_priceNFT(nft_address = c1.address, new_price = sp.tez(10), deadline = sp.timestamp(11)).run(sender = alice, valid = False)
   c2.set_priceNFT(nft_address = c1.address, new_price = sp.tez(10), deadline = sp.timestamp(11)).run(sender = bob)
   scenario.verify(c1.data.price == sp.tez(10))
   c2.set_priceNFT(nft_address = c1.address, new_price = sp.tez(20), deadline = sp.timestamp(11)).run(sender = eve)
   scenario.verify(c1.data.price == sp.tez(20))
