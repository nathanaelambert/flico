from datetime import datetime
def large_number_for_display(x: int) -> str:
    if x < 1e3:
        result = x
    elif x < 1e6:
        result = f"{x/1e3:.1f}k"
    elif x < 1e9:
        result = f"{x/1e6:.1f}M"
    else:
        result = f"{x/1e9:.1f}B"
    return f"{result:>6}"[:6]

def unix_timestamp_for_display(x: int)-> str:
    return datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S')