import smartpy as sp

@sp.module
def main():
    class Geocaching(sp.Contract):
    
        def __init__(self, owner, deadline_commit, deadline_reveal, deadline_dispute, deposit):
            self.data.treasures = sp.big_map({})
            self.data.score_per_user = sp.big_map({})
            self.data.commits = sp.big_map({})
            self.data.current_winner = owner
            self.data.score_per_user[owner] = 0
            self.data.owner = owner
            self.data.deposit = deposit
            self.data.deadline_commit = deadline_commit
            self.data.deadline_reveal = deadline_reveal
            self.data.deadline_dispute = deadline_dispute
            self.data.nb_treasures = 0

        @sp.entrypoint
        def register_player(self):
            assert sp.now < self.data.deadline_commit
            assert not self.data.score_per_user.contains(sp.sender)
            assert sp.amount == self.data.deposit
            self.data.score_per_user[sp.sender] = 0
        
        @sp.entrypoint
        def create_treasure(self, password_hash):
            assert sp.now < self.data.deadline_commit
            assert sp.sender == self.data.owner
            self.data.nb_treasures += 1
            self.data.treasures[self.data.nb_treasures] = sp.record(hash = password_hash, found = False, player = self.data.owner, password = sp.bytes("0x00"))

        @sp.entrypoint
        def commit_discover_treasure(self, id, commit_data):
            assert sp.sender != self.data.owner
            assert sp.now <= self.data.deadline_commit
            assert not self.data.commits.contains(commit_data)
            self.data.commits[commit_data] = True
        
        @sp.entrypoint
        def reveal_discover_treasure(self, id, password):
            assert sp.now <= self.data.deadline_reveal
            treasure = self.data.treasures[id]
            assert not treasure.found
            self.data.treasures[id].found = True
            self.data.treasures[id].password = password
            self.data.treasures[id].player = sp.sender
            self.data.score_per_user[sp.sender] += 1
            if self.data.score_per_user[sp.sender] > self.data.score_per_user[self.data.current_winner]:
                self.data.current_winner = sp.sender

        # if someone detects that a reveal doesn't match a commitment, they can complain
        @sp.entrypoint
        def dispute_discovery(self, id):
            assert sp.now <= self.data.deadline_dispute
            treasure = self.data.treasures[id]
            assert treasure.found
            if sp.blake2b(treasure.password) == treasure.hash:
                expected_commit = sp.blake2b(sp.pack(sp.record(password = treasure.password, user = treasure.player)))
                assert not self.data.commits.contains(expected_commit)
            if self.data.score_per_user.contains(treasure.player):
                del self.data.score_per_user[treasure.player]
                sp.send(sp.sender, self.data.deposit)
            if treasure.player == self.data.current_winner:
                self.data.current_winner = self.data.owner
            self.data.treasures[id].found = False
            # we need to give more time for a player who really found it, to reveal it
            self.data.deadline_reveal = sp.add_seconds(self.data.deadline_reveal, 3600)
            self.data.deadline_dispute = sp.add_seconds(self.data.deadline_dispute, 3600)

        # If we eliminated the winner, we can't do a loop to recompute it, so we let the real winner claim their place
        @sp.entrypoint
        def update_winner(self):
            assert sp.now <= self.data.deadline_dispute
            assert self.data.score_per_user[sp.sender] > self.data.score_per_user[self.data.current_winner]
            self.data.current_winner = sp.sender

        @sp.entrypoint
        def claim_prize(self):
            assert sp.now > self.data.deadline_dispute
            assert sp.sender == self.data.current_winner
            sp.send(sp.sender, sp.balance)
                   
@sp.add_test(name='Geocaching test')
def test():
    alice = sp.test_account("alice").address
    bob = sp.test_account("bob").address
    carl = sp.test_account("carl").address
    scenario = sp.test_scenario(main)
    geocaching = main.Geocaching(alice, sp.timestamp(1000), sp.timestamp(2000), sp.timestamp(3000),sp.tez(1))
    scenario += geocaching
    geocaching.create_treasure(sp.blake2b(sp.pack("secret password 1"))).run(sender = alice, amount = sp.tez(100))
    geocaching.create_treasure(sp.blake2b(sp.pack("secret password 2"))).run(sender = alice)
    geocaching.create_treasure(sp.blake2b(sp.pack("secret password 3"))).run(sender = alice)

    geocaching.register_player().run(sender = bob, amount = sp.tez(1))
    geocaching.register_player().run(sender = carl, amount = sp.tez(1))
    
    # Correct commit and reveal for password 1
    commit_1 = sp.blake2b(sp.pack(sp.record(password = sp.pack("secret password 1"), user = bob)))
    geocaching.commit_discover_treasure(id = 1, commit_data = commit_1).run(sender = bob, now = sp.timestamp(100))
    geocaching.reveal_discover_treasure(id = 1, password = sp.pack("secret password 1")).run(sender = bob, now = sp.timestamp(100))

    # Try invalid password
    commit_fake = sp.blake2b(sp.pack(sp.record(password = sp.pack("false password"), user = bob)))
    geocaching.commit_discover_treasure(id = 2, commit_data = commit_fake).run(sender = bob, now = sp.timestamp(100))
    geocaching.reveal_discover_treasure(id = 2, password = sp.pack("false password")).run(sender = bob, now = sp.timestamp(100))
    geocaching.dispute_discovery(2).run(sender = carl)
    
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
    geocaching.claim_prize().run(sender = alice, now = sp.timestamp(100), valid = False)
    geocaching.claim_prize().run(sender = carl, now = sp.timestamp(1000), valid = False)
    geocaching.claim_prize().run(sender = alice, now = sp.timestamp(1000), valid=False)
    
