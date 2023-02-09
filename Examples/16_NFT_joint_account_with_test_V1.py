import smartpy as sp

class NftForSale(sp.Contract):

   def __init__(self, owner, metadata, price):
       self.init(owner = owner, metadata = metadata, price= price, deadline = sp.timestamp(0))

   @sp.entry_point
   def set_price(self, new_price, deadline):
       sp.verify(sp.sender == self.data.owner, "you cannot update the price")
       self.data.price = new_price
       self.data.deadline = deadline

   @sp.entry_point
   def buy(self):
       sp.verify(sp.amount == self.data.price, "wrong price")
       sp.verify(sp.now <= self.data.deadline)
       sp.send(self.data.owner, self.data.price)
       self.data.owner = sp.sender
    
class NFTJointAccount(sp.Contract):
    def __init__(self, owner1, owner2):
        self.init(owner1 = owner1, owner2 = owner2)

    @sp.entry_point
    def buyNFT(self, nft_address):
        sp.verify( (sp.sender == self.data.owner1) | (sp.sender == self.data.owner2))
        nft_contract = sp.contract(sp.TUnit, nft_address, entry_point="buy").open_some()
        sp.transfer(sp.unit, sp.amount, nft_contract)

    @sp.entry_point
    def set_priceNFT(self, nft_address, new_price, deadline):
        sp.verify((sp.sender == self.data.owner1) | (sp.sender == self.data.owner2))
        entry_point_type = sp.TRecord(new_price = sp.TMutez, deadline = sp.TTimestamp)
        nft_contract = sp.contract(entry_point_type, nft_address, entry_point="set_price").open_some()
        sp.transfer(sp.record(new_price = new_price, deadline = deadline), sp.tez(0), nft_contract)

@sp.add_test(name='Testing set_price and buy')
def test():
   alice = sp.test_account("alice").address
   bob = sp.test_account("bob").address
   eve = sp.test_account("eve").address
   c1 = NftForSale(owner = alice, metadata = "Gwen's first NFT", price = sp.mutez(5000000))
   c2 = NFTJointAccount(bob, eve)
  
   scenario = sp.test_scenario()
   scenario += c1
   scenario += c2
   scenario.h3(" Testing set_price entrypoint")
   #testing set price
   c1.set_price(new_price = sp.mutez(7000000), deadline = sp.timestamp(10)).run(sender = alice)
   c2.buyNFT(c1.address).run(sender = bob, amount=sp.tez(5), valid=False)
   c2.buyNFT(c1.address).run(sender = bob, amount=sp.tez(7))
   c2.set_priceNFT(nft_address = c1.address, new_price = sp.tez(10), deadline = sp.timestamp(100)).run(sender = alice, valid=False)
   c2.set_priceNFT(nft_address = c1.address, new_price = sp.tez(10), deadline = sp.timestamp(100)).run(sender = bob)
   scenario.verify(c1.data.price == sp.tez(10))
   c2.set_priceNFT(nft_address = c1.address, new_price = sp.tez(20), deadline = sp.timestamp(100)).run(sender = eve)
   scenario.verify(c1.data.price == sp.tez(20))
