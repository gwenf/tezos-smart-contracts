import smartpy as sp

@sp.module
def main():

    transaction_type:type = sp.record(to_ = sp.address, token_id = sp.nat, amount = sp.nat).layout(("to_", ("token_id", "amount")))
    operator_type:type = sp.record(owner = sp.address,
                                   operator = sp.address,
                                   token_id = sp.nat
                                  ).layout(("owner", ("operator", "token_id")))
    
    my_variant:type = sp.variant(add_operator = sp.record(owner = sp.address, operator = sp.address, token_id = sp.address),
               remove_operator = sp.record(owner = sp.address, operator = sp.address, token_id = sp.address))
    
    class FA2Token(sp.Contract):
        
        def __init__(self):
            self.data.tokens = sp.big_map()
            self.data.nextTokenID = sp.nat(1)

        @sp.entrypoint
        def mint(self, metadata):
            operators = sp.set()
            sp.cast(operators, sp.set[operator_type])
            self.data.tokens[self.data.nextTokenID] = sp.record(owner = sp.sender, metadata = metadata, operators = sp.set())
            self.data.nextTokenID += 1

        @sp.entrypoint
        def balance_of(self, callback, requests):
            sp.cast(requests, sp.list[sp.record(owner = sp.address, token_id = sp.nat)])
            result = []
            for request in requests:
                assert self.data.tokens.contains(request.token_id), "FA2_TOKEN_UNDEFINED"
                token = self.data.tokens[request.token_id]
                balance = 0
                if token.owner == request.owner:
                    balance = 1
                result = sp.cons(sp.record(request = sp.record(owner = request.owner, token_id =request.token_id),
                                           balance = 1),
                                 result)

            sp.transfer(result, sp.mutez(0), callback)
        
        @sp.entrypoint
        def update_operators(self, actions):
            for action in actions:
                if action.is_variant.add_operator():
                    operator_data = action.unwrap.add_operator()
                    sp.cast(operator_data, operator_type)
                    token = self.data.tokens[operator_data.token_id]
                    assert token.owner == sp.sender, "FA2_NOT_OWNER"
                    assert operator_data.owner == sp.sender, "FA2_NOT_OWNER"
                    token.operators.add(operator_data.operator)
                    self.data.tokens[operator_data.token_id] = token
                else:
                    operator_data = action.unwrap.remove_operator()
                    sp.cast(operator_data, operator_type)
                    token = self.data.tokens[operator_data.token_id]
                    assert token.owner == sp.sender, "FA2_NOT_OWNER"
                    assert operator_data.owner == sp.sender, "FA2_NOT_OWNER"
                    token.operators.remove(operator_data.operator)
                    self.data.tokens[operator_data.token_id] = token
                
        @sp.entrypoint
        def transfer(self, transfers):
            for transf in transfers:
                assert sp.sender == transf.from_
                for tx in transf.txs:
                    sp.cast(tx, transaction_type)
                    assert tx.amount == sp.nat(1)
                    token = self.data.tokens[tx.token_id]
                    assert token.operators.contains(sp.sender)
                    self.data.tokens[tx.token_id].owner = tx.to_

    class Marketplace(sp.Contract):
        def __init__(self, contract_address):
            self.data.contract_address = contract_address
            self.data.offers = sp.big_map({})
            self.data.nextOfferID = 1
     
        @sp.entrypoint
        def new_offer(self, tokenID, price):
           self.data.offers[self.data.nextOfferID] = sp.record(seller = sp.sender, tokenID = tokenID, price = price)
           self.data.nextOfferID += 1
        
        @sp.entrypoint
        def buy(self, idOffer):
            offer = self.data.offers[idOffer]
            assert offer.price == sp.amount

            token_contract = sp.contract(sp.list[sp.record(from_ = sp.address,
                                                           txs = sp.list[sp.record(to_ = sp.address, token_id = sp.nat, amount = sp.nat)])],
                                          self.data.contract_address,
                                          entrypoint="transfer").unwrap_some()

            tx = sp.record(to_ = sp.sender, token_id = offer.tokenID, amount = sp.nat(1))
            sp.cast(tx, transaction_type)
            sp.transfer([sp.record(from_ = sp.self_address(), txs = [tx])], # TODO: undertand what from_ is for
                        sp.tez(0),
                        token_contract)

            sp.send(offer.seller, offer.price)


@sp.add_test(name="FA2 and basic marketplace")
def test():
    alice = sp.test_account("Alice")
    bob = sp.test_account("Bob")
    eve = sp.test_account("Eve")
    axel = sp.test_account("Axel")
    scenario = sp.test_scenario(main)
    ledger = main.FA2Token()
    scenario += ledger
    marketplace = main.Marketplace(ledger.address)
    scenario += marketplace
    ledger.mint("Alice NFT 1").run(sender = alice)
    
    marketplace.new_offer(tokenID = sp.nat(1), price = sp.tez(10)).run(sender = alice)

    #ledger.update_operators([sp.variant.add_operator(sp.record(owner = sp.alice, operator = marketplace.address, token_id = 1))])
    operator_data = sp.record(owner = alice.address, operator = marketplace.address, token_id = 1)
    ledger.update_operators([sp.variant("add_operator", operator_data)]).run(sender=alice)

    marketplace.buy(1).run(sender = bob, amount = sp.tez(10))
