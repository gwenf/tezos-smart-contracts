import smartpy as sp

class EndlessWall(sp.Contract):
   def __init__(self, initialText):
       self.init(wallText = initialText)

   @sp.entry_point
   def write_message(self, message):
       sp.verify((sp.len(message) <= 30) & (sp.len(message) >= 3), "invalid size message")
       self.data.wallText += ", " + message + " forever"
  
@sp.add_test(name = "add my name")
def test():
   c1 = EndlessWall(initialText = "Axel on Tezos forever")
   scenario = sp.test_scenario()
   scenario += c1
   scenario += c1.write_message("Ana & Jack")
   scenario += c1.write_message("freeCodeCamp")
   scenario.verify(c1.data.wallText == "Axel on Tezos forever, Ana & Jack forever, freeCodeCamp forever")
   scenario += c1.write_message("this message is 31 letters long").run(valid = False)
   scenario += c1.write_message("AB").run(valid = False)
   #by default a transaction is valid, no need to add .run(valid = True) after testing the call
   scenario += c1.write_message("LLL")
   scenario += c1.write_message("this message is 30 characters ")
