import smartpy as sp

@sp.module
def main():

    person_type : type = sp.record(first_name = sp.string, last_name = sp.string, birthdate = sp.timestamp)
    
    class Couple(sp.Contract):
       def __init__(self, person1, person2, owner):
           self.data.person1 = person1
           self.data.person2 = person2
           self.data.owner = owner

       @sp.entrypoint
       def set_p1_first_name(self, new_first_name):
           sp.cast(self.data.person1, person_type) # not needed but illustrates the use of a type definition
           assert sp.sender == self.data.owner
           self.data.person1.first_name = new_first_name

       @sp.entrypoint
       def set_p2_first_name(self, new_first_name):
           assert sp.sender == self.data.owner
           self.data.person2.first_name = new_first_name


@sp.add_test(name = "create_couple")
def test():
   alice=sp.test_account("Alice")
   bob=sp.test_account("Bob")
   eve=sp.test_account("Eve")
   c1 = main.Couple(
       sp.record(first_name = "Alice", last_name = "Smith", birthdate = sp.timestamp(1000)),
       sp.record(first_name = "Bob", last_name = "Smith", birthdate = sp.timestamp(1000)),
       eve.address
   )
   scenario = sp.test_scenario(main)
   scenario += c1
   c1.set_p1_first_name("Alicia").run(sender = eve)
   c1.set_p2_first_name("Bobby").run(sender = bob, valid = False)
