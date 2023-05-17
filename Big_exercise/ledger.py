import smartpy as sp

@sp.module
def main():

    paramType:type = sp.record(source = sp.address, destination = sp.address, amount = sp.nat)

    class Ledger(sp.Contract):
        def __init__(self, owner, total_supply):
            self.data.balances = sp.big_map({ owner : total_supply })
            self.data.operators = sp.big_map({ owner: sp.set(owner)})
          
    
        @sp.entrypoint
        def transfer(self, source, destination, amount):
            assert self.data.operators[source].contains(sp.sender)
            assert self.data.balances[source] >= amount
            self.data.balances[source] = sp.as_nat(self.data.balances[source] - amount)
            if not self.data.balances.contains(destination):
                self.data.balances[destination] = sp.nat(0)
                if not self.data.operators.contains(sp.sender):
                    self.data.operators[destination] = sp.set(destination)
            self.data.balances[destination] += amount

        @sp.onchain_view
        def get_balance(self, user):
            sp.cast(user, sp.address)
            return self.data.balances[user]

        @sp.entrypoint
        def add_operator(self, operator):
            if not self.data.operators.contains(sp.sender):
                self.data.operators[sp.sender] = sp.set(sp.sender)
            self.data.operators[sp.sender].add(operator)

        @sp.entrypoint
        def del_operator(self, operator):
            self.data.operators[sp.sender].remove(operator)
