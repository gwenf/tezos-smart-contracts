import smartpy as sp


@sp.module
def main():
    class EndlessWall(sp.Contract):
        def __init__(self, initial_text):
            self.data.wall_text = initial_text
            self.data.nbCalls = 0
            self.data.last_sender = None

        @sp.entrypoint
        def write_message(self, message):
            assert (sp.len(message) <= 30) and (
                sp.len(message) >= 3
            ), "invalid message size"
            assert self.data.last_sender != sp.Some(
                sp.sender
            ), "Do not spam the wall"
            self.data.wall_text += ", " + message + " forever"
            self.data.nbCalls += 1
            self.data.last_sender = sp.Some(sp.sender)


@sp.add_test(name="add my name")
def test():
    alice = sp.test_account("Alice")
    bob = sp.test_account("Bob")
    eve = sp.test_account("Eve")
    c1 = main.EndlessWall(initial_text="Axel on Tezos forever")
    scenario = sp.test_scenario(main)
    scenario += c1

    scenario.verify(c1.data.last_sender.is_none())

    c1.write_message("Gwen").run(sender=eve)
    scenario.verify(c1.data.last_sender == sp.some(eve.address))
    scenario.verify(c1.data.last_sender.open_some() == eve.address)

    c1.write_message("Alex").run(sender=eve, valid=False)
