from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from models.chains import db
from config import seed_chains_from_yaml, get_chains, get_default_chain
from web3.exceptions import BlockNotFound
import core.queries as q
from utils.tools import fmt_wei, time_ago, short
from flask import redirect, url_for
from core.search import classify
from models.chains import Chain
from datetime import datetime
from core.contract import ContractClassifier

app = Flask(__name__, static_folder='static')

# Initialize database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chains.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Seed chains from YAML on startup
with app.app_context():
    db.create_all()
    seed_chains_from_yaml()


@app.get("/")
def home():
    current_chain = request.args.get("chain") or get_default_chain()
    
    try:
        classifier = ContractClassifier(current_chain)
        n = int(request.args.get("n", 5))
        start = request.args.get("start")
        
        # Get blocks with full transaction data for classification
        blocks = (q.get_all_blocks(current_chain, n, classify=True, median_block=int(start)) if start
                  else q.get_all_blocks(current_chain, n, classify=True, median_block=None))
        
        # Simple conversion: just convert HexBytes to strings for display
        if blocks:
            for block in blocks:
                if isinstance(block.get('transactions'), list):
                    for tx in block['transactions']:
                        if hasattr(tx, '_asdict'):
                            tx_dict = dict(tx._asdict())
                            # Convert HexBytes to strings
                            for key, value in tx_dict.items():
                                if hasattr(value, 'hex'):
                                    tx_dict[key] = value.hex()
                            # Replace the original transaction
                            block['transactions'][block['transactions'].index(tx)] = tx_dict
                
                # Add basic classification
                try:
                    block['classification'] = classifier.classify_block(block)
                except:
                    block['classification'] = {'block_type': 'Standard Block', 'primary_activity': 'Unknown'}
        
        error = None

    except Exception as e:
        blocks = []
        error = f"Chain '{current_chain}' is not reachable. Please switch to a working chain."
        n = 10
        start = None
        classifier = None
    
    return render_template("home.html", blocks=blocks, n=n, current_chain=current_chain, CHAINS=get_chains(), error=error, classifier=classifier)


@app.get("/api/blocks")
def blocks_api():
    chain = request.args.get("chain") or get_default_chain()
    n     = int(request.args.get("n", 10))
    start = request.args.get("start")
    data  = (q.blocks_from(int(start), n, chain) if start
             else q.latest_blocks(n, chain))
    return jsonify(data)    

@app.get("/block/<ref>")
def block_page(ref):
    current_chain = request.args.get("chain") or get_default_chain()
    
    try:
        data = q.get_block(ref, current_chain)  # your helper handles number or hash
        
        # Simple classification - convert data first, then classify
        if data and 'transactions' in data:
            try:
                # Convert AttributeDict to regular dict first
                if hasattr(data, '_asdict'):
                    data = dict(data._asdict())
                elif hasattr(data, '__dict__'):
                    data = dict(data.__dict__)
                
                # Now classify everything
                classifier = ContractClassifier(current_chain)
                data['classification'] = classifier.classify_block(data)
                
                # Add transaction classifications
                if isinstance(data['transactions'], list):
                    for i, tx in enumerate(data['transactions']):
                        if hasattr(tx, '_asdict'):
                            tx_dict = dict(tx._asdict())
                            # Convert HexBytes to strings
                            for key, value in tx_dict.items():
                                if hasattr(value, 'hex'):
                                    tx_dict[key] = value.hex()
                            data['transactions'][i] = tx_dict
                            tx = tx_dict
                        
                        # Add classification
                        try:
                            tx_hash = tx['hash'].hex() if hasattr(tx['hash'], 'hex') else str(tx['hash'])
                            tx['classification'] = classifier.get_transaction_classification_details(tx_hash)
                        except:
                            tx['classification'] = {'type': 'Unknown', 'category': 'Unknown', 'priority': 'Low'}
            except:
                pass

        return render_template(
            "block.html",
            block=data,
            current_chain=current_chain,
            CHAINS=get_chains(),
        )
    
    except BlockNotFound:
        error = f"Block {ref} not found on {current_chain}."
        data = {"number": None, "hash": None, "timestamp": None,
                "transactions": [], "gasUsed": None, "gasLimit": None}
    except ConnectionError as e:
        error = f"Cannot connect to {current_chain} RPC: {e}"
        data = {"number": None, "hash": None, "timestamp": None,
                "transactions": [], "gasUsed": None, "gasLimit": None}
    except Exception as e:
        error = f"Unexpected error: {e}"
        data = {"number": None, "hash": None, "timestamp": None,
                "transactions": [], "gasUsed": None, "gasLimit": None}
                
    return render_template(
        "block.html",
        block=data,
        current_chain=current_chain,
        error=error,
        CHAINS=get_chains(),
    )

def block_api(ref):
    current_chain = request.args.get("chain") or get_default_chain()
    try:
        return jsonify(q.get_block(ref, current_chain))
    except BlockNotFound:
        return jsonify({"error": f"Block {ref} not found on {current_chain}"}), 404
    except ConnectionError as e:
        return jsonify({"error": f"Cannot connect to {current_chain} RPC: {str(e)}"}), 502
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@app.get("/tx/<txhash>")
def tx_page(txhash):
    current_chain = request.args.get("chain") or get_default_chain()
    h = txhash
    if isinstance(h, str) and not h.startswith("0x") and len(h) == 64:
        h = "0x" + h  # accept hashes without 0x
    txhash = h
    try:
        print(f"tx_page: txhash='{txhash}', current_chain='{current_chain}'")
        data = q.get_tx(txhash, current_chain)
        error = None
    except TransactionNotFound:
        error = f"Transaction {txhash} not found on {current_chain}."
        data = None
    return render_template(
        "tx.html",
        data=data,
        current_chain=current_chain,
        error=error,
        CHAINS=get_chains(),
    )
@app.get("/api/tx/<txhash>")
def tx_api(txhash):
    current_chain = request.args.get("chain") or get_default_chain()
    try:
        return jsonify(q.get_tx(txhash, current_chain))
    except TransactionNotFound:
        return jsonify({"error": f"Transaction {txhash} not found on {current_chain}"}), 404

@app.get("/address/<addr>")
def address_page(addr):
    chain = request.args.get("chain") or get_default_chain()
    window = int(request.args.get("window", 1000))
    max_logs = int(request.args.get("max_logs", 2000))
    token = request.args.get("token")
    base_url = request.url_root.rstrip('/')

    transfers = q.transfers_per_wallet(addr, chain, window, max_logs, token)
    balance_wei = q.native_balance(addr, chain)
    return render_template(
        "address.html",
        addr=addr,
        transfers=transfers,
        balance_wei=balance_wei,
        current_chain=chain,
        token=token,
        window=window,
        max_logs=max_logs,
        CHAINS=get_chains(),
        base_url=base_url,
    )


@app.get("/api/address/<addr>")
def address_api(addr):
    chain = request.args.get("chain") or get_default_chain()
    window   = int(request.args.get("window", 2000))
    max_logs = int(request.args.get("max_logs", 200))
    token    = request.args.get("token")
    base_url = request.url_root.rstrip('/')
    return jsonify({
        "chain": chain,
        "address": addr,
        "balance_wei": q.native_balance(addr, chain),
        "transfers": q.transfers_per_wallet(addr, chain, window=window, max_logs=max_logs,
                                            tokens=[token] if token else None),
        "base_url": base_url,
    })

@app.get("/token/<token>")
def token_page(token):
    chain    = request.args.get("chain") or get_default_chain()
    window   = int(request.args.get("window", 2000))
    max_logs = int(request.args.get("max_logs", 200))
    holder   = (request.args.get("holder") or "").strip() or None  # "" -> None
    error = None

    try:
        rows = q.transfers_per_wallet(holder, chain, window, max_logs, tokens=token)
    except ValueError as e:          # e.g., bad address length → _topic_for_addr guard
        error, rows = str(e), []
    except Web3RPCError as e:        # RPC-side issues
        error, rows = str(e), []
    except Exception as e:
        error, rows = f"Unexpected error: {e}", []
        
    return render_template("token.html",
                           token=token, rows=rows, holder=holder,
                           window=window, max_logs=max_logs,
                           current_chain=chain,
                           CHAINS=get_chains())

@app.get("/api/token/<token>")
def token_api(token):
    chain    = request.args.get("chain") or get_default_chain()
    window   = int(request.args.get("window", 2000))
    max_logs = int(request.args.get("max_logs", 200))
    holder   = request.args.get("holder")
    rows = q.transfers_per_wallet(holder, chain, window, max_logs, tokens=token)
    return jsonify({"chain": chain, "token": token, "holder": holder,
                    "window": window, "max_logs": max_logs, "transfers": rows})


@app.get("/search")
def search():
    current_chain = request.args.get("chain") or get_default_chain()
    kind, val = classify(request.args.get("q",""))
    if kind == "block":
        return redirect(url_for("block_page", ref=val, chain=current_chain))
    if kind == "tx":
        return redirect(url_for("tx_page", txhash=val, chain=current_chain))
    if kind == "address":
        # if you don’t want a dedicated address page yet, send to token view with holder param
        return redirect(url_for("token_page", token=val, chain=current_chain))
        # or later: url_for("address_page", addr=val, chain=chain)

    # fallback: go home on the same chain
    return redirect(url_for("home", chain=current_chain))



@app.get("/searchfor")
def searchfor():
    chain = request.args.get("chain") or get_default_chain()

    return render_template("search.html",
                           current_chain=chain,
                           address=request.args.get("address", ""),
                           window=request.args.get("window", 1000),
                           max_logs=request.args.get("max_logs", 200),
                           token=request.args.get("token", ""),
                           CHAINS=get_chains(),
                           )



@app.get('/manage-chains')
def manage_chains():
    chains = get_chains()
    default_chain_key = get_default_chain()
    default_chain_obj = chains.get(default_chain_key)
    
    # Current chain should be user's selection from URL
    current_chain = request.args.get("chain") or default_chain_key
    current_chain_obj = chains.get(current_chain)

    return render_template('manage_chains.html',
                       default_chain_key=default_chain_key,  # Pass the KEY, not object
                       current_chain_key=current_chain,  # Pass the KEY, not object
                       current_chain_obj=current_chain_obj,      # Pass the object for display
                       default_chain=default_chain_obj,     # Pass the object for display
                       CHAINS=get_chains(),
                       )

@app.post('/add-chain')
def add_chain():
    key = request.form.get('key')
    chain_id = request.form.get('chain_id')
    rpc_url = request.form.get('rpc_url')
    fallback = request.form.get('fallback')
    created_at = datetime.utcnow()
    chain = Chain(key=key, chain_id=chain_id, rpc_url=rpc_url, fallback=fallback, is_preset=True, created_at=created_at)
    db.session.add(chain)
    db.session.commit()
    return redirect(url_for('manage_chains'))

@app.post('/remove-chain')
def remove_chain():
    key = request.form.get('key')
    chain = Chain.query.filter_by(key=key).first()
    db.session.delete(chain)
    db.session.commit()
    return redirect(url_for('manage_chains'))

@app.get("/all_blocks")
def all_blocks():

    current_chain = request.args.get("chain") or get_default_chain()
    address = request.args.get("address")
    token = request.args.get("token")
    window = int(request.args.get("window", 1000))
    max_logs = int(request.args.get("max_logs", 2000))
    n = int(request.args.get("n", 20))
    median_block = request.args.get("median_block")
    if median_block:
        median_block = int(median_block)
    # Check if chain is reachable
    try:
        blocks = (q.get_all_blocks(current_chain, n, classify=True, median_block=median_block) if median_block
                  else q.get_all_blocks(current_chain, n, classify=True, median_block=None))
        error = None

    except Exception as e:
        # Chain is unreachable
        blocks = []  # Add this line!
        error = f"Chain '{current_chain}' is not reachable. Please switch to a working chain."




    
    return render_template("all_blocks.html",
                    blocks=blocks,  # Now blocks is always defined
                    current_chain=current_chain, 
                    CHAINS=get_chains(),
                    error=error,
                    address=address,
                    token=token,
                    window=window,
                    max_logs=max_logs,
                    median_block=median_block,
                    n=n)




@app.get("/erc3643")
def erc3643():
    return render_template("erc3643.html",
                           default_chain=get_default_chain(),
                           CHAINS=get_chains(),
                           )


if __name__ == "__main__":
    app.run(debug=True, port=5001)