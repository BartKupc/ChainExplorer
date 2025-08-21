import os
from web3 import Web3
from core.chain_manager import ChainManager
import os
import sys
from pathlib import Path
from web3.exceptions import BlockNotFound
from web3.datastructures import AttributeDict
from web3.exceptions import TransactionNotFound
from hexbytes import HexBytes
import time
from requests.exceptions import HTTPError
from datetime import datetime

from config import get_chains, get_default_chain

PAGE_BLOCK_STEP = int(os.getenv("LOGS_PAGE_BLOCK_STEP", "2000"))  # try 1000–1500 on Cronos

TRANSFER_TOPIC = Web3.keccak(text="Transfer(address,address,uint256)").hex()
if not TRANSFER_TOPIC.startswith("0x"):
    TRANSFER_TOPIC = "0x" + TRANSFER_TOPIC

BLOCK_WINDOW = int(os.getenv("DEFAULT_BLOCK_WINDOW", "5000"))  # tune in .env


mgr = ChainManager()

def jsonable(x):
    if isinstance(x, HexBytes):                 # 0x-prefixed hex for bytes
        return x.hex()
    if isinstance(x, (bytes, bytearray)):
        return "0x" + x.hex()
    if isinstance(x, AttributeDict):            # recurse dict-like
        return {k: jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):            # recurse lists
        return [jsonable(v) for v in x]
    return x

def get_chain_id(chain_key: str) -> int:
    return mgr.get_web3(chain_key).eth.chain_id
    
def get_chain_name(chain_key: str) -> str:
    return mgr.meta(chain_key)["name"]

def get_block_number(chain_key: str) -> int:
    return mgr.get_web3(chain_key).eth.block_number


def get_block(ref: str | int, chain: str | None = None, full_txs: bool = True) -> dict:

    
    w3 = mgr.get_web3(chain)

    # convert "12345" -> 12345 (block number)
    if isinstance(ref, str) and ref.isdigit():
        ref = int(ref)

    try:
        b = w3.eth.get_block(ref, full_transactions=full_txs)
        return b
    except BlockNotFound as e:
        print(f"❌ BlockNotFound: {e}")
        raise
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")
        raise

    # (shape just what you need)
    return jsonable(b)

def latest_blocks(n: int, chain=None):
    w3 = mgr.get_web3(chain)
    head = w3.eth.block_number
    f, t = max(head - n, 0), head
    out = []
    for b in range(t, f, -1):
        out.append(jsonable(w3.eth.get_block(b, full_transactions=False)))

    return out

def blocks_from(start: int, n: int, chain=None):
    w3 = mgr.get_web3(chain)
    head = w3.eth.block_number
    start = min(int(start), head)              # clamp if start > head
    n = max(1, int(n))

    end = max(0, start - (n - 1))              # inclusive lower bound
    nums = range(start, end - 1, -1)           # e.g. 10..6

    return [jsonable(w3.eth.get_block(i, full_transactions=False)) for i in nums]


def _topic_for_addr(addr: str) -> str:
    a = addr.lower().replace("0x", "")
    return "0x" + ("0" * 24) + a

def _get_logs_paged(w3, base_params: dict, step: int, cap: int):
    f = int(base_params["fromBlock"]); t = int(base_params["toBlock"])
    out = []
    while f <= t and len(out) < cap:
        end = min(f + step, t)
        params = dict(base_params)
        params["fromBlock"], params["toBlock"] = f, end
        out.extend(w3.eth.get_logs(params))
        f = end + 1
    return out[:cap]

def _normalize_token_filter(tokens, w3):
    if not tokens:
        return None
    if isinstance(tokens, str):
        tokens = [tokens]
    return [w3.to_checksum_address(a) for a in tokens]


def transfers_per_wallet(holder: str| None, chain: str|None=None,
                         window: int|None=None, max_logs: int = 2000,
                         tokens: str | None = None):
    w3 = mgr.get_web3(chain)
    head = w3.eth.block_number
    f, t = max(head - (window or BLOCK_WINDOW), 0), head
    addr_filter = _normalize_token_filter(tokens, w3)

    if holder is None:
        if not addr_filter:
            raise ValueError("token-only mode requires tokens=[...] to be set")
        base = {"fromBlock": f, "toBlock": t, "topics": [TRANSFER_TOPIC], "address": addr_filter}
        logs = _get_logs_paged(w3, base, PAGE_BLOCK_STEP, max_logs)
        formatted_time = datetime.fromtimestamp(logs[0]["blockNumber"]).strftime('%Y-%m-%d %H:%M:%S')
            
        out = [{
            "token": l["address"],
            "from":  "0x" + l["topics"][1].hex()[-40:],
            "to":    "0x" + l["topics"][2].hex()[-40:],
            "value_raw": Web3.to_int(l["data"]),
            "block": l["blockNumber"],
            "timestamp": formatted_time,
            "tx":    l["transactionHash"].hex(),
        } for l in logs if len(l["topics"]) >= 3]

        out.sort(key=lambda x: x["block"], reverse=True)
        return out

    else:

        topic_addr = _topic_for_addr(holder)
        base_from = {"fromBlock": f, "toBlock": t, "topics": [TRANSFER_TOPIC, topic_addr, None]}
        base_to   = {"fromBlock": f, "toBlock": t, "topics": [TRANSFER_TOPIC, None, topic_addr]}
        if addr_filter:
            base_from["address"] = addr_filter
            base_to["address"]   = addr_filter

        logs_from = _get_logs_paged(w3, base_from, PAGE_BLOCK_STEP, max_logs)
        logs_to   = _get_logs_paged(w3, base_to,   PAGE_BLOCK_STEP, max_logs)

        # dedupe
        seen, merged = set(), []
        for l in (logs_from + logs_to):
            key = (l["transactionHash"].hex(), l["logIndex"])
            if key in seen:
                continue
            seen.add(key)
            merged.append(l)

        logs = merged[:max_logs]
        formatted_time = datetime.fromtimestamp(logs[0]["blockNumber"]).strftime('%Y-%m-%d %H:%M:%S')
        out = [{
            "token": l["address"],
            "from":  "0x" + l["topics"][1].hex()[-40:],
            "to":    "0x" + l["topics"][2].hex()[-40:],
            "value_raw": Web3.to_int(l["data"]),
            "block": l["blockNumber"],
            "timestamp": formatted_time,
            "tx":    l["transactionHash"].hex(),
        } for l in logs if len(l["topics"]) >= 3]

        out.sort(key=lambda x: x["block"], reverse=True)
        return out

def get_tx(txhash: str, chain: str|None=None) -> dict:
    w3 = mgr.get_web3(chain)
    try:
        tx = w3.eth.get_transaction(txhash)
    except TransactionNotFound:
        raise

    try:
        rcpt = w3.eth.get_transaction_receipt(txhash)
    except TransactionNotFound:
        rcpt = None

    return {
    "tx": jsonable(tx),
    "receipt": jsonable(rcpt) if rcpt else None,
    "logs": jsonable(rcpt.logs) if rcpt else None,
}

def native_balance(addr: str, chain: str|None=None) -> int:
    return mgr.get_web3(chain).eth.get_balance(addr)


def classify_transaction_type(tx):
    """Classify transaction type more generally"""
    
    # Convert input data to string for comparison
    input_data = tx['input'].hex() if tx['input'] else ''
    

    # Contract deployment (no recipient)
    if not tx['to']:
        return 'contract_deploy'
    
    # No data = native coin transfer
    elif input_data == '0x' or input_data == '':
        return 'coin_transfer'
    
    # ERC20 transfer (transfer function)
    elif input_data.startswith('0xa9059cbb'):  # transfer(address,uint256)
        return 'erc20_transfer'
    
    # ERC20 transferFrom (transferFrom function)
    elif input_data.startswith('0x23b872dd'):  # transferFrom(address,address,uint256)
        return 'erc20_transfer'
    
    # ERC20 approve (approve function)
    elif input_data.startswith('0x095ea7b3'):  # approve(address,uint256)
        return 'erc20_approve'
    
    # Contract call (any other data)
    else:
        return 'contract_call'


def get_all_blocks(chain: str|None=None, n: int=20, classify: bool = False, start_block: int|None=None):
    """Get blocks with simple sequential pagination"""
    w3 = mgr.get_web3(chain)
    
    # Calculate start and end blocks - always use simple sequential pagination
    if start_block is None:
        # Default: latest blocks
        latest_block = get_block_number(chain)
        start_block = latest_block
        end_block = max(latest_block - n + 1, 0)
    else:
        # Start from specified block and go backwards
        end_block = max(start_block - n + 1, 0)
    
    print(f"Processing blocks {end_block} to {start_block} (total: {start_block - end_block + 1} blocks)")
    
    blocks = []
    
    for block_num in range(start_block, end_block - 1, -1):
        try:
            # Small delay between blocks
            time.sleep(0.01)
            
            # If classification is needed, get full transactions
            full_txs = classify
            block = w3.eth.get_block(block_num, full_transactions=full_txs)
            formatted_time = datetime.fromtimestamp(block.timestamp).strftime('%Y-%m-%d %H:%M:%S')
            
            if classify:
                # For classification, return full transaction data
                block_data = {
                    'number': block.number,
                    'hash': block.hash.hex(),
                    'timestamp': formatted_time,
                    'transactions': block.transactions,  # Full objects
                    'gasUsed': block.gasUsed,
                    'gasLimit': block.gasLimit,
                    'miner': block.miner,
                    'size': block.size
                }
            else:
                # For display, just count transactions
                block_data = {
                    'number': block.number,
                    'hash': block.hash.hex(),
                    'timestamp': formatted_time,
                    'transactions': len(block.transactions),  # Just count
                    'gasUsed': block.gasUsed,
                    'gasLimit': block.gasLimit,
                    'miner': block.miner,
                    'size': block.size
                }
            
            blocks.append(block_data)
            
        except Exception as e:
            if "429" in str(e) or "rate limit" in str(e).lower():
                print(f"Rate limit hit at block {block_num}, waiting 3 seconds...")
                time.sleep(3)
                continue
            else:
                print(f"Error at block {block_num}: {e}")
                continue
    
    print(f"Total blocks found: {len(blocks)}")
    return blocks


def get_all_blocks_simple(chain: str|None=None, n: int=20, classify: bool = False, start_block: int|None=None):
    """Get blocks with simple sequential pagination"""
    w3 = mgr.get_web3(chain)
    
    # Calculate start and end blocks
    if start_block is None:
        # Default: latest blocks
        latest_block = get_block_number(chain)
        start_block = latest_block
        end_block = max(latest_block - n + 1, 0)
    else:
        # Start from specified block and go backwards
        end_block = max(start_block - n + 1, 0)
    
    print(f"Processing blocks {end_block} to {start_block} (total: {start_block - end_block + 1} blocks)")
    
    blocks = []
    
    for block_num in range(start_block, end_block - 1, -1):
        try:
            # Small delay between blocks
            time.sleep(0.01)
            
            # If classification is needed, get full transactions
            full_txs = classify
            block = w3.eth.get_block(block_num, full_transactions=full_txs)
            formatted_time = datetime.fromtimestamp(block.timestamp).strftime('%Y-%m-%d %H:%M:%S')
            
            if classify:
                # For classification, return full transaction data
                block_data = {
                    'number': block.number,
                    'hash': block.hash.hex(),
                    'timestamp': formatted_time,
                    'transactions': block.transactions,  # Full objects
                    'gasUsed': block.gasUsed,
                    'gasLimit': block.gasLimit,
                    'miner': block.miner,
                    'size': block.size
                }
            else:
                # For display, just count transactions
                block_data = {
                    'number': block.number,
                    'hash': block.hash.hex(),
                    'timestamp': formatted_time,
                    'transactions': len(block.transactions),  # Just count
                    'gasUsed': block.gasUsed,
                    'gasLimit': block.gasLimit,
                    'miner': block.miner,
                    'size': block.size
                }
            
            blocks.append(block_data)
            
        except Exception as e:
            if "429" in str(e) or "rate limit" in str(e).lower():
                print(f"Rate limit hit at block {block_num}, waiting 3 seconds...")
                time.sleep(3)
                continue
            else:
                print(f"Error at block {block_num}: {e}")
                continue
    
    print(f"Total blocks found: {len(blocks)}")
    return blocks

