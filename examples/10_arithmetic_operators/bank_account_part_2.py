import smartpy as sp
from utils import utils


@sp.module
def main():
    class BankAccount(sp.Contract):
        def __init__(self):
            self.data.balance = sp.mutez(1000000)

        @sp.entrypoint
        def add(self, y):
            self.data.balance = self.data.balance + utils.nat_to_mutez(y)

        @sp.entrypoint
        def sub(self, y):
            self.data.balance = self.data.balance - utils.nat_to_mutez(y)

        @sp.entrypoint
        def multiply(self, y):
            # self.data.balance = utils.nat_to_mutez(x * y)
            self.data.balance = sp.mul(self.data.balance, y)

        @sp.entrypoint
        def divide(self, y):
            self.data.balance = sp.fst(
                sp.ediv(self.data.balance, y).unwrap_some()
            )


@sp.add_test(name="testing bank account functions")
def test():
    contract = main.BankAccount()
    scenario = sp.test_scenario([utils, main])
    scenario += contract

    contract.add(3000000)
    contract.sub(5000000).run(valid=False)
    # contract.multiply(x=5000000, y=3000000)
    contract.multiply(sp.nat(3))
    contract.divide(sp.nat(3))
