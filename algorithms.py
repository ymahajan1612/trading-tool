
def checkSMACrossOver(stock_data):
    """
    Returns:
    int: 1 for buy signal, -1 for sell signal and 0 for hold. 
    """
    curr = stock_data.iloc[-1]
    prev = stock_data.iloc[-2]
    
    # Generate Buy Signal
    if (prev.SMA_short < prev.SMA_long) and (curr.SMA_short > curr.SMA_long):
        return 1
    
    # Sell Signal
    if (prev.SMA_short > prev.SMA_long) and (curr.SMA_short < curr.SMA_long):
        return -1
    
    # hold
    return 0 


