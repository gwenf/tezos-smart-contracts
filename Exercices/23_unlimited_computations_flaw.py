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
            remainingDeposits = []
            total = sp.tez(0)
            for deposit in self.data.deposits:
                if deposit.deadline <= sp.now:
                    total += deposit.amount
                else:
                    remainingDeposits = sp.cons(deposit, remainingDeposits)
            self.data.deposits = remainingDeposits
            sp.send(sp.sender, total)
                   

@sp.add_test(name='Testing extortion attack')
def test():
    alice = sp.test_account("alice").address
    bob = sp.test_account("bob").address
    carl = sp.test_account("carl").address
    scenario = sp.test_scenario(main)
    timeSafeContract = main.TimeSafe(alice)
    scenario += timeSafeContract
    timeSafeContract.deposit(sp.timestamp(100)).run(sender = bob, amount = sp.tez(10))
    timeSafeContract.deposit(sp.timestamp(200)).run(sender = carl, amount = sp.tez(20))
    timeSafeContract.withdraw().run(sender = alice, now = sp.timestamp(0))
    # TODO: verify balance 30 tez
    timeSafeContract.withdraw().run(sender = alice, now = sp.timestamp(100))
    # TODO: verify balance 20 tez
    timeSafeContract.withdraw().run(sender = alice, now = sp.timestamp(2000))
    # TODO: verify balance 0 tez
    
    
#Solution 2:
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
        def withdraw(self):
            assert sp.sender == self.data.owner
            total = sp.tez(0)
            for key in range(self.data.counter):
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
    timeSafeContract = main.TimeSafe(alice)
    scenario += timeSafeContract
    timeSafeContract.deposit(sp.timestamp(100)).run(sender = bob, amount = sp.tez(10))
    timeSafeContract.deposit(sp.timestamp(200)).run(sender = carl, amount = sp.tez(20))
    timeSafeContract.withdraw().run(sender = alice, now = sp.timestamp(0))
    # TODO: verify balance 30 tez
    timeSafeContract.withdraw().run(sender = alice, now = sp.timestamp(100))
    # TODO: verify balance 20 tez
    timeSafeContract.withdraw().run(sender = alice, now = sp.timestamp(2000))
    # TODO: verify balance 0 tez
    
    
    #Solution 3, the good one:
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
        def withdraw(self, requestedItems):
            assert sp.sender == self.data.owner
            total = sp.tez(0)
            for key in requestedItems:
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
    timeSafeContract = main.TimeSafe(alice)
    scenario += timeSafeContract
    timeSafeContract.deposit(sp.timestamp(100)).run(sender = bob, amount = sp.tez(10))
    timeSafeContract.deposit(sp.timestamp(200)).run(sender = carl, amount = sp.tez(20))
    timeSafeContract.withdraw([0,1]).run(sender = alice, now = sp.timestamp(0))
    # TODO: verify balance 30 tez
    timeSafeContract.withdraw([0,1]).run(sender = alice, now = sp.timestamp(100))
    # TODO: verify balance 20 tez
    timeSafeContract.withdraw([1]).run(sender = alice, now = sp.timestamp(2000))
    # TODO: verify balance 0 tez