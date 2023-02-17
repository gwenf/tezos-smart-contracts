import smartpy as sp

@sp.module
def main():

    class YieldFarming(sp.Contract):
        def __init__(self, owner, lender, annual_yield_rate, ramp_up_duration):
            self.data.owner = owner
            self.data.lender = lender
            self.data.deposit_amount = sp.tez(0)
            self.data.deposit_date = sp.timestamp(0)
            self.data.annual_yield_rate = annual_yield_rate
            self.data.ramp_up_duration = ramp_up_duration
    
    
        @sp.entrypoint
        def owner_withdraw(self, requestedAmount):
            assert sp.sender == self.data.owner
            one_year_yield = sp.split_tokens(self.data.deposit_amount, self.data.annual_yield_rate, 100)
            reserve = self.data.deposit_amount + one_year_yield
            assert sp.balance - requestedAmount >= reserve
            sp.send(sp.sender, requestedAmount)
            
        @sp.entrypoint
        def set_delegate(self, delegate_option):
            assert sp.sender == self.data.owner
            sp.set_delegate(delegate_option)
    
        @sp.entrypoint
        def deposit(self):
            assert sp.sender == self.data.lender
            assert self.data.deposit_amount == sp.tez(0)
            self.data.deposit_amount = sp.amount
            self.data.deposit_date = sp.now
            
            
        @sp.entrypoint
        def withdraw(self):
            assert sp.sender == self.data.lender
            duration = sp.is_nat(sp.now - (sp.add_seconds(self.data.deposit_date, self.data.ramp_up_duration))).unwrap_some()
            one_year= 365*24*3600
            one_year_yield = sp.mul(self.data.deposit_amount, self.data.annual_yield_rate)
            duration_yield = sp.split_tokens(one_year_yield, duration, one_year*100)
            sp.send(sp.sender, self.data.deposit_amount + duration_yield )
            self.data.deposit_amount = sp.tez(0)
            self.data.deposit_date = sp.timestamp(0)
    
        @sp.entrypoint
        def default(self):
            pass

@sp.add_test(name = "Yield Farming")
def test():
    owner = sp.test_account("owner").address
    alice = sp.test_account("Alice").address
    bob = sp.test_account("Bob").address
    eve = sp.test_account("Eve").address
    delegate = sp.test_account("delegate")
    voting_powers = {
        delegate.public_key_hash: 0,
    }
    c1 = main.YieldFarming(owner = owner, lender = alice, annual_yield_rate = 4, ramp_up_duration = 3600*24*21)
    scenario = sp.test_scenario(main)
    scenario += c1
    scenario.h3("Testing default entrypoint")
    c1.default().run(sender=owner, amount= sp.tez(5))
    scenario.verify(c1.balance==sp.tez(5))
    scenario.h3("Testing deposit entrypoint")
    c1.deposit().run(sender=alice, amount = sp.tez(100))
    scenario.verify(c1.data.deposit_amount == sp.tez(100))
    scenario.verify(c1.balance==sp.tez(105))
    c1.deposit().run(sender=alice, amount = sp.tez(100), valid = False)
    scenario.h3("Testing withdraw entrypoint")
    scenario.h3("Testing owner_withdraw entrypoint")
    c1.owner_withdraw(sp.tez(1)).run(sender=bob, valid = False)
    c1.owner_withdraw(sp.mutez(1000001)).run(sender=owner, valid = False)
    c1.owner_withdraw(sp.tez(1)).run(sender=owner)
    scenario.h3("Testing set delegate")
    c1.set_delegate(sp.some(delegate.public_key_hash)).run(sender = owner, voting_powers = voting_powers)
    c1.withdraw().run(sender=alice, now = sp.timestamp(3600*24*21 + 3600*24*365 ))
    
