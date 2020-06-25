sent: public(bool)                                                             

@public
def __init__():                                                                
    self.sent = False                                                          
                                                                               
@public                                                                        
@nonreentrant("exampleKey")                                                    
def sendFunc(to: address) -> uint256:                                          
    if self.sent == False:                                                     
        send(to, 1)                                                            
        self.sent = True                                                       
    return 1               
