import smartpy as sp

@sp.module
def main():

    class EndlessWall(sp.Contract):
       def __init__(self, initial_text):
           self.data.wall_text = initial_text
    
       @sp.entry_point
       def write_message(self, message):
           assert (sp.len(message) <= 30) and (sp.len(message) >= 3), "invalid size message"
           self.data.wall_text += ", " + message + " forever"
  
@sp.add_test(name = "add my name")
def test():
   c1 = main.EndlessWall(initial_text = "Axel on Tezos forever")
   scenario = sp.test_scenario(main)
   scenario += c1
   scenario.h3(" Testing write_message")
   c1.write_message("Ana & Jack")
   c1.write_message("freeCodeCamp")
   scenario.verify(c1.data.wall_text == "Axel on Tezos forever, Ana & Jack forever, freeCodeCamp forever")
   scenario.h3(" Testing write_message size message on limits")
   c1.write_message("this message is 31 letters long").run(valid = False)
   c1.write_message("AB").run(valid = False)
   #by default a transaction is valid, no need to add .run(valid = True) after testing the call
   c1.write_message("LLL")
   c1.write_message("this message is 30 characters ")
