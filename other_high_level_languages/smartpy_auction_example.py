import smartpy as sp

    class Auction(sp.Contract):
        def __init__(self, owner, deadline):
            self.init(owner = owner, deadline = deadline, topBidder = owner,
                bids = { owner: sp.tez(0) })
    
        @sp.entry_point
        def bid(self):
            sp.verify(sp.now < self.data.deadline, "Too late!")
            bids = self.data.bids
            sp.verify(~bids.contains(sp.sender), "You already bid")
            bids[sp.sender] = sp.amount
            sp.if sp.amount > bids[self.data.topBidder]:
                self.data.topBidder = sp.sender
    
        @sp.entry_point
        def collectTopBid(self):
            sp.verify(sp.now >= self.data.deadline, "Too early!")
            sp.verify(sp.sender == self.data.owner)
            sp.send(sp.sender, self.data.bids[self.data.topBidder])
            del self.data.bids[self.data.topBidder]
        
        @sp.entry_point
        def claim(self):
            sp.verify(self.data.bids.contains(sp.sender))
            sp.verify(sp.now >= self.data.deadline, "To early!")
            sp.verify(sp.sender != self.data.topBidder, "You won the auction")
            sp.send(sp.sender, self.data.bids[sp.sender])
            del self.data.bids[sp.sender]
