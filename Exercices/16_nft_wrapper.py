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
    def __init__(self, boolean, owner, price):
        self.init(allowSales = boolean, price = price, owner_wrapper = owner)


    #  buyNft(nft: address)
    #  Call the buy entry point of the nft contract
    @sp.entry_point
    def buyNFT(self, nft_address):
        sp.verify(sp.sender == self.data.owner)
        nft_contract = sp.contract(sp.TUnit, nft_address, entry_point="buy").open_some()
        sp.transfer(sp.unit, sp.amount, nft_contract)
        
#     setPrice(newPrice: tez)
#     Verify that the caller is the owner
#     Replace price with newPrice in the storage
    @sp.entry_point
    def setPrice(self, new_price):
        sp.verify(sp.sender == self.data.owner)
        self.data.price = new_price

#     buy()
#     Verify that the transferred amount equals the price
#     Create a transaction that sends price tez to the owner
#     Replace owner with the caller
    @sp.entry_point
    def buy(self):
        sp.verify(sp.amount == self.data.price)
        sp.send(owner, self.data.price)
        self.data.owner = sp.sender
        
#     setAllowSale(newValue: boolean)
#     Verify that the caller is the owner
#     Replace allowSales with newValue in the storage

    @sp.entry_point
    def setAllowSale(self, new_boolean):
        sp.verify(sp.sender == self.data.owner)
        self.data.allowSales = new_boolean

    #default()
    #Verify that allowSales is true
    @sp.entry_point
    def default(self):
        sp.verify(self.data.allowSales == True)

@sp.add_test(name="test Wrapped Nft")
def test():
   alice = sp.test_account("alice").address
   bob = sp.test_account("bob").address
   eve = sp.test_account("eve").address
   c1 = NftForSale(owner = alice, metadata = "Gwen's first NFT", price = sp.mutez(5000000))
   c2 = NftWrapperContract(allowSales = sp.bool(True), price = sp.mutez(5000000), owner_wrapper = bob)
   scenario = sp.test_scenario()
   scenario +=c1
   scenario +=c2
   scenario.h3(" Testing set_price entrypoint")
   #testing set price
   c1.set_price(sp.mutez(7000000)).run(sender = alice)
   c2.buyNFT(c1.address).run(sender = bob, amount=sp.tez(7))