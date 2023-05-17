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
    
    class LiquidityPool(sp.Contract):
        def __init__(self, owner, ledger):
            self.data.ledger = ledger
            self.data.ledger_transfer = None
            self.data.owner = owner
            self.data.K = sp.tez(0)
            self.data.tokensOwned = sp.nat(0)
            # tokensOwned * sp.balance = K -> should always be true

        @sp.entrypoint
        def provide_liquidity(self, depositedTokens):
            assert sp.sender == self.data.owner
            assert self.data.K == sp.tez(0)
            self.data.K = sp.mul(sp.balance, depositedTokens)

            self.data.tokensOwned = depositedTokens

            self.data.ledger_transfer = sp.contract(paramType, self.data.ledger, entrypoint="transfer")
            sp.transfer(sp.record(source = sp.sender, destination = sp.self_address(), amount = depositedTokens), sp.tez(0), self.data.ledger_transfer.unwrap_some())
            
        @sp.entrypoint
        def withdraw_liquidity(self):
            assert sp.sender == self.data.owner
            sp.send(sp.sender, sp.balance)
            
            sp.transfer(sp.record(source = sp.self_address(), destination = sp.sender, amount = self.data.tokensOwned), sp.tez(0), self.data.ledger_transfer.unwrap_some())

            self.data.tokensOwned = sp.nat(0)
            self.data.K = sp.tez(0)

        
        @sp.entrypoint
        def sellTokens(self, nbTokensSold, minTezRequested):
            ratio = sp.ediv(self.data.K, self.data.tokensOwned + nbTokensSold).unwrap_some()
            tezObtained = sp.balance - sp.fst(ratio)
            assert tezObtained >= minTezRequested

            sp.transfer(sp.record(source = sp.sender, destination = sp.self_address(), amount = nbTokensSold), sp.tez(0), self.data.ledger_transfer.unwrap_some())

            self.data.tokensOwned += nbTokensSold
            sp.send(sp.sender, tezObtained)

        @sp.entrypoint
        def buyTokens(self, minTokensBought):
            sp.cast(minTokensBought, sp.nat)
            tokensObtained = sp.as_nat(self.data.tokensOwned - sp.fst(sp.ediv(self.data.K, sp.balance).unwrap_some()))
            assert tokensObtained >= minTokensBought

            sp.transfer(sp.record(source = sp.self_address(), destination = sp.sender, amount = tokensObtained), sp.tez(0), self.data.ledger_transfer.unwrap_some())

            self.data.tokensOwned = sp.as_nat(self.data.tokensOwned - tokensObtained)
            

        @sp.onchain_view
        def get_token_price(self):
            # returns what we would get if we sold one token
            ratio1 = sp.ediv(self.data.K, self.data.tokensOwned).unwrap_some()
            ratio2 = sp.ediv(self.data.K, sp.as_nat(self.data.tokensOwned - 1)).unwrap_some()
            trace ("The current value of K is:")
            trace(self.data.K)
            trace("The pool owns this amount of tokens:")
            trace(self.data.tokensOwned)
            trace("The balance of the pool is:")
            trace(sp.balance)
            trace("The ratios before and after a potential purchase of 1 token would be:")
            trace(ratio1)
            trace(ratio2)
            tokenPrice = sp.fst(ratio2) - sp.fst(ratio1)
            trace("The price of the token returned is:")
            trace(tokenPrice)
            return tokenPrice
