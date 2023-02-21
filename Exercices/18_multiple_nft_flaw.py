import smartpy as sp

@sp.module
def main():

    class MultipleNftSingleContract(sp.Contract):
        def __init__(self, owner):
            self.data.owner = owner
            self.data.next_id = 1
            self.data.tokens = sp.big_map ({})
    
        @sp.entrypoint
        def buy(self, token_id):
            #Checks that tokens[tokenID] exists, call it token
            assert self.data.tokens.contains(token_id)
            token = self.data.tokens[token_id]
            #Check that the amount transferred is equal to the price of the token
            assert sp.amount == token.price
            #Send 5% of the price to the author of the token
            author_fee = sp.split_tokens(token.price, 5, 100)
            #sp.send(token.author, author_fee)
            sp.send(self.data.owner, sp.amount - author_fee)
            sp.send(token.author, author_fee)
            #Replace owner with the caller in the token
            token.owner = sp.sender
            #Increase price by 10% in the token
            token.price += sp.split_tokens(token.price, 10, 100)
    
        @sp.entrypoint
        def mint(self, metadata, price):
            #Create a new entry in tokens, with key nextID
            #Set owner and author to the address of the caller
            #Set metadata and price to the value of the parameters
            self.data.tokens[self.data.next_id] = sp.record(metadata = metadata, price = price, owner = sp.sender, author = sp.sender)
            #Increment nextID
            self.data.next_id += 1

@sp.add_test(name='Test One')
def test():
    author = sp.test_account('author').address
    alice = sp.test_account('alice').address
    bob = sp.test_account('bob').address
    eve = sp.test_account('eve').address
    c1 = main.MultipleNftSingleContract(alice)
    scenario = sp.test_scenario(main)
    scenario += c1
    c1.mint(metadata='second contract', price=sp.tez(2)).run(sender=author)
    c1.buy(1).run(sender=bob, amount=sp.tez(2))
    scenario.verify(c1.balance == sp.tez(0))
