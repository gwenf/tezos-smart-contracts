import smartpy as sp


@sp.module
def main():
    class EndlessWall(sp.Contract):
        def __init__(self, initialText, minLength, maxLength):
            self.data.wallText = initialText
            self.data.minLength = minLength
            self.data.maxLength = maxLength

        @sp.entry_point
        def write_message(self, message):
            assert sp.len(message) <= self.data.maxLength
            assert sp.len(message) >= self.data.minLength
            self.data.wallText += ", " + message + " forever"


@sp.add_test(name="add my name")
def test():
    c1 = main.EndlessWall(
        initialText="Axel on Tezos forever", minLength=3, maxLength=30
    )
    scenario = sp.test_scenario(main)
    scenario += c1
    scenario.h3(" Testing write_message")
    c1.write_message("Ana & Jack")
    c1.write_message("Ana")
    c1.write_message(
        "freeCodeCamp freeCodeCamp freeCodeCamp freeCodeCamp"
    ).run(valid=False)
    scenario.verify(
        c1.data.wallText
        == "Axel on Tezos forever, Ana & Jack forever, freeCodeCamp forever"
    )
