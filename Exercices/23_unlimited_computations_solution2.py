import smartpy as sp

@sp.module
def main():
    class TimeSafe(sp.Contract):
    
        def __init__(self, owner):
            self.data.owner = owner
            self.data.deposits = sp.big_map({})
            self.data.counter = sp.nat(0)

        @sp.entrypoint
        def deposit(self, deadline):
            deposit = sp.record(source=sp.sender, deadline=deadline, amount=sp.amount)
            self.data.deposits[self.data.counter] = deposit
            self.data.counter += 1

        @sp.entrypoint
        def withdraw(self, requested_items):
            assert sp.sender == self.data.owner
            total = sp.tez(0)
            for key in requested_items:
                if self.data.deposits.contains(key):
                    deposit = self.data.deposits[key]
                    if deposit.deadline <= sp.now:
                        total += deposit.amount
                        del self.data.deposits[key]
            sp.send(sp.sender, total)
                   

@sp.add_test(name='Testing extortion attack')
def test():
    alice = sp.test_account("alice").address
    bob = sp.test_account("bob").address
    carl = sp.test_account("carl").address
    scenario = sp.test_scenario(main)
    time_safe_contract = main.TimeSafe(alice)
    scenario += time_safe_contract
    time_safe_contract.deposit(sp.timestamp(100)).run(sender = bob, amount = sp.tez(10))
    time_safe_contract.deposit(sp.timestamp(200)).run(sender = carl, amount = sp.tez(20))
    time_safe_contract.withdraw([0,1]).run(sender = alice, now = sp.timestamp(0))
    scenario.verify(time_safe_contract.balance == sp.tez(30))
    time_safe_contract.withdraw([0,1]).run(sender = alice, now = sp.timestamp(100))
    scenario.verify(time_safe_contract.balance == sp.tez(20))
    time_safe_contract.withdraw([1]).run(sender = alice, now = sp.timestamp(2000))
    scenario.verify(time_safe_contract.balance == sp.tez(0))
