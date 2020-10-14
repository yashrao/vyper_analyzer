@internal
def branch():
    test: uint256 = 0
    test_2: uint256 = 1
    test_3: uint256 = 1
    for i in range(10):
        test += 1
        test += 2
    if test == 1:
        test += 1
        test_2 += 1
    elif test == 7:
        test_3 += 1000
    else:
        test_2 += 1
    test_4: uint256 = 3
    

