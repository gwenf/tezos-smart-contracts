import smartpy as sp

@sp.module
def main():
    class Micropayments(sp.Contract):
    
        def __init__(self):
            self.data.deposits = sp.big_map({})

        @sp.entrypoint
        def deposit(self, destination, deadline, public_key):
            key = sp.record(source = sp.sender, destination = destination)
            if not self.data.deposits.contains(key):
                self.data.deposits[key] = sp.record(deadline=deadline, amount=sp.amount, public_key = public_key, counter = 0)
            else:
                assert self.data.deposits[key].deadline < deadline
                self.data.deposits[key].deadline = deadline
                self.data.deposits[key].amount += sp.amount

        @sp.entrypoint
        def claimPayments(self, source, packed_message, signature):
            key = sp.record(source = source, destination = sp.sender)
            deposit = self.data.deposits[key]
            assert sp.check_signature(deposit.public_key, signature, packed_message)
            message = sp.unpack(packed_message, sp.record(destination = sp.address, amount = sp.mutez, counter = sp.nat)).unwrap_some()
            assert message.destination == sp.sender
            assert message.counter == deposit.counter
            assert deposit.amount >= message.amount
            self.data.deposits[key].amount = deposit.amount - message.amount
            self.data.deposits[key].counter += 1
            sp.send(sp.sender, message.amount)

        @sp.entrypoint
        def closeAccount(self, destination):
            key = sp.record(source = sp.sender, destination = destination)
            assert self.data.deposits[key].deadline <= sp.now
            sp.send(sp.sender, self.data.deposits[key].amount)
            del self.data.deposits[key]
                   

@sp.add_test(name='Testing extortion attack')
def test():
    alice = sp.test_account("alice")
    bob = sp.test_account("bob").address
    carl = sp.test_account("carl").address
    scenario = sp.test_scenario(main)
    micropayments = main.Micropayments()
    scenario += micropayments
    micropayments.deposit(destination = bob, deadline = sp.timestamp(1000), public_key = alice.public_key).run(sender = alice.address, amount = sp.tez(100))
    message = sp.record(destination = bob, amount = sp.tez(5), counter = sp.nat(0))
    packed_message = sp.pack(message)
    signature = sp.make_signature(alice.secret_key, packed_message)
    micropayments.claimPayments(source = alice.address, packed_message = packed_message, signature = signature).run(sender = bob)
    micropayments.claimPayments(source = alice.address, packed_message = packed_message, signature = signature).run(sender = bob, valid = False)
    micropayments.closeAccount(bob).run(sender = alice.address, now = sp.timestamp(1001))

            
    


        