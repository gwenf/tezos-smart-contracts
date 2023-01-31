import smartpy as sp

class YieldFarming(sp.Contract):
    def __init__(self, owner, lender, annual_yield_rate, ramp_up_duration):
        self.init(owner = owner, 
                  lender = lender, 
                  deposit_amount = sp.tez(0), 
                  deposit_date = sp.timestamp(0),
                  annual_yield_rate = annual_yield_rate, 
                  ramp_up_duration = ramp_up_duration)


    @sp.entry_point
    def owner_withdraw(self, requestedAmount):
        sp.verify(sp.sender == self.data.owner)
        one_year_yield = sp.split_tokens(self.data.deposit_amount, self.data.annual_yield_rate, 100)
        reserve = self.data.deposit_amount + one_year_yield
        sp.verify(sp.balance - requestedAmount >= reserve)
        sp.send(sp.sender, requestedAmount)
        
    @sp.entry_point
    def set_delegate(self, delegate_option):
        sp.verify(sp.sender == self.data.owner)
        sp.set_delegate(delegate_option)

    @sp.entry_point
    def deposit(self):
        sp.verify(sp.sender == self.data.lender)
        sp.verify(self.data.deposit_amount == sp.tez(0))
        self.data.deposit_amount = sp.amount
        self.data.deposit_date = sp.now
        
        
    @sp.entry_point
    def withdraw(self):
        sp.verify(sp.sender == self.data.lender)
        duration = sp.is_nat(sp.now - (self.data.deposit_date.add_seconds(self.data.ramp_up_duration))).open_some()
        one_year= 365*24*3600
        one_year_yield = sp.mul(self.data.deposit_amount, self.data.annual_yield_rate)
        duration_yield = sp.split_tokens(one_year_yield, duration, one_year)
        sp.send(sp.sender, self.data.deposit_amount + duration_yield )
        self.data.deposit_amount = sp.tez(0)
        self.data.deposit_date = sp.timestamp(0)

    @sp.entry_point
    def default(self):
        pass

@sp.add_test(name = "Yield Farming")
def test():
    owner = sp.test_account("owner").address
    alice = sp.test_account("Alice").address
    bob = sp.test_account("Bob").address
    eve = sp.test_account("Eve").address
    c1 = YieldFarming(owner = owner, lender = alice, annual_yield_rate = 4, ramp_up_duration = 3600*24*21)
    scenario = sp.test_scenario()
    scenario += c1
    scenario.h3("Testing entrypoints")
    c1.default().run(sender=owner, amount= sp.tez(5))
    c1.deposit().run(sender=alice, amount = sp.tez(100))
    c1.withdraw().run(sender=alice, now = sp.timestamp(3600*24*21 + 100))
    c1.owner_withdraw(sp.tez(1)).run(sender=owner)
