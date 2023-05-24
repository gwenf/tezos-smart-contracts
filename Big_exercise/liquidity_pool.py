import smartpy as sp

@sp.module
def main():
    
    class LiquidityPool(sp.Contract):
        def __init__(self, owner, ledger):
            self.data.ledger = ledger
            self.data.owner = owner
            self.data.K = sp.tez(0)
            self.data.tokensOwned = sp.nat(0)
            self.data.ledger_contract_opt = None
            # tokensOwned * sp.balance = K -> should always be true

        @sp.entrypoint
        def provide_liquidity(self, depositedTokens):
            assert sp.sender == self.data.owner
            assert self.data.K == sp.tez(0)
            self.data.K = sp.mul(sp.balance, depositedTokens)

            self.data.tokensOwned = depositedTokens

            self.data.ledger_contract_opt = sp.contract(paramType, self.data.ledger, entrypoint="transfer")
            sp.transfer(sp.record(source = sp.sender, destination = sp.self_address(), amount = depositedTokens), sp.tez(0), self.data.ledger_contract_opt.unwrap_some())
            
        @sp.entrypoint
        def withdraw_liquidity(self):
            assert sp.sender == self.data.owner
            sp.send(sp.sender, sp.balance)
            
            sp.transfer(sp.record(source = sp.self_address(), destination = sp.sender, amount = self.data.tokensOwned), sp.tez(0), self.data.ledger_contract_opt.unwrap_some())

            self.data.tokensOwned = sp.nat(0)
            self.data.K = sp.tez(0)

        
        @sp.entrypoint
        def sellTokens(self, nbTokensSold, minTezRequested):
            ratio = sp.ediv(self.data.K, self.data.tokensOwned + nbTokensSold).unwrap_some()
            tezObtained = sp.balance - sp.fst(ratio)
            assert tezObtained >= minTezRequested

            sp.transfer(sp.record(source = sp.sender, destination = sp.self_address(), amount = nbTokensSold), sp.tez(0), self.data.ledger_contract_opt.unwrap_some())

            self.data.tokensOwned += nbTokensSold
            sp.send(sp.sender, tezObtained)

        @sp.entrypoint
        def buyTokens(self, minTokensBought):
            sp.cast(minTokensBought, sp.nat)
            tokensObtained = sp.as_nat(self.data.tokensOwned - sp.fst(sp.ediv(self.data.K, sp.balance).unwrap_some()))
            assert tokensObtained >= minTokensBought

            sp.transfer(sp.record(source = sp.self_address(), destination = sp.sender, amount = tokensObtained), sp.tez(0), self.data.ledger_contract_opt.unwrap_some())

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
