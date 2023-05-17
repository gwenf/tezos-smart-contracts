import smartpy as sp
@sp.module
def main():

    class StoreValue(sp.Contract):
        def __init__(self):
            self.data.stored_value = 42
