#user cannot add twice in a row
#between two calls of a given user, at least one other user must have added text
import smartpy as sp

@sp.module
def main():

    class EndlessWall(sp.Contract):
       def __init__(self, initial_text, owner):
           self.data.wall_text = initial_text
           self.data.nb_calls = 0
           self.data.last_sender = owner
    
       @sp.entry_point
       def write_message(self, message):
           assert (sp.len(message) <= 30) and (sp.len(message) >= 3), "invalid message size"
           assert self.data.last_sender != sp.sender, "Do not spam the wall"
           self.data.wall_text += ", " + message + " forever"
           self.data.nb_calls += 1
           self.data.last_sender = sp.sender
  
@sp.add_test(name = "add my name")
def test():
   alice=sp.test_account("Alice").address
   bob=sp.test_account("Bob").address
   eve=sp.test_account("Eve").address
   c1 = main.EndlessWall(initial_text = "Axel on Tezos forever", owner=alice)
   scenario = sp.test_scenario(main)
   scenario += c1
   scenario.h3("Testing write_message entrypoint ")
   c1.write_message("Ana & Jack").run(sender = eve)
   c1.write_message("freeCodeCamp").run(sender = bob)
   scenario.verify(c1.data.wall_text == "Axel on Tezos forever, Ana & Jack forever, freeCodeCamp forever")
   scenario.h3("Testing user cannot add twice in a row ")
   c1.write_message("freeCodeCamp").run(sender = bob, valid = False)
   c1.write_message("freeCodeCamp").run(sender = bob, valid = False)
   scenario.h3("Testing write_message size message on limits ")
   c1.write_message("this message is 31 letters long").run(sender = alice, valid = False)
   #by default a transaction is valid, no need to add .run(valid = True) after testing a valid call
   c1.write_message("LLL").run(sender = alice)
   c1.write_message("this message is 30 characters ").run(sender = eve)
   scenario.verify(c1.data.nb_calls == 4)

