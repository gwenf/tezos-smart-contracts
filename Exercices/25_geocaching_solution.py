import smartpy as sp

@sp.module
def main():
    class Geocaching(sp.Contract):
    
        def __init__(self, owner, deadline):
            self.data.treasures = sp.big_map({})
            self.data.scorePerUser = sp.big_map({})
            self.data.commits = sp.big_map({})
            self.data.currentWinner = owner
            self.data.scorePerUser[owner] = 0
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
        def commit_discover_treasure(self, id, commit_data):
            assert not self.data.commits.contains(commit_data)
            self.data.commits[commit_data] = True
        
        @sp.entrypoint
        def reveal_discover_treasure(self, id, password):
            assert sp.now < self.data.deadline
            treasure = self.data.treasures[id]
            assert not treasure.found
            assert sp.blake2b(password) == treasure.hash
            expected_commit = sp.blake2b(sp.pack(sp.record(password = password, user = sp.sender)))
            assert self.data.commits.contains(expected_commit)
            self.data.treasures[id].found = True
            if not self.data.scorePerUser.contains(sp.sender):
                self.data.scorePerUser[sp.sender] = 0
            self.data.scorePerUser[sp.sender] += 1
            if self.data.scorePerUser[sp.sender] > self.data.scorePerUser[self.data.currentWinner]:
                self.data.currentWinner = sp.sender

        @sp.entrypoint
        def award_prize(self):
            assert sp.now >= self.data.deadline
            assert sp.sender == self.data.owner
            sp.send(self.data.currentWinner, sp.balance)
                   
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

    # Correct commit and reveal for password 1
    commit_1 = sp.blake2b(sp.pack(sp.record(password = sp.pack("secret password 1"), user = bob)))
    geocaching.commit_discover_treasure(id = 1, commit_data = commit_1).run(sender = bob, now = sp.timestamp(100))
    geocaching.reveal_discover_treasure(id = 1, password = sp.pack("secret password 1")).run(sender = bob, now = sp.timestamp(100))

    # Try invalid password
    commit_fake = sp.blake2b(sp.pack(sp.record(password = sp.pack("false password"), user = bob)))
    geocaching.commit_discover_treasure(id = 2, commit_data = commit_fake).run(sender = bob, now = sp.timestamp(100))
    geocaching.reveal_discover_treasure(id = 2, password = sp.pack("false password")).run(sender = bob, now = sp.timestamp(100), valid = False)
    
    # Try to reveal without a commit
    geocaching.reveal_discover_treasure(id = 2, password = sp.pack("secret password 2")).run(sender = bob, now = sp.timestamp(100), valid = False)
    
    commit_2 = sp.blake2b(sp.pack(sp.record(password = sp.pack("secret password 2"), user = carl)))
    geocaching.commit_discover_treasure(id = 2, commit_data = commit_2).run(sender = carl, now = sp.timestamp(100))
    # Wrong person tries to reveal
    geocaching.reveal_discover_treasure(id = 2, password = sp.pack("secret password 2")).run(sender = bob, now = sp.timestamp(100), valid = False)
    geocaching.reveal_discover_treasure(id = 2, password = sp.pack("secret password 2")).run(sender = carl, now = sp.timestamp(100))

    
    commit_3 = sp.blake2b(sp.pack(sp.record(password = sp.pack("secret password 3"), user = carl)))
    geocaching.commit_discover_treasure(id = 2, commit_data = commit_3).run(sender = carl, now = sp.timestamp(100))
    geocaching.reveal_discover_treasure(id = 3, password = sp.pack("secret password 3")).run(sender = carl, now = sp.timestamp(200))
    geocaching.award_prize().run(sender = alice, now = sp.timestamp(100), valid = False)
    geocaching.award_prize().run(sender = carl, now = sp.timestamp(1000), valid = False)
    geocaching.award_prize().run(sender = alice, now = sp.timestamp(1000))

    


        

    


        