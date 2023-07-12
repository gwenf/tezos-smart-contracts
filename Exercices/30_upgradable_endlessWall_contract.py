import smartpy as sp

@sp.module
def main():
    
    class EndlessWall(sp.Contract):
       def __init__(self, owner):
           self.data.wall_content = sp.big_map({})
           self.data.owner = owner
    
       @sp.entrypoint
       def write_message(self, message):
           data = sp.record(text = "", timestamp = sp.timestamp(0))
           if self.data.wall_content.contains(sp.sender):
               data = self.data.wall_content[sp.sender]
               data.text += "," + message
           else:
               data.text = message
           data.timestamp = sp.now
           self.data.wall_content[sp.sender] = data

       @sp.onchain_view
       def read_messages(self, user):
           return self.data.wall_content[user]

    class EndlessWall_v2(sp.Contract):
       def __init__(self, owner, old_contract):
           self.data.wall_content = sp.big_map({})
           self.data.owner = owner
           self.data.old_contract = old_contract
    
       @sp.entrypoint
       def write_message(self, message):
           assert sp.amount >= sp.tez(1)
           assert len(message) < 30, "error message"
           
           data = sp.record(text = "", timestamp = sp.timestamp(0))
           if self.data.wall_content.contains(sp.sender):
               data = self.data.wall_content[sp.sender]
               data.text += "," + message
           else:
               data.text = message
           data.timestamp = sp.now
           self.data.wall_content[sp.sender] = data

       @sp.entrypoint
       def transfer_old_messages(self):
           old_data = sp.view("read_messages",
               self.data.old_contract,
               sp.sender,
               sp.record(text = sp.string, timestamp = sp.timestamp)).unwrap_some()
           self.data.wall_content[sp.sender] = old_data
           
       @sp.onchain_view
       def read_message(self, user):
           return self.data.wall_content[user]





@sp.add_test(name = "add my name")
def test():
    alice=sp.test_account("Alice")
    bob=sp.test_account("Bob")
    eve=sp.test_account("Eve")
    sc = sp.test_scenario(main)
    endless_wall = main.EndlessWall(owner = alice.address)
    sc += endless_wall
    endless_wall.write_message("Message with the old version can be very long").run(sender = bob)

    endless_wall_v2 = main.EndlessWall_v2(owner = alice.address, old_contract = endless_wall.address)
    sc += endless_wall_v2
    endless_wall_v2.write_message("Long messages are not allowed anymore").run(sender = eve, amount = sp.tez(1), valid=False)
    endless_wall_v2.write_message("Short messages are ok").run(sender = eve, amount = sp.tez(1))
    endless_wall_v2.transfer_old_messages().run(sender = bob)
    endless_wall_v2.write_message("New short message from bob").run(sender = bob, amount = sp.tez(1))

    
    
