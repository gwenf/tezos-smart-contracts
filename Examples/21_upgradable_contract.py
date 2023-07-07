import smartpy as sp

@sp.module
def main():

    class DataEndlessWall(sp.Contract):
       def __init__(self, owner):
           self.data.wall_content = sp.big_map({})
           self.data.nb_calls = 0
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
    
       @sp.entrypoint
       def update_owner(self, new_owner):
            assert sp.sender == self.data.owner, "not the owner"
            self.data.owner = new_owner

    class UpgradableEndlessWall(sp.Contract):
        def __init__(self, wall_contract, owner):
            self.data.owner = owner
            self.data.wall_contract = wall_contract

        @sp.entrypoint
        def write_message(self, message):
            wall_write_message = sp.contract(sp.record(message = sp.string, user = sp.address),
                                             self.data.wall_contract,
                                             entrypoint="write_message").unwrap_some()
            sp.transfer(sp.record(message = message, user = sp.sender), sp.tez(0), wall_write_message)

        @sp.entrypoint
        def upgrade(self, new_contract):
            assert sp.sender == self.data.owner
            wall_update_owner = sp.contract(sp.address,
                                            self.data.wall_contract,
                                            entrypoint="update_owner").unwrap_some()
            sp.transfer(new_contract, sp.tez(0), wall_update_owner)


    class UpgradableEndlessWallV2(sp.Contract):
        def __init__(self, wall_contract, owner):
            self.data.owner = owner
            self.data.wall_contract = wall_contract

        @sp.entrypoint
        def write_message(self, message):
            assert sp.len(message) <= 30, "Wall v2 requires message lengths under 30"
            wall_write_message = sp.contract(sp.record(message = sp.string, user = sp.address),
                                             self.data.wall_contract,
                                             entrypoint="write_message").unwrap_some()
            sp.transfer(sp.record(message = message, user = sp.sender), sp.tez(0), wall_write_message)

        @sp.entrypoint
        def upgrade(self, new_contract):
            assert sp.sender == self.data.owner
            wall_update_owner = sp.contract(sp.address,
                                            self.data.wall_contract,
                                            entrypoint="update_owner").unwrap_some()
            sp.transfer(new_contract, sp.tez(0), wall_update_owner)


@sp.add_test(name = "add my name")
def test():
    alice=sp.test_account("Alice")
    bob=sp.test_account("Bob")
    eve=sp.test_account("Eve")
    sc = sp.test_scenario(main)
    innerWall = main.DataEndlessWall(alice.address)
    sc += innerWall
    endlessWallV1 = main.UpgradableEndlessWall(wall_contract = innerWall.address, owner = alice.address)
    sc += endlessWallV1
    innerWall.update_owner(endlessWallV1.address).run(sender = alice)
    endlessWallV1.write_message("Message with the old version can be very long").run(sender = bob)
    endlessWallV2 = main.UpgradableEndlessWallV2(wall_contract = innerWall.address, owner = alice.address)
    sc += endlessWallV2
    endlessWallV1.upgrade(endlessWallV2.address).run(sender = alice)
    endlessWallV2.write_message("Long messages aren't allowed anymore").run(sender = eve, valid=False)
    endlessWallV2.write_message("Short messages are ok").run(sender = eve)
    
    
    
