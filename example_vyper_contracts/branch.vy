@internal
def branch():
    test: uint256 = 0
    test_2: uint256 = 1
    test_3: uint256 = 1
    if test == 0:
    	test_2 += 1
    else:
    	test_3 += 1
    
@external
def test_fn():
    test: uint256 = 0
    test += 1
