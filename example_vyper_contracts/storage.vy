number_var: uint256

@external
def store(num: int128):
    self.number_var = num
    
@external
def retrieve() -> int128:
    return self.number_var

@external
def add_num():
    self.number_var += 10
    
@external
def subtract_num():
    self.number_var -= 10
    

