@public
def _swapOneSplit(testADDR: address,
                  fromToken: address,               \
                  toToken: address,                 \
                  amount: uint256,                  \
                  minReturn: uint256,               \
                  trade_dist: uint256[4],           \
                  disableFlags: uint256):
    funcSig: bytes[4] = method_id("swap(address,address,uint256,uint256,uint256[],uint256)", bytes[4])
    data: bytes[352] = concat(convert(fromToken, bytes32),            \
                              convert(toToken, bytes32),              \
                              convert(amount, bytes32),               \
                              convert(minReturn, bytes32),            \
                              convert(160, bytes32),                  \
                              convert(4, bytes32),                    \
                              convert(trade_dist[0], bytes32),        \
                              convert(trade_dist[1], bytes32),        \
                              convert(trade_dist[2], bytes32),        \
                              convert(trade_dist[3], bytes32),        \
                              convert(disableFlags, bytes32)          \
                            )
    full_data: bytes[356] = concat(funcSig, data)
    raw_call(
        testADDR,
        full_data,
        outsize=0,
        gas=msg.gas,
        delegate_call=True
    )
