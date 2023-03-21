import smartpy as sp

@sp.module
def main():

    class Auction(sp.Contract):
        def __init__(self):
            self.data.items = {}
            self.data.tokens = {}
            self.data.tokenID = 1

        @sp.entrypoint
        def mint(self, metadata):
            self.data.tokens[self.data.tokenID] = sp.record(metadata = metadata, owner = sp.sender)
            self.data.tokenID += 1
        
        @sp.entrypoint
        def openAuction(self, itemID, seller, deadline):
            # Bug 1, 2, 3, 4
            # bug 1
            self.data.items[itemID] = sp.record(seller = seller,
                                                deadline = deadline,
                                                topBid = sp.tez(0),
                                                topBidder = seller
                                               )
    
        @sp.entrypoint
        def bid(self, itemID):
            item = self.data.items[itemID]
            assert sp.amount > item.topBid
            assert sp.now < item.deadline
            sp.send(item.topBidder, item.topBid) # Bug 4
            item.topBid = sp.amount
            item.topBidder = sp.sender
            self.data.items[itemID] = item

        @sp.entrypoint
        def claimTopBid(self, itemID):
            item = self.data.items[itemID]
            assert sp.now >= item.deadline
            assert sp.sender == item.seller # Potential bug 6 if missing
            sp.send(item.seller, item.topBid) # Bug 5
            self.data.tokens[itemID].owner = item.topBidder # Bug 7

@sp.add_test(name='Testing extortion attack')
def test():
    seller1 = sp.test_account("seller1").address
    seller2 = sp.test_account("seller2").address
    alice = sp.test_account("alice").address
    bob = sp.test_account("bob").address
    scenario = sp.test_scenario(main)
    auctionContract = main.Auction()
    scenario += auctionContract
    auctionContract.mint("Mon NFT").run(sender = seller1)
    auctionContract.openAuction(itemID = 1, seller = seller1, deadline = sp.timestamp(100))
    auctionContract.bid(1).run(sender = alice, amount = sp.tez(1), now = sp.timestamp(1))
    auctionContract.bid(1).run(sender = bob, amount = sp.tez(2), now = sp.timestamp(2))
    auctionContract.claimTopBid(1).run(sender = seller1, now = sp.timestamp(101))
