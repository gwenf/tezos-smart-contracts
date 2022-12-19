#user cannot add twice in a row
#between two calls of a given user, at least one other user must have added text
import smartpy as sp

class EndlessWall(sp.Contract):
   def __init__(self, initialText, owner):
       self.init(wallText = initialText, nbCalls=0, lastSender = owner)

   @sp.entry_point
   def write_message(self, message):
       sp.verify((sp.len(message)<= 30) & (sp.len(message)>=3), "message less than 30 char")
       sp.verify(self.data.lastSender != sp.sender, "Do not spam the wall" )
       self.data.wallText += ", " + message + " forever"
       self.data.nbCalls += 1
       self.data.lastSender = sp.sender
  
@sp.add_test(name = "add my name")
def test():
   
   alice=sp.test_account("Alice").address
   bob=sp.test_account("Bob").address
   eve=sp.test_account("Eve").address
   c1 = EndlessWall(initialText="Axel on Tezos forever", owner=alice)
   scenario = sp.test_scenario()
   scenario += c1
   scenario += c1.write_message("Ana & Jack").run(sender=eve)
   scenario += c1.write_message("freeCodeCamp").run(sender=bob)
   scenario += c1.write_message("freeCodeCamp").run(sender=bob)