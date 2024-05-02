def bank():
    accounts = {}

    def balance_of(account):
        return accounts.get(account,0)
    
    def deposit(account, amount):
        accounts[account] = balance_of(account) + amount
    
    return balance_of, deposit

balance_of, deposit = bank()
deposit('Steve',3)

def counter():
    tally = 0
    def increment():
        tally += 1
        return tally
    return increment

inc = counter()
print(inc())