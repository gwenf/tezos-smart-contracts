
@sp.entrypoint
def bid(self, hashValue):
    assert sp.amount == self.data.bidAmount + self.data.depositAmount
    assert sp.now < self.data.deadlineCommit
    self.data.players[self.data.nbPlayers] = sp.record(address = sp.sender, hash = hashValue, revealed = False)
    self.data.nbPlayers += 1
    self.data.totalDeposits += self.data.depositAmount

@sp.entrypoint
def reveal(self, idPlayer, value):
    assert sp.now < self.data.deadlineReveal
    player = self.data.players[iPlayer]
    assert player.hashValue == sp.blake2b(value)
    self.data.players[idPlayer].reveal = True
    self.data.total += value
    self.data.nbRevealed += 1

@sp.entrypoint
def claimPrize(self):
    assert sp.now > self.data.deadlineReveal
    idWinner = self.data.total % self.data.nbPlayers
    winner = players[idWinner].address
    assert winner.revealed
    amount = sp.data.bidAmount * self.data.nbPlayers
    amount += self.data.totalDeposits / nbRevealed
    sp.send(winner, amount)
    del self.data.players[idWinner]

@sp.entrypoint
def claimDeposit(self, idPlayer):
    assert sp.now > self.data.deadlineReveal
    player = self.data.players[idPlayer]
    assert player.revealed
    user = players[idPlayer].address
    sp.send(user, self.data.totalDeposits / nbRevealed)
    del self.data.players[idPlayer]
