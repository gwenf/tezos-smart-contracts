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
    
class NftWrapperContract(sp.Contract):
    def __init__(self, allowSales, owner, price):
        self.init(allowSales = allowSales, price = price, owner_wrapper = owner)


    @sp.entry_point
    def buyNFT(self, nft_address):
        sp.verify(sp.sender == self.data.owner_wrapper)
        nft_contract = sp.contract(sp.TUnit, nft_address, entry_point="buy").open_some()
        sp.transfer(sp.unit, sp.amount, nft_contract)
        
    @sp.entry_point
    def setPrice(self, new_price):
        sp.verify(sp.sender == self.data.owner_wrapper)
        self.data.price = new_price


    @sp.entry_point
    def buy(self):
        sp.verify(sp.amount == self.data.price)
        #sp.verify(self.data.allowSales == True)
        sp.send(self.data.owner_wrapper, self.data.price)
        self.data.owner_wrapper = sp.sender
        
    @sp.entry_point
    def setAllowSale(self, new_boolean):
        sp.verify(sp.sender == self.data.owner_wrapper)
        self.data.allowSales = new_boolean

    @sp.entry_point
    def default(self):
        sp.verify(self.data.allowSales == True)

@sp.add_test(name="test Wrapped Nft")
def test():
   alice = sp.test_account("alice").address
   bob = sp.test_account("bob").address
   eve = sp.test_account("eve").address
   dan = sp.test_account("dan").address
   c1 = NftForSale(owner = alice, metadata = "Gwen's first NFT", price = sp.mutez(5000000))
   c2 = NftWrapperContract(allowSales = sp.bool(True), price = sp.mutez(5000000), owner = bob)
   scenario = sp.test_scenario()
   scenario +=c1
   scenario +=c2
   scenario.h3(" Testing set_price entrypoint")
   c1.set_price(new_price = sp.mutez(7000000), deadline = sp.timestamp(100)).run(sender = bob, valid = False)
   c1.set_price(new_price = sp.mutez(7000000), deadline = sp.timestamp(100)).run(sender = alice)
   scenario.h3("testing buy NFT from Wrapper")
   c2.buyNFT(c1.address).run(sender = bob, amount=sp.tez(7), now = sp.timestamp(50))
   scenario.verify(c1.data.owner == c2.address)
   scenario.h3("testing allowSales")
   c2.setAllowSale(False).run(sender = eve, valid = False)
   c2.setAllowSale(False).run(sender = bob)
   scenario.h3("testing setPrice NFT Wrapper")
   c2.setPrice(sp.tez(50)).run(sender = eve, valid = False)
   c2.setPrice(sp.tez(50)).run(sender = bob)
   scenario.verify(c2.data.price == sp.tez(50))
   scenario.verify(c2.data.owner_wrapper == bob)
   scenario.h3("trying to buy nft from NFTforSale while not possible")
   scenario.verify(c1.data.price == sp.tez(7))
   c1.buy().run(sender = dan, amount = sp.tez(7), valid = False)
   scenario.h3("buying NftWrapper i.e. buying NFT at nftwrapper set_price()")
   c2.buy().run(sender = dan, amount = sp.tez(50))
   scenario.verify(c2.data.owner_wrapper == dan)