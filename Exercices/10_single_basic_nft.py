import smartpy as sp

class SingleBasicNFT(sp.Contract):
  def __init__(self, first_owner):
      self.init(owner=first_owner, metadata="Gwen\'\s first NFT")

  @sp.entry_point
  def transfer(self, new_owner):
      sp.verify(sp.sender== self.data.owner, "not your property")
      self.data.owner = new_owner

  @sp.add_test(name="update owner")
  def test():
      alice= sp.test_account("alice").address
      bob = sp.test_account("bob").address
      eve = sp.test_account("eve").address
      c1 = SingleBasicNFT(alice)
      scenario = sp.test_scenario()
      scenario +=c1
      c1.transfer(bob).run(sender=alice)
      c1.transfer(eve).run(sender=bob)
      c1.transfer(alice).run(sender=eve)