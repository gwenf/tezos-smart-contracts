import smartpy as sp

@sp.module
def main():

    class DataEndlessWall(sp.Contract):
       def __init__(self, owner):
           self.data.wall_content = sp.big_map({})
           self.data.owner = owner
    
       @sp.entrypoint
       def write_data(self, data, user):
           sp.cast(user, sp.address)
           sp.cast(data, sp.record(text = sp.string, timestamp = sp.timestamp))
           assert self.data.owner == sp.sender
           self.data.wall_content[user] = data
           
       @sp.entrypoint
       def update_owner(self, new_owner):
            assert sp.sender == self.data.owner, "not the owner"
            self.data.owner = new_owner

       @sp.onchain_view
       def read_data(self, user):
            result = sp.record(text = "", timestamp = sp.timestamp(0))
            if self.data.wall_content.contains(user):
                result = self.data.wall_content[user]
            return result

    class Upgradableendless_wall(sp.Contract):
        def __init__(self, wall_contract, owner):
            self.data.owner = owner
            self.data.wall_contract = wall_contract

        @sp.entrypoint
        def write_message(self, message):
           opt_data = sp.view("read_data",
                              self.data.wall_contract,
                              sp.sender,
                              sp.record(text = sp.string, timestamp = sp.timestamp))
           data = sp.record(text = "", timestamp = sp.timestamp(0))
           data.text += "," + message
           data.timestamp = sp.now

           wall_write_data = sp.contract(sp.record(data =  sp.record(text = sp.string, timestamp = sp.timestamp),
                                                    user = sp.address),
                                             self.data.wall_contract,
                                             entrypoint="write_data").unwrap_some()
           sp.transfer(sp.record(data = data, user = sp.sender), sp.tez(0), wall_write_data)

        @sp.entrypoint
        def upgrade(self, new_contract):
            assert sp.sender == self.data.owner
            wall_update_owner = sp.contract(sp.address,
                                            self.data.wall_contract,
                                            entrypoint="update_owner").unwrap_some()
            sp.transfer(new_contract, sp.tez(0), wall_update_owner)

    class Upgradableendless_wall_V2(sp.Contract):
        def __init__(self, wall_contract, owner):
            self.data.owner = owner
            self.data.wall_contract = wall_contract

        @sp.entrypoint
        def write_message(self, message):
           assert sp.len(message) <= 30, "Wall v2 requires message lengths under 30"
           opt_data = sp.view("read_data",
                              self.data.wall_contract,
                              sp.sender,
                              sp.record(text = sp.string, timestamp = sp.timestamp))
           data = sp.record(text = "", timestamp = sp.timestamp(0))
           data.text += "," + message
           data.timestamp = sp.now

           wall_write_data = sp.contract(sp.record(data =  sp.record(text = sp.string, timestamp = sp.timestamp),
                                                    user = sp.address),
                                             self.data.wall_contract,
                                             entrypoint="write_data").unwrap_some()
           sp.transfer(sp.record(data = data, user = sp.sender), sp.tez(0), wall_write_data)

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
    endless_wall_V1 = main.Upgradableendless_wall(wall_contract = innerWall.address, owner = alice.address)
    sc += endless_wall_V1
    innerWall.update_owner(endless_wall_V1.address).run(sender = alice)
    endless_wall_V1.write_message("Message with the old version can be very long").run(sender = bob)
    endless_wall_V2 = main.Upgradableendless_wall_V2(wall_contract = innerWall.address, owner = alice.address)
    sc += endless_wall_V2
    endless_wall_V1.upgrade(endless_wall_V2.address).run(sender = alice)
    endless_wall_V2.write_message("Long messages aren't allowed anymore").run(sender = eve, valid=False)
    endless_wall_V2.write_message("Short messages are ok").run(sender = eve)
