import smartpy as sp
from utils import utils


@sp.module
def main():
    class BankAccount(sp.Contract):
        def __init__(self):
            self.data.balance = sp.mutez(1000000)

        @sp.entrypoint
        def add(self, x, y):
            self.data.balance = utils.nat_to_mutez(x) + utils.nat_to_mutez(y)

        @sp.entrypoint
        def multiply(self, x, y):
            # self.data.balance = utils.nat_to_mutez(x * y)
            self.data.balance = sp.mul(x, y)

        @sp.entrypoint
        def divide(self, x, y):
            self.data.balance = sp.fst(sp.ediv(x, y).unwrap_some())


@sp.add_test(name="testing bank account functions")
def test():
    contract = main.BankAccount()
    scenario = sp.test_scenario([utils, main])
    scenario += contract

    contract.add(x=5000000, y=3000000)
    # contract.multiply(x=5000000, y=3000000)
    contract.multiply(x=sp.tez(5), y=sp.nat(3))
    contract.divide(x=sp.tez(5), y=sp.nat(3))
