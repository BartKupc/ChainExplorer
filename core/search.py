import re



HEX = re.compile(r"^(0x)?[0-9a-fA-F]+$")

def classify(q: str):
    s = (q or "").strip()
    if not s:
        return ("unknown", None)

    # block number
    if s.isdigit():
        return ("block", int(s))

    # hex strings
    if HEX.match(s):
        h = s if s.startswith("0x") else "0x" + s

        # addresses: 42 chars incl 0x
        if len(h) == 42:
            return ("address", h)

        # tx/block hashes: 66 chars incl 0x
        if len(h) == 66:
            # keep it simple: treat as tx hash by default
            # (optional: try tx first; if not found, treat as block hash)
            return ("tx", h)

    return ("unknown", s)
