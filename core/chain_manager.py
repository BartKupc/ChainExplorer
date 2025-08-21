from typing import Dict, Any
from threading import Lock
from web3 import Web3
import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import get_chains, get_default_chain


class ChainManager:
    def __init__(self, timeout: int = 20):
        self._timeout = timeout
        self._clients: dict[str, Web3] = {}
        self._lock = Lock()

    def _profile(self,chain_key: str) -> dict:
        chains = get_chains()

        if chain_key not in chains.keys():
            raise KeyError(f"Chain {chain_key} not found")
        return chains[chain_key]
    
    # In core/chain_manager.py
    def _build(self, chain_key: str) -> Web3:

        p = self._profile(chain_key)
      
        # Try primary RPC first
        try:
            w3 = Web3(Web3.HTTPProvider(p["rpc_url"], request_kwargs={"timeout": self._timeout}))
            if w3.is_connected() and w3.eth.chain_id == int(p["chain_id"]):
                return w3
        except:
            pass
        
        # Primary failed, try fallback
        fallback_rpc = p.get("fallback")
        if fallback_rpc:
            try:
                w3 = Web3(Web3.HTTPProvider(fallback_rpc, request_kwargs={"timeout": self._timeout}))
                if w3.is_connected() and w3.eth.chain_id == int(p["chain_id"]):
                    print(f"⚠️ {chain_key}: Primary RPC failed, using fallback")
                    return w3
            except:
                pass
        

        raise ConnectionError(f"Chain {chain_key} is not reachable")
    
    def get_web3(self, chain_key: str | None = None) -> Web3:
        key = chain_key or get_default_chain()
        with self._lock:
            if key not in self._clients:
                self._clients[key] = self._build(key)
            return self._clients[key]

    def meta(self, chain_key: str | None = None) -> dict:
        return self._profile(chain_key or get_default_chain())

    def reset(self, chain_key: str | None = None) -> None:
        with self._lock:
            self._clients.pop(chain_key, None) if chain_key else self._clients.clear()

    def health(self, chain_key: str | None = None) -> dict:
        k = chain_key or get_default_chain()
        w3 = self.get_web3(k)
        return {"chain_key": k, "chain_id": w3.eth.chain_id, "latest_block": w3.eth.block_number}

