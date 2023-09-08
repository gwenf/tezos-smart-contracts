import smartpy as sp


@sp.module
def main():
    class EndlessWall(sp.Contract):
        def __init__(self, initialText, maxLength, minLength):
            self.data.wallText = initialText
            self.data.maxLength = maxLength
            self.data.minLength = minLength

        @sp.entry_point
        def write_message(self, message):
            assert sp.len(message) <= self.data.maxLength
            assert sp.len(message) >= self.data.minLength
            self.data.wallText += ", " + message + " forever"

        @sp.entry_point
        def update_constraints(self, maxLength, minLength):
            self.data.maxLength = maxLength
            self.data.minLength = minLength


@sp.add_test(name="add my name")
def test():
    c1 = main.EndlessWall(
        initialText="Axel on Tezos forever", maxLength=30, minLength=3
    )
    scenario = sp.test_scenario(main)
    scenario += c1
    scenario.h3(" Testing write_message")
    c1.write_message("Ana & Jack")
    c1.write_message("Ana")

    c1.update_constraints(maxLength=52, minLength=3)
    c1.write_message("freeCodeCamp freeCodeCamp freeCodeCamp freeCodeCamp")

    scenario.verify(
        c1.data.wallText
        == "Axel on Tezos forever, Ana & Jack forever, freeCodeCamp forever"
    )
