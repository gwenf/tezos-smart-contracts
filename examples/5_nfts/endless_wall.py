import smartpy as sp


@sp.module
def main():
    class EndlessWall(sp.Contract):
        def __init__(self, initial_text, last_sender):
            self.data.wall_text = initial_text
            self.data.nb_calls = 0
            self.data.last_sender = last_sender

        @sp.entry_point
        def write_message(self, message):
            assert (sp.len(message) <= 30) and (
                sp.len(message) >= 3
            ), "invalid message size"
            assert self.data.last_sender != sp.sender
            self.data.wall_text += ", " + message + " forever"
            self.data.nb_calls += 1
            self.data.last_sender = sp.sender


@sp.add_test(name="add my name")
def test():
    alice = sp.test_account("Alice").address
    bob = sp.test_account("Bob").address
    eve = sp.test_account("Eve").address

    c1 = main.EndlessWall(
        initial_text="Axel on Tezos forever", last_sender=alice
    )
    scenario = sp.test_scenario(main)
    scenario += c1

    scenario.h2("Testing write_message entrypoint ")
    c1.write_message("Ana & Jack").run(sender=bob)
    c1.write_message("freeCodeCamp").run(sender=alice)
    scenario.verify(
        c1.data.wall_text
        == "Axel on Tezos forever, Ana & Jack forever, freeCodeCamp forever"
    )

    scenario.h3("Testing message length is between 3 and 30 inclusive")
    c1.write_message("freeCodeCamp").run(sender=bob)
    c1.write_message("ab").run(sender=eve, valid=False)
    c1.write_message("freeCodeCampfreeCodeCampfreeCodeCamp").run(
        sender=alice, valid=False
    )

    scenario.h3("Testing that no one can call write_message consecutively")
    c1.write_message("Gwendolyn").run(sender=eve)
    c1.write_message("Alex").run(sender=eve, valid=False)
