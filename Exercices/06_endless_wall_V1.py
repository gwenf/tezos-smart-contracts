import smartpy as sp

@sp.module
def main():

    class EndlessWall(sp.Contract):
       def __init__(self, initial_text):
           self.data.wall_text = initial_text
    
       @sp.entrypoint
       def write_message(self, message):
           self.data.wall_text += ", " + message + " forever"
  
@sp.add_test(name = "add my name")
def test():
   c1 = main.EndlessWall(initial_text = "Axel on Tezos forever")
   scenario = sp.test_scenario(main)
   scenario += c1
   scenario.h3("Testing write_message entrypoint")
   c1.write_message("Ana & Jack")
   c1.write_message("freeCodeCamp")
   #check the expected output
