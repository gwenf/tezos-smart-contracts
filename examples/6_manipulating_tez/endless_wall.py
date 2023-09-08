import smartpy as sp


@sp.module
def main():
    class EndlessWall(sp.Contract):
        def __init__(self, initial_text, owner):
            self.data.wall_text = initial_text
            self.data.nb_calls = 0
            self.data.owner = owner

        @sp.entry_point
        def write_message(self, message):
            assert (sp.len(message) <= 30) and (
                sp.len(message) >= 3
            ), "invalid message size"
            assert sp.amount >= sp.tez(1), "Must send one Tez"
            self.data.wall_text += ", " + message + " forever"
            self.data.nb_calls += 1

        @sp.entrypoint
        def claim(self, amount):
            assert sp.sender == self.data.owner, "Not your money!"
            sp.send(self.data.owner, amount)

        @sp.entrypoint
        def claim_all(self):
            assert sp.sender == self.data.owner, "Not your money!"
            sp.send(self.data.owner, sp.balance)


@sp.add_test(name="add my name")
def test():
    alice = sp.test_account("Alice").address
    bob = sp.test_account("Bob").address
    eve = sp.test_account("Eve").address

    c1 = main.EndlessWall(initial_text="Axel on Tezos forever", owner=alice)
    scenario = sp.test_scenario(main)
    scenario += c1

    scenario.h2("Testing write_message entrypoint ")
    c1.write_message("Ana & Jack").run(sender=bob, amount=sp.tez(2))
    c1.write_message("freeCodeCamp").run(sender=alice, amount=sp.tez(1))
    scenario.verify(
        c1.data.wall_text
        == "Axel on Tezos forever, Ana & Jack forever, freeCodeCamp forever"
    )

    scenario.h2("Test withdrawing money from the contract")
    c1.claim(sp.mutez(5000)).run(sender=alice)
    c1.claim(sp.mutez(5000)).run(sender=bob, valid=False)
    c1.claim_all().run(sender=alice)
    scenario.verify(c1.balance == sp.tez(0))

    # scenario.h3("Testing message length is between 3 and 30 inclusive")
    # c1.write_message("freeCodeCamp").run(sender=bob)
    # c1.write_message("ab").run(sender=eve, valid=False)
    # c1.write_message("freeCodeCampfreeCodeCampfreeCodeCamp").run(sender=alice, valid = False)
