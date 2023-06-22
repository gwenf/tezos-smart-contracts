import smartpy as sp

@sp.module
def main():
    class TimeSafe(sp.Contract):
    
        def __init__(self, owner):
            self.data.owner = owner
            self.data.deposits = []

        @sp.entrypoint
        def deposit(self, deadline):
            deposit = sp.record(source=sp.sender, deadline=deadline, amount=sp.amount)
            self.data.deposits = sp.cons(deposit, self.data.deposits)

        @sp.entrypoint
        def withdraw(self):
            assert sp.sender == self.data.owner
            remaining_deposits = []
            total = sp.tez(0)
            for deposit in self.data.deposits:
                if deposit.deadline <= sp.now:
                    total += deposit.amount
                else:
                    remaining_deposits = sp.cons(deposit, remaining_deposits)
            self.data.deposits = remaining_deposits
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
    time_safe_contract.withdraw().run(sender = alice, now = sp.timestamp(0))
    scenario.verify(time_safe_contract.balance == sp.tez(30))
    time_safe_contract.withdraw().run(sender = alice, now = sp.timestamp(100))
    scenario.verify(time_safe_contract.balance == sp.tez(20))
    time_safe_contract.withdraw().run(sender = alice, now = sp.timestamp(2000))
    scenario.verify(time_safe_contract.balance == sp.tez(0))
