import smartpy as sp

@sp.module
def main():
    def default_verify_message(message):
    	pass

    def upgraded_verify_message(message):
        assert sp.len(message) <= 30, "Wall v2 requires message lengths under 30"
        
    
    class EndlessWall(sp.Contract):
       def __init__(self, owner):
           self.data.wall_content = sp.big_map({})
           self.data.owner = owner
           self.data.verify = default_verify_message
    
       @sp.entrypoint
       def write_message(self, message):
           self.data.verify(message)

           data = sp.record(text = "", timestamp = sp.timestamp(0))
           if self.data.wall_content.contains(sp.sender):
               data = self.data.wall_content[sp.sender]
               data.text += "," + message
           else:
               data.text = message
           data.timestamp = sp.now
           self.data.wall_content[sp.sender] = data

       @sp.entrypoint
       def set_verify(self, new_verify_message):
           assert sp.sender == self.data.owner
           self.data.verify = new_verify_message


@sp.add_test(name = "add my name")
def test():
    alice=sp.test_account("Alice")
    bob=sp.test_account("Bob")
    eve=sp.test_account("Eve")
    sc = sp.test_scenario(main)
    endless_wall = main.EndlessWall(owner = alice.address)
    sc += endless_wall
    endless_wall.write_message("Message with the old version can be very long").run(sender = bob)
    endless_wall.set_verify(main.upgraded_verify_message).run(sender = alice)
    endless_wall.write_message("Long messages aren't allowed anymore").run(sender = bob, valid = False)
    endless_wall.write_message("Short messages are ok").run(sender = bob)    
