import smartpy as sp


@sp.module
def main():
    class Calculator(sp.Contract):
        def __init__(self):
            self.data.int_value = sp.int(1)
            self.data.nat_value = sp.nat(2)
            self.data.option_value = None

        @sp.entrypoint
        def add(self):
            self.data.int_value = sp.add(
                self.data.int_value, self.data.nat_value
            )

        @sp.entrypoint
        def mult(self):
            # self.data.int_value *= sp.to_int(self.data.nat_value)
            self.data.int_value = sp.mul(
                self.data.int_value, self.data.nat_value
            )

        @sp.entrypoint
        def negate(self):
            self.data.int_value = -self.data.int_value

        @sp.entrypoint
        def edivide(self):
            self.data.option_value = sp.ediv(
                self.data.int_value, self.data.nat_value
            )

        @sp.entrypoint
        def modulo(self, x, y):
            self.data.nat_value = sp.mod(x, y)


@sp.add_test(name="calculator test")
def test():
    contract = main.Calculator()
    scenario = sp.test_scenario(main)
    scenario += contract

    contract.add()
    contract.mult()
    contract.negate()
    contract.negate()
    contract.edivide()
    contract.modulo(x=9, y=2)
