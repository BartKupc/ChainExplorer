# config.py
import os, yaml
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 1) Load chains.yaml
CHAINS_YAML = Path(__file__).resolve().parent / "chains.yaml"

def seed_chains_from_yaml():
    """Seed database with chains from YAML file"""
    try:
        from models.chains import db, Chain
        
        # Read YAML file
        data = yaml.safe_load(CHAINS_YAML.read_text(encoding="utf-8"))
        raw_chains = data.get("chains", {})
        
        # Check if chains already exist
        existing_chains = Chain.query.filter_by(is_preset=True).count()
        
        if existing_chains == 0:
            # Add chains from YAML
            for key, chain_data in raw_chains.items():
                chain = Chain(
                    key=key,
                    chain_id=int(chain_data["chain_id"]),
                    rpc_url=chain_data.get("rpc_url", ""),
                    fallback=chain_data.get("fallback", ""),
                    is_preset=True
                )
                db.session.add(chain)
            
            db.session.commit()
            print("✅ Chains seeded from YAML file")
        
    except Exception as e:
        print(f"⚠️ Could not seed chains: {e}")

def get_chains():
    """Get chains from database"""
    try:
        from models.chains import Chain
        
        chains = {}
        
        # Get all chains from database
        db_chains = Chain.query.all()
        
        for chain in db_chains:
            rpc_url = (chain.rpc_url or chain.fallback or "").strip()
            
            if rpc_url:
                chains[chain.key] = {
                    "key": chain.key,
                    "chain_id": chain.chain_id,
                    "rpc_url": rpc_url,
                    "fallback": chain.fallback,
                    "is_preset": chain.is_preset,
                    "created_at": chain.created_at,
                }
            else:
                print(f"⚠️ Skipping chain {chain.key} - no RPC URL")

        return chains
        
    except Exception as e:
        print(f"❌ get_chains failed with error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return {}

def get_default_chain():
    """Get default chain from .env or first available"""
    chains = get_chains()
    if not chains:
        return None
    
    # Check .env first
    env_chain = os.getenv("ACTIVE_CHAIN", "").strip()
    if env_chain and env_chain in chains:
        return env_chain
    
    # Fall back to first available chain
    return next(iter(chains.keys()))

def is_chain_reachable(chain_key):
    """Check if a chain is reachable"""
    try:
        import core.queries as q
        # Try to get latest block number
        q.get_block_number(chain_key)
        return True
    except:
        return False