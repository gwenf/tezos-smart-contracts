import smartpy as sp

@sp.module
def main():
  
class Membership(sp.Contract):
        def __init__(self, membership_price, owner, ledger, liquidityPool):
            self.data.owner = owner
            self.data.membership_price = membership_price
            self.data.members = sp.set()
            self.data.ledger = ledger
            self.data.liquidityPool = liquidityPool

        @sp.entrypoint
        def join(self):
            assert sp.amount == self.data.membership_price
            self.data.members.add(sp.sender)
            sp.send(self.data.owner, sp.amount)
            self.data.members.add(sp.sender)

        @sp.entrypoint
        def join_with_tokens(self, nbTokens):
            sp.cast(nbTokens, sp.nat)
            tokenPrice =  sp.view("get_token_price", self.data.liquidityPool, (), sp.mutez).unwrap_some();
            assert sp.mul(tokenPrice, nbTokens) > self.data.membership_price
            ledger_contract = sp.contract(paramType, self.data.ledger, entrypoint="transfer").unwrap_some()
            sp.transfer(sp.record(source = sp.sender, destination = self.data.owner, amount = nbTokens), sp.tez(0), ledger_contract)
            self.data.members.add(sp.sender)
