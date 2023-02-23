import smartpy as sp

class MultipleNftSingleContract(sp.Contract):
    def __init__(self, owner):
        self.init(
            owner = owner,
            next_id =1,
            tokens = sp.big_map ({}),
            ledger = sp.big_map({}, tkey = sp.TAddress, tvalue = sp.TMutez) 
        )
                    
   
    def add_to_ledger(self, user, amount):
        self.data.ledger[user] = self.data.ledger.get(user, sp.tez(0)) + amount
    
    @sp.entry_point
    def buy(self, token_id):
        #Checks that tokens[tokenID] exists, call it token
        sp.verify(self.data.tokens.contains(token_id))
        token = self.data.tokens[token_id]
        #Check that the amount transferred is equal to the price of the token
        sp.verify(sp.amount == token.price)
        #Send 5% of the price to the author of the token
        author_fee = sp.split_tokens(token.price, 5, 100)
        #sp.send(token.author, author_fee)
        self.add_to_ledger(self.data.owner, sp.amount - author_fee)
        self.add_to_ledger(token.author, author_fee)
        #Replace owner with the caller in the token
        token.owner = sp.sender
        #Increase price by 10% in the token
        token.price += sp.split_tokens(token.price, 10, 100)

    @sp.entry_point
    def mint(self, metadata, price):
        #Create a new entry in tokens, with key nextID
        #Set owner and author to the address of the caller
        #Set metadata and price to the value of the parameters
        self.data.tokens[self.data.next_id] = sp.record(metadata=metadata, price = price, owner=sp.sender, author=sp.sender)
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
    c1 = MultipleNftSingleContract(alice)
    scenario = sp.test_scenario()
    scenario += c1
    c1.mint(metadata='second contract', price=sp.tez(2)).run(sender=author)
    c1.buy(1).run(sender=bob, amount=sp.tez(2))
    c1.claim().run(sender=author)
    c1.claim().run(sender=alice)