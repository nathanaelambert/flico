from datetime import datetime
def large_number_for_display(x: int) -> str:
    if x < 1e3:
        return x
    elif x < 1e6:
        return f"{x/1e3:.1f}k"
    elif x < 1e9:
        return f"{x/1e6:.1f}M"
    else:
        return f"{x/1e9:.1f}B"

def unix_timestamp_for_display(x: int)-> str:
    return datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S')