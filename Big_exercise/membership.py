import smartpy as sp

@sp.module
def main():
  
class Membership(sp.Contract):
        def __init__(self, membership_price, owner, ledger, liquidity_pool):
            self.data.owner = owner
            self.data.membership_price = membership_price
            self.data.members = sp.set()
            self.data.ledger = ledger
            self.data.liquidity_pool = liquidity_pool

        @sp.entrypoint
        def join(self):
            assert sp.amount == self.data.membership_price
            self.data.members.add(sp.sender)
            sp.send(self.data.owner, sp.amount)
            self.data.members.add(sp.sender)

        @sp.entrypoint
        def join_with_tokens(self, nb_tokens):
            sp.cast(nb_tokens, sp.nat)
            token_price =  sp.view("get_token_price", self.data.liquidity_pool, (), sp.mutez).unwrap_some();
            assert sp.mul(token_price, nb_tokens) > self.data.membership_price
            ledger_contract = sp.contract(paramType, self.data.ledger, entrypoint="transfer").unwrap_some()
            sp.transfer(sp.record(source = sp.sender, destination = self.data.owner, amount = nb_tokens), sp.tez(0), ledger_contract)
            self.data.members.add(sp.sender)
