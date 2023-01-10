import smartpy as sp

class EndlessWall(sp.Contract):
   def __init__(self, initialText, owner):
       self.init(wallText = initialText, nbCalls=0, owner = owner, price=sp.tez(1))

   @sp.entry_point
   def write_message(self, message):
       sp.verify((sp.len(message) <= 30) & (sp.len(message) >= 3), "invalid size message")
       sp.verify(sp.amount == self.data.price, "incorrect amount")
       #sp.verify(sp.now<sp.)
       self.data.wallText += ", " + message + " forever"
       self.data.nbCalls += 1
       self.data.price += sp.split_tokens(self.data.price, 5, 100)

   @sp.entry_point
   def claim(self, requestedAmount):
        sp.verify(sp.sender == self.data.owner, "not your money")
        sp.send(self.data.owner, requestedAmount)
  
@sp.add_test(name = "add my name")
def test():
   alice=sp.test_account("Alice").address
   bob=sp.test_account("Bob").address
   eve=sp.test_account("Eve").address
   c1 = EndlessWall(initialText = "Axel on Tezos forever", owner=alice)
   scenario = sp.test_scenario()
   scenario += c1
   scenario.h3(" Testing write_message is ok ")
   scenario += c1.write_message("Ana & Jack").run(sender = eve, amount = sp.tez(1))
   scenario += c1.write_message("freeCodeCamp").run(sender = bob, amount = sp.mutez(1050000))
   scenario += c1.write_message("freeCodeCamp").run(sender = alice, amount = sp.mutez(1102500))