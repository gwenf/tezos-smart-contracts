import smartpy as sp

@sp.module
def main():

    paramType:type = sp.record(tokenID = sp.int, newOwner = sp.address)
    
    class Ledger(sp.Contract):
        
        def __init__(self, admin):
            self.data.admin = admin
            self.data.tokens = sp.big_map()
            self.data.nextTokenID = 1

        @sp.entrypoint
        def mint(self, metadata):
            self.data.tokens[self.data.nextTokenID] = sp.record(owner = sp.sender, metadata = metadata)
            self.data.nextTokenID += 1

        @sp.onchain_view()
        def getTokenOwner(self, tokenID):
            sp.cast(tokenID, sp.int)
            return self.data.tokens[tokenID].owner

        @sp.entrypoint
        def changeOwner(self, tokenID, newOwner):
            assert sp.sender == self.data.admin
            self.data.tokens[tokenID].owner = newOwner


    class Marketplace(sp.Contract):
        def __init__(self):
            self.data.offers = sp.big_map({})
            self.data.nextOfferID = 1
     
        @sp.entrypoint
        def new_offer(self, sold_tokens, bought_tokens):
           self.data.offers[self.data.nextOfferID] = sp.record(seller = sp.sender,
                                                            sold_tokens = sold_tokens,
                                                            bought_tokens = bought_tokens)
           self.data.nextOfferID += 1
        
        @sp.entrypoint
        def accept_offer(self, idOffer):
            offer = self.data.offers[idOffer]

            for sold_token in offer.sold_tokens:
                owner = sp.view("getTokenOwner", sold_token.contract_address, sold_token.tokenID, sp.address).unwrap_some()
                assert owner == offer.seller
                ledger_contract = sp.contract(paramType, sold_token.contract_address, entrypoint="changeOwner").unwrap_some()
                sp.transfer(sp.record(tokenID = sold_token.tokenID, newOwner = sp.sender), sp.tez(0), ledger_contract)

            for bought_token in offer.bought_tokens:
                owner = sp.view("getTokenOwner", bought_token.contract_address, bought_token.tokenID, sp.address).unwrap_some()
                assert owner == sp.sender
                ledger_contract = sp.contract(paramType, bought_token.contract_address, entrypoint="changeOwner").unwrap_some()
                sp.transfer(sp.record(tokenID = bought_token.tokenID, newOwner = offer.seller), sp.tez(0), ledger_contract)

            del self.data.offers[idOffer]    
       
@sp.add_test(name="testing truly endless wall")
def test():
    alice = sp.test_account("Alice")
    bob = sp.test_account("Bob")
    eve = sp.test_account("Eve")
    axel = sp.test_account("Axel")
    scenario = sp.test_scenario(main)
    marketplace = main.Marketplace()
    scenario += marketplace
    ledger1 = main.Ledger(marketplace.address)
    scenario += ledger1
    ledger2 = main.Ledger(marketplace.address)
    scenario += ledger2
    ledger1.mint("Alice NFT 1").run(sender = alice)
    ledger2.mint("Alice NFT 2").run(sender = alice)
    ledger1.mint("Bob NFT 1").run(sender = bob)
    ledger2.mint("Bob NFT 2").run(sender = bob)
    ledger2.mint("Bob NFT 3").run(sender = bob)
    
    marketplace.new_offer(sold_tokens = [
                            sp.record(contract_address = ledger1.address, tokenID = 1),
                            sp.record(contract_address = ledger2.address, tokenID = 1),
                          ],
                          bought_tokens = [
                            sp.record(contract_address = ledger1.address, tokenID = 2),
                            sp.record(contract_address = ledger2.address, tokenID = 2),
                            sp.record(contract_address = ledger2.address, tokenID = 3),
                          ]
                         ).run(sender = alice)
    marketplace.accept_offer(1).run(sender = bob)
