from datetime import datetime


def fmt_wei(v: int, decimals=18): return f"{v / (10**decimals):.6f}"

def time_ago(ts): 
    d = datetime.utcfromtimestamp(ts)
    s = (datetime.utcnow() - d).total_seconds()
    return f"{int(s//60)}m ago" if s<3600 else f"{int(s//3600)}h ago"

def short(addr): return addr[:6] + "…" + addr[-4:]