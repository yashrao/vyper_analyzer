_test: uint256

@private
def branch():
    if self._test == 1:
        self._test += 1

    for i in range(10):
        self._test += i
