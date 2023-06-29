import smartpy as sp

@sp.module
def main():

    class EndlessWall(sp.Contract):
       def __init__(self, initial_text, owner):
           self.data.wall_text = initial_text
           self.data.nbCalls = 0
           self.data.last_sender = None
    
       @sp.entrypoint
       def write_message(self, message):
           assert (sp.len(message) <= 30) and (sp.len(message) >= 3), "invalid message size"
           assert self.data.last_sender != sp.Some(sp.sender), "Do not spam the wall"
           self.data.wall_text += ", " + message + " forever"
           self.data.nbCalls += 1
           self.data.last_sender = sp.Some(sp.sender)  
  
@sp.add_test(name = "add my name")
def test():
   alice=sp.test_account("Alice")
   bob=sp.test_account("Bob")
   eve=sp.test_account("Eve")
   c1 = main.EndlessWall(initial_text = "Axel on Tezos forever", owner = alice.address)
   scenario = sp.test_scenario(main)
   scenario += c1
   scenario.verify(c1.data.last_sender == sp.none)
   c1.write_message("Ana & Jack").run(sender = eve)
   scenario.verify(c1.data.last_sender == sp.some(eve))
   scenario.verify(c1.data.last_sender.open_some() == eve) # equivalent to the previous line
   c1.write_message("freeCodeCamp").run(sender = bob)
   scenario.verify(c1.data.wall_text == "Axel on Tezos forever, Ana & Jack forever, freeCodeCamp forever")
   c1.write_message("freeCodeCamp").run(sender = bob, valid = False, exception="Do not spam the wall")
   c1.write_message("this message is 31 letters long").run(sender = alice, valid = False)
   #by default a transaction is valid, no need to add .run(valid = True) after testing a valid call
   c1.write_message("LLL").run(sender = alice)
   c1.write_message("this message is 30 characters ").run(sender = eve)
   scenario.verify(c1.data.nbCalls == 4)
    
