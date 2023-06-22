import smartpy as sp

@sp.module
def main():
    
    class LiquidityPool(sp.Contract):
        def __init__(self, owner, ledger):
            self.data.ledger = ledger
            self.data.owner = owner
            self.data.K = sp.tez(0)
            self.data.tokens_owned = sp.nat(0)
            self.data.ledger_contract_opt = None
            # tokens_owned * sp.balance = K -> should always be true

        @sp.entrypoint
        def provide_liquidity(self, deposited_tokens):
            assert sp.sender == self.data.owner
            assert self.data.K == sp.tez(0)
            self.data.K = sp.mul(sp.balance, deposited_tokens)

            self.data.tokens_owned = deposited_tokens

            self.data.ledger_contract_opt = sp.contract(paramType, self.data.ledger, entrypoint="transfer")
            sp.transfer(sp.record(source = sp.sender, destination = sp.self_address(), amount = deposited_tokens), sp.tez(0), self.data.ledger_contract_opt.unwrap_some())
            
        @sp.entrypoint
        def withdraw_liquidity(self):
            assert sp.sender == self.data.owner
            sp.send(sp.sender, sp.balance)
            
            sp.transfer(sp.record(source = sp.self_address(), destination = sp.sender, amount = self.data.tokens_owned), sp.tez(0), self.data.ledger_contract_opt.unwrap_some())

            self.data.tokens_owned = sp.nat(0)
            self.data.K = sp.tez(0)

        
        @sp.entrypoint
        def sell_tokens(self, nb_tokens_sold, min_tez_requested):
            ratio = sp.ediv(self.data.K, self.data.tokens_owned + nb_tokens_sold).unwrap_some()
            tez_obtained = sp.balance - sp.fst(ratio)
            assert tez_obtained >= min_tez_requested

            sp.transfer(sp.record(source = sp.sender, destination = sp.self_address(), amount = nb_tokens_sold), sp.tez(0), self.data.ledger_contract_opt.unwrap_some())

            self.data.tokens_owned += nb_tokens_sold
            sp.send(sp.sender, tez_obtained)

        @sp.entrypoint
        def buy_tokens(self, min_tokens_bought):
            sp.cast(min_tokens_bought, sp.nat)
            tokens_obtained = sp.as_nat(self.data.tokens_owned - sp.fst(sp.ediv(self.data.K, sp.balance).unwrap_some()))
            assert tokens_obtained >= min_tokens_bought

            sp.transfer(sp.record(source = sp.self_address(), destination = sp.sender, amount = tokens_obtained), sp.tez(0), self.data.ledger_contract_opt.unwrap_some())

            self.data.tokens_owned = sp.as_nat(self.data.tokens_owned - tokens_obtained)
            

        @sp.onchain_view
        def get_token_price(self):
            # returns what we would get if we sold one token
            ratio1 = sp.ediv(self.data.K, self.data.tokens_owned).unwrap_some()
            ratio2 = sp.ediv(self.data.K, sp.as_nat(self.data.tokens_owned - 1)).unwrap_some()
            trace ("The current value of K is:")
            trace(self.data.K)
            trace("The pool owns this amount of tokens:")
            trace(self.data.tokens_owned)
            trace("The balance of the pool is:")
            trace(sp.balance)
            trace("The ratios before and after a potential purchase of 1 token would be:")
            trace(ratio1)
            trace(ratio2)
            token_price = sp.fst(ratio2) - sp.fst(ratio1)
            trace("The price of the token returned is:")
            trace(token_price)
            return token_price
