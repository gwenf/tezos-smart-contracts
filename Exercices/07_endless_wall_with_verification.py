import smartpy as sp

class EndlessWall(sp.Contract):
   def __init__(self, initialText):
       self.init(wallText = initialText)

   @sp.entry_point
   def write_message(self, message):
       sp.verify((sp.len(message)<= 30) & (sp.len(message)>=3), "message less than 30 char")
       self.data.wallText += ", " + message + " forever"
  
@sp.add_test(name = "add my name")
def test():
   c1 = EndlessWall(initialText="Axel on Tezos forever")
   scenario = sp.test_scenario()
   scenario += c1
   scenario += c1.write_message("Ana & Jack")
   scenario += c1.write_message("freeCodeCamp")
   scenario += c1.write_message("freeCodeCamp is the best learning ressource")