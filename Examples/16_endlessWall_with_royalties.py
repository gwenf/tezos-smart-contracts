import smartpy as sp

class EndlessWall(sp.Contract):
   def __init__(self, initialText, owner, charity, charity_fee):
       self.init(wallText = initialText, 
       nbCalls=0, owner = owner, price=sp.tez(1), 
       charity = charity, charity_fee = charity_fee)

   @sp.entry_point
   def write_message(self, message):
       sp.verify((sp.len(message) <= 30) & (sp.len(message) >= 3), "invalid size message")
       sp.verify(sp.amount == self.data.price, "incorrect amount")
       #sp.verify(sp.now<sp.)
       self.data.wallText += ", " + message + " forever"
       self.data.nbCalls += 1
       self.data.price += sp.split_tokens(self.data.price, 5, 100)
       self.data.charity_fee += sp.split_tokens(self.data.price, 5, 100)

   @sp.entry_point
   def claim(self, requestedAmount):
        sp.verify(sp.sender == self.data.owner, "not your money")
        sp.send(self.data.owner, requestedAmount)
       
   @sp.entry_point    
   def claim_charity_fee(self, requestedAmount):
        sp.verify(sp.sender == self.data.charity, "not your money")
        sp.send(self.data.charity, requestedAmount)

  
@sp.add_test(name = "add my name")
def test():
   alice = sp.test_account("Alice").address
   bob = sp.test_account("Bob").address
   eve = sp.test_account("Eve").address
   charity = sp.test_account("Charity").address
   c1 = EndlessWall(initialText = "Axel on Tezos forever", owner=alice, charity = charity, charity_fee = sp.mutez(0))
   scenario = sp.test_scenario()
   scenario += c1
   scenario.h3(" Testing write_message is ok ")
   scenario += c1.write_message("Ana & Jack").run(sender = eve, amount = sp.tez(1))
   scenario += c1.write_message("freeCodeCamp").run(sender = bob, amount = sp.mutez(1050000))
   scenario += c1.write_message("freeCodeCamp").run(sender = alice, amount = sp.mutez(1102500))
   scenario.h3("Testing claim charity fee")
   c1.claim_charity_fee(sp.mutez(165000)).run(sender = alice, valid = False)
   c1.claim_charity_fee(sp.mutez(165000)).run(sender = charity)