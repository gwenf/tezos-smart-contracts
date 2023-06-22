import smartpy as sp

@sp.module
def main():

    class Auction(sp.Contract):
        def __init__(self):
            self.data.items = {}
            self.data.tokens = {}
            self.data.token_id = 1

        @sp.entrypoint
        def mint(self, metadata):
            self.data.tokens[self.data.token_id] = sp.record(metadata = metadata, owner = sp.sender)
            self.data.token_id += 1
        
        @sp.entrypoint
        def open_auction(self, item_id, seller, deadline):
            # Bug 1, 2, 3, 4
            # bug 1
            self.data.items[item_id] = sp.record(seller = seller,
                                                deadline = deadline,
                                                top_bid = sp.tez(0),
                                                top_bidder = seller
                                               )
    
        @sp.entrypoint
        def bid(self, item_id):
            item = self.data.items[item_id]
            assert sp.amount > item.top_bid
            assert sp.now < item.deadline
            sp.send(item.top_bidder, item.top_bid) # Bug 4
            item.top_bid = sp.amount
            item.top_bidder = sp.sender
            self.data.items[item_id] = item

        @sp.entrypoint
        def claim_top_bid(self, item_id):
            item = self.data.items[item_id]
            assert sp.now >= item.deadline
            assert sp.sender == item.seller # Potential bug 6 if missing
            sp.send(item.seller, item.top_bid) # Bug 5
            self.data.tokens[item_id].owner = item.top_bidder # Bug 7

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
    auctionContract.open_auction(item_id = 1, seller = seller1, deadline = sp.timestamp(100))
    auctionContract.bid(1).run(sender = alice, amount = sp.tez(1), now = sp.timestamp(1))
    auctionContract.bid(1).run(sender = bob, amount = sp.tez(2), now = sp.timestamp(2))
    auctionContract.claim_top_bid(1).run(sender = seller1, now = sp.timestamp(101))
