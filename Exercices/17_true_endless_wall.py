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
           data = sp.record(text = "", timestamp = sp.timestamp(0))
           if self.data.messages.contains(sp.sender):
               data = self.data.messages[sp.sender]
               data.text += "," + text
           else:
               data.text = text
           data.timestamp = timestamp
           self.data.messages[sp.sender] = data
    
       
@sp.add_test(name="testing truly endless wall")
def test():
    alice = sp.test_account("Alice").address
    bob = sp.test_account("Bob").address
    eve = sp.test_account("Eve").address
    axel = sp.test_account("Axel").address
    scenario = sp.test_scenario(main)
    c1 = main.TrulyEndlessWall(axel)
    scenario += c1
    c1.write_message(text="bob's message 1", timestamp=sp.timestamp(20)).run(sender= bob)
    c1.write_message(text="bob's message 2", timestamp=sp.timestamp(30)).run(sender= bob)
