import smartpy as sp

@sp.module
def main():

    class InnerEndlessWall(sp.Contract):
       def __init__(self, owner):
           self.data.wall_content = sp.big_map({})
           self.data.owner = owner
    
       @sp.entrypoint
       def write_message(self, message, user):
           sp.cast(user, sp.address)
           assert self.data.owner == sp.sender
           data = sp.record(text = "", timestamp = sp.timestamp(0))
           if self.data.wall_content.contains(user):
               data = self.data.wall_content[user]
               data.text += "," + message
           else:
               data.text = message
           data.timestamp = sp.now
           self.data.wall_content[user] = data

    class InnerEndlessWall_V2(sp.Contract):
       def __init__(self, owner, balance_owner):
           self.data.wall_content = sp.big_map({})
           self.data.owner = owner
           self.data.balance_owner = balance_owner
    
       @sp.entrypoint
       def write_message(self, message, user):
           sp.cast(user, sp.address)
           assert self.data.owner == sp.sender
           assert sp.len(message) <= 30, "Wall v2 requires message lengths under 30"
           assert sp.amount == sp.tez(1)
           data = sp.record(text = "", timestamp = sp.timestamp(0))
           if self.data.wall_content.contains(user):
               data = self.data.wall_content[user]
               data.text += "," + message
           else:
               data.text = message
           data.timestamp = sp.now
           self.data.wall_content[user] = data

       @sp.entrypoint
       def claim(self):
           assert sp.sender == self.data.balance_owner
           sp.send(sp.sender, sp.balance)

    class UpgradableEndlessWall(sp.Contract):
        def __init__(self, inner_contract, owner):
            self.data.owner = owner
            self.data.inner_contract = owner

        @sp.entrypoint
        def write_message(self, message):
            inner_write_message = sp.contract(sp.record(message = sp.string, user = sp.address),
                                             self.data.inner_contract,
                                             entrypoint="write_message").unwrap_some()
            sp.transfer(sp.record(message = message, user = sp.sender), sp.amount, inner_write_message)

        @sp.entrypoint
        def upgrade(self, new_inner_contract):
            assert sp.sender == self.data.owner
            self.data.inner_contract = new_inner_contract


@sp.add_test(name = "add my name")
def test():
    alice=sp.test_account("Alice")
    bob=sp.test_account("Bob")
    eve=sp.test_account("Eve")
    sc = sp.test_scenario(main)
    endless_wall = main.UpgradableEndlessWall(inner_contract = alice.address, owner = alice.address)
    sc += endless_wall
    innerWall_V1 = main.InnerEndlessWall(endless_wall.address)
    sc += innerWall_V1
    endless_wall.upgrade(innerWall_V1.address).run(sender = alice)
    endless_wall.write_message("Message with the old version can be very long").run(sender = bob)
    innerWall_V2 = main.InnerEndlessWall_V2(endless_wall.address, alice.address)
    sc += innerWall_V2
    endless_wall.upgrade(innerWall_V2.address).run(sender = alice)
    endless_wall.write_message("Long messages aren't allowed anymore").run(sender = bob, valid = False)
    endless_wall.write_message("Short messages are ok").run(sender = bob, amount = sp.tez(1))
    innerWall_V2.claim().run(sender = alice)
    
