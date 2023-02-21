import smartpy as sp

@sp.module
def main():
    class TrulyEndlessWall(sp.Contract):
        def __init__(self, owner):
            self.data.messages = sp.cast(sp.big_map({}),
                                         sp.big_map[sp.address,
                                                    sp.record(text = sp.string,
                                                              timestamp = sp.timestamp)
                                         ]
                                        )
            self.data.owner = owner
           
     
        @sp.entrypoint
        def write_message(self, text, timestamp):
           self.data.messages[sp.sender] = sp.record(text = text, timestamp = timestamp)
    
       
@sp.add_test(name="testing truly endless wall")
def test():
    alice = sp.test_account("Alice").address
    bob = sp.test_account("Bob").address
    eve = sp.test_account("Eve").address
    axel = sp.test_account("Axel").address
    scenario = sp.test_scenario(main)
    c1 = main.TrulyEndlessWall(axel)
    scenario += c1
    c1.write_message(text="bob's message", timestamp=sp.timestamp(20)).run(sender= bob)
