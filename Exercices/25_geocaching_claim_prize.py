import smartpy as sp

@sp.module
def main():
    class Geocaching(sp.Contract):
    
        def __init__(self, owner, deadline):
            self.data.treasures = sp.big_map({})
            self.data.scorePerPlayer = sp.big_map({})
            self.data.currentWinner = owner
            self.data.scorePerPlayer[owner] = 0
            self.data.owner = owner
            self.data.deadline = deadline
            self.data.nbTreasures = 0

        @sp.entrypoint
        def create_treasure(self, password_hash):
            assert sp.now < self.data.deadline
            assert sp.sender == self.data.owner
            self.data.nbTreasures += 1
            self.data.treasures[self.data.nbTreasures] = sp.record(hash = password_hash, found = False)

        @sp.entrypoint
        def discover_treasure(self, id, password):
            assert sp.now < self.data.deadline
            treasure = self.data.treasures[id]
            assert not treasure.found
            assert sp.blake2b(password) == treasure.hash
            self.data.treasures[id].found = True
            if not self.data.scorePerPlayer.contains(sp.sender):
                self.data.scorePerPlayer[sp.sender] = 0
            self.data.scorePerPlayer[sp.sender] += 1
            if self.data.scorePerPlayer[sp.sender] > self.data.scorePerPlayer[self.data.currentWinner]:
                self.data.currentWinner = sp.sender

        @sp.entrypoint
        def claim_prize(self):
            assert sp.now >= self.data.deadline
            assert sp.sender == self.data.currentWinner
            sp.send(sp.sender, sp.balance)
                   
@sp.add_test(name='Geocaching test')
def test():
    alice = sp.test_account("alice").address
    bob = sp.test_account("bob").address
    carl = sp.test_account("carl").address
    scenario = sp.test_scenario(main)
    geocaching = main.Geocaching(alice, sp.timestamp(1000))
    scenario += geocaching
    geocaching.create_treasure(sp.blake2b(sp.pack("secret password 1"))).run(sender = alice, amount = sp.tez(100))
    geocaching.create_treasure(sp.blake2b(sp.pack("secret password 2"))).run(sender = alice)
    geocaching.create_treasure(sp.blake2b(sp.pack("secret password 3"))).run(sender = alice)
    geocaching.discover_treasure(id = 1, password = sp.pack("secret password 1")).run(sender = bob, now = sp.timestamp(100))
    geocaching.discover_treasure(id = 2, password = sp.pack("false password")).run(sender = bob, now = sp.timestamp(100), valid = False)
    geocaching.discover_treasure(id = 2, password = sp.pack("secret password 2")).run(sender = carl, now = sp.timestamp(100))
    geocaching.discover_treasure(id = 3, password = sp.pack("secret password 3")).run(sender = carl, now = sp.timestamp(200))
    geocaching.claim_prize().run(sender = carl, now = sp.timestamp(100), valid = False)
    geocaching.claim_prize().run(sender = bob, now = sp.timestamp(1000), valid = False)
    geocaching.claim_prize().run(sender = carl, now = sp.timestamp(1000))

        
