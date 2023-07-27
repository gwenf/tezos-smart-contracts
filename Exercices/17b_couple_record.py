import smartpy as sp

@sp.module
def main():

    person_type : type = sp.record(
        first_name = sp.string,
        last_name = sp.string,
        birthdate = sp.timestamp,
        login = sp.string,
        address = sp.address,
        last_change = sp.timestamp
    )
    
    class Couple(sp.Contract):
       def __init__(self, person1, person2, owner):
           self.data.person1 = person1
           self.data.person2 = person2

       @sp.entrypoint
       def set_p1_login(self, new_login):
           person1 = self.data.person1
           sp.cast(person1, person_type) # not needed but illustrates the use of a type definition
           assert sp.sender == person1.address
           assert sp.now - person1.last_change > 60*60*24*365
           person1.login = new_login
           self.data.person1 = person1
           

       @sp.entrypoint
       def set_p2_login(self, new_login):
           person2 = self.data.person2
           assert sp.sender == person2.address
           assert sp.now - person2.last_change > 60*60*24*365
           person2.login = new_login
           self.data.person2 = person2


@sp.add_test(name = "create_couple")
def test():
   alice=sp.test_account("Alice")
   bob=sp.test_account("Bob")
   eve=sp.test_account("Eve")
   c1 = main.Couple(
       sp.record(
           first_name = "Alice",
           last_name = "Smith",
           birthdate = sp.timestamp(1000),
           login = "alice_s",
           address = alice.address,
           last_change = sp.timestamp(0)
       ),
       sp.record(
           first_name = "Bob",
           last_name = "Smith",
           birthdate = sp.timestamp(1000),
           login = "bob_s",
           address = bob.address,
           last_change = sp.timestamp(0)
       ),
       eve.address
   )
   scenario = sp.test_scenario(main)
   scenario += c1
   c1.set_p1_login("alicia").run(sender = alice, now = sp.timestamp(60*60*24*366))
   c1.set_p2_login("bobby").run(sender = bob, now = sp.timestamp(60*60*24*364), valid=False)
   c1.set_p2_login("bobby").run(sender = bob, now = sp.timestamp(60*60*24*366))

