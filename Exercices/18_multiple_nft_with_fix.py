import smartpy as sp

@sp.module
def main():

    class NftMarketplace(sp.Contract):
        def __init__(self, fee_rate, admin ):
            self.data.fee_rate= fee_rate
            self.data.admin = admin
            self.data.tokens = sp.cast(
                sp.big_map({}),
                sp.big_map[sp.pair(sp.contract, sp.int), sp.record]
            )
            self.data.ledger = sp.cast(sp.big_map({}), sp.big_map[sp.address, sp.mutez])                         
       
        def add_to_ledger(self, user, amount):
            self.data.ledger[user] = self.data.ledger.get(user, sp.tez(0)) + amount
    
        @sp.entry_point
        def addToMarketplace(self, contract, tokenID, price):
            #Check that the caller is the owner of the token
            owner = sp.view("getOwner",contract, tokenID, t = sp.TAddress)
            assert owner == sp.sender
            #Add a contract/tokenID entry to tokens big-map, and store caller as the seller, and the price
            self.data.tokens[(contract, tokenID)] = sp.record(price=price, owner=sp.sender)
            #Transfer token ownership to the marketplace
            #Transfer token ownership to the marketplace
            entryType = sp.TRecord(sp.TNat, sp.TAddress)
            myContract = sp.contract(entryType, contract, 'transfer').open_some()
            sp.transfer((tokenId, ), sp.tez(0), myContract)
           
    
        @sp.entry_point
        def removeFromMarketplace(self, contract, tokenID):
            #Check that the caller is the seller
            assert sp.sender == self.data.tokens[(contract, token_id)].owner, 'not your property'
            #Transfer token ownership back to the seller
            myContract = sp.contract(entryType, contract, 'transfer').unwrap_some()
            sp.transfer((tokenId, sp.sender), sp.tez(0), myContract)
            del self.data.tokens[(contract, token_id)]
    
    
        
        @sp.entry_point
        def buy(self, token_id):
            #Checks that tokens[tokenID] exists, call it token
            assert self.data.tokens.contains(token_id)
            #Check that the amount transferred is equal to the price of the token
            assert sp.amount == self.data.tokens[token_id].price
            #Send 5% of the price to the author of the token
            author_fee = sp.split_tokens(self.data.tokens[token_id].price, 5, 100)
            sp.send(self.data.author, author_fee)
            self.add_to_ledger(self.data.owner, sp.amount - author_fee)
            self.add_to_ledger(self.data.author, author_fee)
            #Replace owner with the caller in the token
            sp.sender = self.data.ledger[token_id].owner
            #Increase price by 10% in the token
            self.data.tokens[token_id].price += sp.split_tokens(self.data.tokens[token_id].price, 10, 100)
    
        @sp.entry_point
        def mint(self, metadata, price):
            #Create a new entry in tokens, with key nextID
            #Set owner and author to the address of the caller
            #Set metadata and price to the value of the parameters
            self.data.tokens[self.data.next_id] = sp.record(metadata = metadata, price = price, owner = sp.sender, author = sp.sender)
            #Increment nextID
            self.data.next_id += 1
        
        @sp.entry_point
        def claim(self):
            #Verify that ledger[caller] exists
            sp.verify(self.data.ledger.contains(sp.sender), 'You do not own any token')
            #Create a transaction to send ledger[caller].value to caller
            sp.send(sp.sender, self.data.ledger[sp.sender])
            #Delete ledger[caller]
            del (self.data.ledger[sp.sender])
    
@sp.add_test(name='Test One')
def test():
    author = sp.test_account('author').address
    alice = sp.test_account('alice').address
    bob = sp.test_account('bob').address
    eve = sp.test_account('eve').address
    c1 = main.NftMarketplace(admin=alice, fee_rate=sp.nat(3))
    scenario = sp.test_scenario(main)
    c1 += scenario
    c1.mint(metadata = 'second contract', price = sp.tez(2)).run(sender = alice, amount = sp.tez(2))
