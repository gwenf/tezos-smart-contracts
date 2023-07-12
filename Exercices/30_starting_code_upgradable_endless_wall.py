import smartpy as sp

@sp.module
def main():
    
    class EndlessWall(sp.Contract):
       def __init__(self, owner):
           self.data.wall_content = sp.big_map({})
           self.data.owner = owner
    
       @sp.entrypoint
       def write_message(self, message):
           data = sp.record(text = "", timestamp = sp.timestamp(0))
           if self.data.wall_content.contains(sp.sender):
               data = self.data.wall_content[sp.sender]
               data.text += "," + message
           else:
               data.text = message
           data.timestamp = sp.now
           self.data.wall_content[sp.sender] = data

       @sp.onchain_view
       def read_messages(self, user):
           return self.data.wall_content[user]
