import smartpy as sp

class EndlessWall(sp.Contract):
   def __init__(self, initialText, owner):
       self.init(wallText = initialText, nbCalls=0, owner = owner)

   @sp.entry_point
   def write_message(self, message):
       sp.verify((sp.len(message) <= 30) & (sp.len(message) >= 3), "invalid size message")
       sp.verify(sp.amount == sp.tez(1), "incorrect amount")
       #sp.verify(sp.now<sp.)
       self.data.wallText += ", " + message + " forever"
       self.data.nbCalls += 1

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
    #scenario write_message ok
   scenario += c1.write_message("Ana & Jack").run(sender = eve, amount = sp.tez(1))
   scenario += c1.write_message("freeCodeCamp").run(sender = bob, amount = sp.tez(1))
   scenario.verify(c1.data.wallText == "Axel on Tezos forever, Ana & Jack forever, freeCodeCamp forever")
    #scenario write_message fails for spamming
   scenario += c1.write_message("bob is the last sender").run(sender = bob, valid = False)
   scenario += c1.write_message("bob is the last sender").run(sender = bob, valid = False)
    #checking write_message fails for size message
   scenario += c1.write_message("this message is 31 letters long").run(sender = alice, valid = False, amount = sp.tez(1))
   scenario += c1.write_message("AB").run(sender = alice, valid = False, amount = sp.tez(1))
    #checking write_message passes for size message
   scenario += c1.write_message("LLL").run(sender = alice, amount = sp.tez(1))
   scenario += c1.write_message("this message is 30 characters ").run(sender = eve, amount = sp.tez(1) )
   scenario.verify(c1.data.nbCalls == 4)
   #checking testing amounts
   scenario += c1.write_message("testing right amount").run(sender = eve,amount = sp.tez(1))
   scenario += c1.write_message("testing lesser amount").run(sender = eve,amount = sp.mutez(999999), valid = False)
   scenario += c1.write_message("testing bigger amount").run(sender = bob, amount = sp.mutez(1000001), valid = False)
   scenario += c1.write_message("testing correct amount").run(sender = bob, amount = sp.tez(1))
   #checking claim entrypoint
   scenario += c1.claim(sp.tez(3)).run(sender = bob, valid = False)
   scenario += c1.claim(sp.tez(4)).run(sender = alice)