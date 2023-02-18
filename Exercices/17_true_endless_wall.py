import smartpy as sp

class TrulyEndlessWall(sp.Contract):
    def __init__(self, owner):
        self.init(messages=sp.big_map(
                {},
                tkey = sp.TAddress,
                tvalue = sp.TRecord(text=sp.TString, timestamp=sp.TTimestamp)
            ),
            owner = owner)
       
 
    @sp.entry_point
    def write_message(self,text,timestamp):
       self.data.messages = sp.update_map(self.data.messages, sp.sender, sp.some(sp.record(text=text, timestamp= timestamp)))


       
@sp.add_test(name="testing truly endless wall")
def test():
    alice = sp.test_account("Alice").address
    bob = sp.test_account("Bob").address
    eve = sp.test_account("Eve").address
    axel = sp.test_account("Axel").address
    scenario = sp.test_scenario()
    c1 = TrulyEndlessWall(axel)
    scenario += c1
    c1.write_message(text="bob's message", timestamp=sp.timestamp(20)).run(sender= bob)
