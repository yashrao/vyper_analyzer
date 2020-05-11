number_var: int128

@public 
def store(num: int128):
    self.number_var = num
    
@public
def retrieve() -> int128:
    return self.number_var

@public
def add_num():
    self.number_var += 10
    
@public
def subtract_num():
    self.number_var -= 10
    

