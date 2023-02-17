import smartpy as sp

@sp.module
def main():

    class NftForSale(sp.Contract):
       def __init__(self, owner, metadata, price):
           self.data.owner = owner
           self.data.metadata = metadata
           self.data.price = price
    
       @sp.entrypoint
       def buy(self):
           assert sp.amount == self.data.price, "wrong price"
           sp.send(self.data.owner, self.data.price)
           self.data.price += sp.split_tokens(self.data.price, 10, 100)
           self.data.owner = sp.sender
        
    class NftWrapperContract(sp.Contract):
        def __init__(self, allowSales, owner, price):
            self.data.allowSales = allowSales
            self.data.price = price
            self.data.owner_wrapper = owner
    
        @sp.entrypoint
        def buyNFT(self, nft_address):
            assert sp.sender == self.data.owner_wrapper
            nft_contract = sp.contract(sp.unit, nft_address, entrypoint="buy").unwrap_some()
            sp.transfer((), sp.amount, nft_contract)
            
        @sp.entrypoint
        def setPrice(self, new_price):
            assert sp.sender == self.data.owner_wrapper
            self.data.price = new_price
    
        @sp.entrypoint
        def buy(self):
            assert sp.amount == self.data.price
            sp.send(self.data.owner_wrapper, self.data.price)
            self.data.owner_wrapper = sp.sender
            
        @sp.entrypoint
        def setAllowSale(self, new_boolean):
            assert sp.sender == self.data.owner_wrapper
            self.data.allowSales = new_boolean
    
        @sp.entrypoint
        def default(self):
            assert self.data.allowSales

@sp.add_test(name="test Wrapped Nft")
def test():
   alice = sp.test_account("alice").address
   bob = sp.test_account("bob").address
   eve = sp.test_account("eve").address
   dan = sp.test_account("dan").address
   c1 = main.NftForSale(owner = alice, metadata = "Gwen's first NFT", price = sp.mutez(5000000))
   c2 = main.NftWrapperContract(allowSales = sp.bool(True), price = sp.mutez(5000000), owner = bob)
   scenario = sp.test_scenario(main)
   scenario +=c1
   scenario +=c2
   scenario.h3("testing buy NFT from NftforSale")
   c1.buy().run(sender = dan, amount = sp.tez(5))
   scenario.verify(c1.data.price == sp.mutez(5500000))
   c1.buy().run(sender = alice, amount = sp.mutez(5500000))
   scenario.h3("testing buy NFT with Wrapper")
   c2.buyNFT(c1.address).run(sender = bob, amount=sp.mutez(6050000))
   scenario.verify(c1.data.price == sp.mutez(6655000) )
   scenario.verify(c1.data.owner == c2.address)
   scenario.h3("testing allowSales")
   c2.setAllowSale(False).run(sender = eve, valid = False)
   c2.setAllowSale(False).run(sender = bob)
   scenario.verify(c1.data.price == sp.mutez(6655000))
   c1.buy().run(sender = dan, amount = sp.mutez(6655000), valid = False)
   scenario.h3("testing setPrice NFT Wrapper")
   c2.setPrice(sp.tez(5)).run(sender = eve, valid = False)
   c2.setPrice(sp.tez(5)).run(sender = bob)
   c2.buy().run(sender = alice, amount = sp.tez(5))
   scenario.verify(c2.data.price == sp.tez(5))
   scenario.verify(c2.data.owner_wrapper == alice)
   scenario.h3("trying to buy nft from NFTforSale while not possible") 
   scenario.h3("buying NftWrapper i.e. buying NFT at nftwrapper set_price()")
   c2.setAllowSale(True).run(sender = alice)
   c1.buy().run(sender = dan, amount = sp.mutez(6655000))
   scenario.verify(c1.data.owner == dan)
