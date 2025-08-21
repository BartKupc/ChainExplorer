import config
from core.chain_manager import ChainManager
import os
import core.queries as q
from app import app  # Import your Flask app
from models.chains import Chain, db
from config import get_chains
from core.contract import ContractClassifier
from core.contract import EVENT_SIGNATURES
from collections import Counter

def test_chain_manager():
    mgr = ChainManager(config.CHAINS, config.ACTIVE_CHAIN_KEY)

    # --- hardhat ---
    w3_h = mgr.get_web3("hardhat")
    assert w3_h.eth.chain_id == 31337
    assert q.get_chain_id("hardhat") == 31337
    assert isinstance(q.get_chain_name("hardhat"), str)
    assert mgr.meta("hardhat")["chain_id"] == 31337

    # cache works (same object returned)
    assert mgr.get_web3("hardhat") is w3_h
    print(q.get_block_number("hardhat"))
    # --- reset & cronos ---
    mgr.reset()  # clears cache
    w3_c = mgr.get_web3("cronos")
    assert w3_c.eth.chain_id == 25
    assert q.get_chain_id("cronos") == 25
    assert q.get_chain_name("cronos") in ("Cronos", "CRONOS")  # name check
    assert mgr.meta("cronos")["chain_id"] == 25
    print(q.get_block_number("cronos"))
    # cache works for cronos too
    assert mgr.get_web3("cronos") is w3_c

def test_queries():
    mgr = ChainManager(config.CHAINS, config.ACTIVE_CHAIN_KEY)
    CRONOS_WCRO = os.getenv("CRONOS_WCRO", "").strip()
    CRONOS_USDC = os.getenv("CRONOS_USDC", "").strip()
    print(q.transfers_per_wallet("0x0000000000000000000000000000000000000000", "hardhat", 100)[:2])
    counter = 0
    print(q.transfers_per_wallet("0x0000000000000000000000000000000000000000", "hardhat", 100))

    for t in q.transfers_per_wallet("0x0000000000000000000000000000000000000000", "cronos", 1000,20000):
        counter += 1
    print(counter)
    print("--------------------------------")
    counter1 = 0
    for t in q.transfers_per_array(["0x0000000000000000000000000000000000000000"], "cronos", 1000,20000):
        counter1 += 1
    print(counter1)
    print("--------------------------------")
    counter2 = 0
    for t in q.transfers_per_array(["0x0000000000000000000000000000000000000000"], "cronos", 10000,20000,tokens=[CRONOS_USDC]):
        counter2 += 1
    print(counter2)
    print("--------------------------------")
    counter3 = 0
    for t in q.transfers_per_array(None, "cronos", 1000,20000,CRONOS_USDC):
        counter3 += 1
    print(counter3)

def test_database():
    with app.app_context():
        # Now you can use database queries
        chains = Chain.query.all()
        print(f"Found {len(chains)} chains in database:")
        for chain in chains:
            print(f"  - {chain.key}: (ID: {chain.chain_id}) {chain.rpc_url} {chain.fallback} {chain.is_preset}")

def test_get_chains():
    with app.app_context():
        chains = Chain.query.all()
        print(f"Found {len(chains)} chains in database:")
        for chain in chains:
            print(f"  - {chain.key}: (ID: {chain.chain_id}) {chain.rpc_url} {chain.fallback} {chain.is_preset}")
        print(get_chains())

def test_get_block():
    with app.app_context():
        # First check what blocks are available
        print("🔍 Checking Cronos chain...")
        
        # Get latest block number
        latest_block = q.get_block_number("Hardhat")
        print(f" Latest block on Cronos: {latest_block}")
        
        # Try to get block 1 (should exist)
        try:
            block_1 = q.get_block("27", "Hardhat",True)
            print(f" Block 1 exists: {block_1['number']}")
        except Exception as e:
            print(f" Block 1 error: {e}")
        
        # # Try to get block 222
        # try:
        #     block_222 = q.get_block("222", "Hardhat")
        #     print(f" Block 222 exists: {block_222['number']}")
        # except Exception as e:
        #     print(f" Block 222 error: {e}")

def test_direct_rpc():
    """Test RPC directly without our chain manager"""
    print("🔍 Testing RPC directly...")
    
    from web3 import Web3
    
    # Test the exact RPC URL from your database
    rpc_url = "https://evm.cronos.org/"
    print(f" Testing RPC: {rpc_url}")
    
    try:
        # Create Web3 connection directly
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        
        # Check connection
        if w3.is_connected():
            print(f"✅ Connected to RPC")
            print(f" Chain ID: {w3.eth.chain_id}")
            print(f" Latest block: {w3.eth.block_number}")
            
            # Test getting block 1 directly
            try:
                block_1 = w3.eth.get_block(1)
                print(f"✅ Block 1 exists: {block_1['number']}")
                print(f" Block 1 hash: {block_1['hash'].hex()}")
            except Exception as e:
                print(f"❌ Block 1 failed: {type(e).__name__}: {e}")
            
            # Test getting block 222 directly
            try:
                block_222 = w3.eth.get_block(222)
                print(f"✅ Block 222 exists: {block_222['number']}")
                print(f" Block 222 hash: {block_222['hash'].hex()}")
            except Exception as e:
                print(f"❌ Block 222 failed: {type(e).__name__}: {e}")
            
            # Test getting a recent block
            latest = w3.eth.block_number
            recent = latest - 100
            try:
                recent_block = w3.eth.get_block(recent)
                print(f"✅ Recent block {recent} exists: {recent_block['number']}")
            except Exception as e:
                print(f"❌ Recent block {recent} failed: {type(e).__name__}: {e}")
                
        else:
            print("❌ Failed to connect to RPC")
            
    except Exception as e:
        print(f"❌ RPC test failed: {type(e).__name__}: {e}")


def test_find_blocks_by_address_or_token():
    with app.app_context():
        print(q.find_blocks_by_address_or_token("0x0000000000000000000000000000000000000000", "Cronos", 100, 20000))

def test_get_all_blocks_with_classifier():
    with app.app_context():
        classifier = ContractClassifier("Hardhat")
        
        blocks = q.get_all_blocks("Cronos", 10, classify=True)

        all_results = {}
        for block in blocks:
            print(f"Block {block['number']} has {len(block['transactions'])} transactions")
            block_results = {}
            for tx in block["transactions"]:
                tx_results = {}

                # Check 'from' address
                if tx.get('from'):
                    from_result = classifier.classify_address(tx["from"])
                    if from_result == "EOA":
                        tx_results[tx["from"]] = "EOA", "from"
                elif tx.get('from') == "Contract (0 bytes)":
                    tx_results[tx["from"]] = "Contract (0 bytes)", "from"
                else:
                    tx_results[tx["from"]] = "Unknown", "from"

                if tx.get('to'):
                    to_result = classifier.classify_address(tx["to"])
                    if to_result == "EOA":
                        tx_results[tx["to"]] = "EOA", "to"
                elif tx.get('to') == "Contract (0 bytes)":
                    tx_results[tx["to"]] = "Contract (0 bytes)", "to"
                else:
                    tx_results[tx["to"]] = "Unknown", "to"

                block_results[tx["hash"].hex()] = tx_results
            all_results[block["number"]] = block_results

        eoa_count = sum(
            1 for block_results in all_results.values()
            for tx_results in block_results.values()
            for (classification, direction) in tx_results.values()
            if classification == "EOA"
        )
        print(eoa_count)
        
        # print(x)


def test_classifier_full():
    """Test full classification on last 20 blocks"""
    with app.app_context():
        classifier = ContractClassifier("Hardhat")
        blocks = q.get_all_blocks("Hardhat", 50, classify=True)
        
        for block in blocks:
            print(f"Block {block['number']}: {len(block['transactions'])} transactions")
            
            for tx in block["transactions"]:
                # Full classify each transaction
                result = classifier.full_classify(tx_hash=tx["hash"].hex())
                print(f"  TX: {result}")
                
                # Classify addresses with debug info
                if tx.get('from'):
                    from_type = classifier.classify_address(tx["from"])
                    print(f"    FROM: {from_type['classification']} - {from_type['address']}")
                    if 'details' in from_type:
                        print(f"      FROM Details: {from_type['details']}")
                    
                    # Debug: Check if it's a contract and get logs
                    if from_type['classification'] != "EOA":
                        logs = classifier._get_recent_logs(tx["from"], blocks_window=1000)
                        print(f"      FROM logs found: {len(logs)}")
                        if logs:
                            for log in logs: 
                                if log.get('topics') and len(log['topics']) > 0:
                                    topic0 = log['topics'][0].hex()
                                    event_name = classifier._fingerprint_from_logs([log])
                                    print(f"      FROM event: {topic0} -> {event_name}")
                
                if tx.get('to'):
                    to_type = classifier.classify_address(tx["to"])
                    print(f"    TO: {to_type['classification']} - {to_type['address']}")
                    if 'details' in to_type:
                        print(f"      TO Details: {to_type['details']}")
                    
                    # Debug: Check if it's a contract and get logs
                    if to_type['classification'] != "EOA":
                        logs = classifier._get_recent_logs(tx["to"], blocks_window=1000)
                        print(f"      TO logs found: {len(logs)}")
                        if logs:
                            for log in logs:  # Show all logs
                                if log.get('topics') and len(log['topics']) > 0:
                                    topic0 = log['topics'][0].hex()
                                    event_name = classifier._fingerprint_from_logs([log])
                                    print(f"      TO event: {topic0} -> {event_name}")


def test_classifier_clean():
    """Clean test output for troubleshooting - just the essentials"""
    with app.app_context():
        classifier = ContractClassifier("Hardhat")
        blocks = q.get_all_blocks("Hardhat", 50, classify=True)
        
        print("=== CLEAN CLASSIFICATION TEST ===")
        for block in blocks:
            print(f"\nBlock {block['number']}: {len(block['transactions'])} transactions")
            
            for tx in block["transactions"]:
                print(f"  TX: {tx['hash'].hex()}")
                
                # Classify addresses
                if tx.get('from'):
                    from_type = classifier.classify_address(tx["from"])
                    print(f"    FROM: {from_type['classification']} - {from_type['address']}")
                
                if tx.get('to'):
                    to_type = classifier.classify_address(tx["to"])
                    print(f"    TO: {to_type['classification']} - {to_type['address']}")
                    
                    # Show events if it's a contract
                    if to_type['classification'] != "EOA":
                        logs = classifier._get_recent_logs(tx["to"], blocks_window=1000)
                        if logs:
                            print(f"    Events ({len(logs)}):")
                            for log in logs:
                                if log.get('topics') and len(log['topics']) > 0:
                                    topic0 = log['topics'][0].hex()
                                    event_name = EVENT_SIGNATURES.get(topic0, "Unknown")
                                    print(f"      {topic0} -> {event_name}")


def test_classifier_simple():
    """Super simple test - just block, from, to, and classification"""
    with app.app_context():
        classifier = ContractClassifier("Hardhat")
        blocks = q.get_all_blocks("Hardhat", 50, classify=True)
        
        print("=== SIMPLE CLASSIFICATION TEST ===")
        for block in blocks:
            print(f"\nBlock {block['number']}:")
            
            for tx in block["transactions"]:
                # Classify addresses
                if tx.get('from'):
                    from_type = classifier.classify_address(tx["from"])
                    from_class = from_type['classification']
                    from_addr = from_type['address']
                else:
                    from_class = "Contract Creation"
                    from_addr = "N/A"
                
                if tx.get('to'):
                    to_type = classifier.classify_address(tx["to"])
                    to_class = to_type['classification']
                    to_addr = to_type['address']
                else:
                    to_class = "Contract Creation"
                    to_addr = "N/A"
                
                print(f"  {from_class} -> {to_class}")
                print(f"  {from_addr} -> {to_addr}")


def test_classifier_full_contract_creation():
    """Focus on contract creation transactions - show block, FROM, and hash"""
    with app.app_context():
        classifier = ContractClassifier("Hardhat")
        blocks = q.get_all_blocks("Hardhat", 50, classify=True)
        
        print("=== CONTRACT CREATION ANALYSIS ===")
        contract_creations = []
        
        for block in blocks:
            for tx in block["transactions"]:
                # Check if this is a contract creation (to is None)
                if tx.get('to') is None:
                    contract_creations.append({
                        'block': block['number'],
                        'from': tx.get('from'),
                        'hash': tx['hash'].hex(),
                        'gas_used': tx.get('gas_used'),
                        'input_data_length': len(tx.get('input', b'')) if tx.get('input') else 0
                    })
        
        print(f"\n📦 Found {len(contract_creations)} contract creation transactions:")
        
        for creation in contract_creations:
            print(f"\n🔨 Block {creation['block']}:")
            print(f"   FROM: {creation['from']}")
            print(f"   HASH: {creation['hash']}")
            print(f"   Gas Used: {creation['gas_used']}")
            print(f"   Input Data: {creation['input_data_length']} bytes")
            
            # Try to get more details about what was created
            try:
                # Get transaction receipt to find contract address
                tx_receipt = classifier.w3.eth.get_transaction_receipt(creation['hash'])
                if tx_receipt and tx_receipt.contractAddress:
                    contract_address = tx_receipt.contractAddress
                    print(f"   Contract Created: {contract_address}")
                    
                    # Try to classify the created contract
                    contract_type = classifier.classify_address(contract_address)
                    print(f"   Contract Type: {contract_type['classification']}")
                    
                    # Get some logs to see what events it emits
                    logs = classifier._get_recent_logs(contract_address, blocks_window=100)
                    if logs:
                        print(f"   Recent Events: {len(logs)} found")
                        for log in logs[:3]:  # Show first 3 events
                            if log.get('topics') and len(log['topics']) > 0:
                                topic0 = log['topics'][0].hex()
                                event_name = EVENT_SIGNATURES.get(topic0, "Unknown")
                                print(f"     {topic0} -> {event_name}")
                    
            except Exception as e:
                print(f"   Error getting contract details: {e}")
        
        print(f"\n📊 Summary: {len(contract_creations)} contracts created across {len(set(c['block'] for c in contract_creations))} blocks")


def test_full_classify_demo():
    """Test and demonstrate the full_classify method with readable output"""
    with app.app_context():
        classifier = ContractClassifier("Hardhat")
        blocks = q.get_all_blocks("Hardhat", 50, classify=True)  # Just 20 blocks for demo
        
        print("=== FULL_CLASSIFY DEMONSTRATION ===")
        print("This test shows how full_classify works for both addresses and transactions")
        print("=" * 60)
        
        # Test address classification first
        print("\n🔍 TESTING ADDRESS CLASSIFICATION:")
        print("=" * 40)
        
        # Get a few contract addresses from the first few transactions
        sample_addresses = []
        for block in blocks[:3]:  # First 3 blocks
            for tx in block["transactions"]:
                if tx.get('to') and tx['to'] not in sample_addresses:
                    sample_addresses.append(tx['to'])
                if len(sample_addresses) >= 3:
                    break
            if len(sample_addresses) >= 3:
                break
        
        for i, addr in enumerate(sample_addresses):
            print(f"\n  📍 Address {i+1}: {addr[:16]}...")
            addr_result = classifier.full_classify(address=addr)
            if 'address_classification' in addr_result:
                addr_class = addr_result['address_classification']
                print(f"    🎯 Classification: {addr_class['classification']}")
                if 'details' in addr_class:
                    print(f"    📋 Details: {addr_class['details']}")
            print(f"    " + "─" * 30)
        
        print("\n🔍 TESTING TRANSACTION CLASSIFICATION:")
        print("=" * 40)
        
        contract_creations_found = 0
        regular_transactions = 0
        total_blocks = len(blocks)
        total_txs_in_blocks = sum(len(block['transactions']) for block in blocks)
        
        print(f"\n📊 BLOCK ANALYSIS:")
        print(f"   📦 Total Blocks: {total_blocks}")
        print(f"   🔄 Total Transactions in Blocks: {total_txs_in_blocks}")
        print(f"   🎯 Processing all blocks and transactions...")
        print("=" * 60)
        
        for block in blocks:
            print(f"\n🔍 Block {block['number']} ({len(block['transactions'])} txs)")
            
            for tx in block["transactions"]:
                tx_hash = tx['hash'].hex()
                
                # Test full_classify on this transaction
                print(f"\n  📋 Transaction: {tx_hash}")
                
                # Use full_classify to get complete classification
                full_result = classifier.full_classify(tx_hash=tx_hash)
                
                if 'transaction_classification' in full_result:
                    tx_class = full_result['transaction_classification']
                    tx_type = tx_class['type']
                    details = tx_class['details']
                    
                    print(f"    🎯 Type: {tx_type}")
                    print(f"    👤 From: {details.get('from', 'N/A')}")
                    print(f"    🎯 To: {details.get('to', 'Contract Creation')}")
                    
                    # Enhanced classification display
                    if details.get('to') and details['to'] != 'Contract Creation':
                        # This is a contract interaction - classify the target
                        try:
                            target_class = classifier.classify_address(details['to'])
                            print(f"    🏗️ Target Contract: {target_class['classification']}")
                            if 'details' in target_class:
                                print(f"    📋 Target Details: {target_class['details']}")
                        except Exception as e:
                            print(f"    ❌ Error classifying target: {e}")
                    
                    # Show logs if available
                    if details.get('logs'):
                        event_count = len(details['logs'])
                        print(f"    📝 Events: {event_count} found")
                        if event_count > 0:
                            # Show first few events briefly
                            for i, log in enumerate(details['logs'][:3]):
                                if 'event_name' in log:
                                    print(f"      {i+1}. {log['event_name']}")
                                else:
                                    topic0 = log['topics'][0] if log.get('topics') else 'Unknown'
                                    print(f"      {i+1}. {topic0[:16]}...")
                    
                    # Enhanced contract creation debugging
                    if "Contract Creation" in tx_type:
                        contract_creations_found += 1
                        print(f"    🏭 ✅ Contract Creation Detected!")
                    else:
                        regular_transactions += 1
                        
                    print(f"    " + "─" * 40)
        
        total_transactions = contract_creations_found + regular_transactions
        print(f"\n" + "=" * 60)
        print("📊 FULL_CLASSIFY SUMMARY:")
        print(f"   🏭 Contract Creations: {contract_creations_found}")
        print(f"   🔄 Regular Transactions: {regular_transactions}")
        print(f"   📦 Total Transactions Analyzed: {total_transactions}")
        print(f"   🎯 Classification Success: {total_transactions} transactions processed")
        print(f"   📊 Expected Transactions: {total_txs_in_blocks}")
        print(f"   ❓ Missing Transactions: {total_txs_in_blocks - total_transactions}")
        print("=" * 60)
        print("✅ full_classify demonstration complete!")
        print("   This shows how the enhanced classification works for:")
        print("   • Contract creation identification")
        print("   • Event decoding")
        print("   • Complete transaction analysis")
        print("=" * 60)


def test_log_scanning():
    with app.app_context():
        """Quick test to see how many logs are in recent blocks"""
        print("🔍 QUICK LOG SCANNING TEST")
        print("=" * 50)
        
        # Test on Hardhat (should have T-REX contracts)
        classifier = ContractClassifier('Hardhat')
        
        # Focus on block 27 where we know there should be 4 events
        block_num = 27
        print(f"\n📦 Block {block_num}:")
        
        try:
            # Get block using your working method
            block = q.get_block(str(block_num), "Hardhat", True)
            if not block:
                print("   ❌ Block not found")
                return
                
            print(f"   📊 Transactions: {len(block['transactions'])}")
            
            # Check each transaction for logs using receipt
            for i, tx in enumerate(block['transactions']):
                try:
                    tx_hash = tx['hash'].hex()
                    print(f"\n   📝 TX {i}: {tx_hash[:16]}...")
                    
                    # Method 1: Transaction receipt (current method)
                    receipt = classifier.w3.eth.get_transaction_receipt(tx_hash)
                    if receipt and receipt.logs:
                        print(f"      📋 Receipt logs: {len(receipt.logs)}")
                        for j, log in enumerate(receipt.logs):
                            if log.topics:
                                topic0 = log.topics[0].hex()
                                event_name = EVENT_SIGNATURES.get(topic0, "Unknown")
                                print(f"         Log {j}: {topic0[:16]}... → {event_name}")
                    else:
                        print(f"      📋 Receipt logs: 0")
                    
                    # Method 2: Direct eth_getLogs for this block
                    print(f"      🔍 Direct eth_getLogs for block {block_num}:")
                    try:
                        # Try different parameter formats
                        direct_logs = classifier.w3.eth.get_logs({
                            'fromBlock': block_num,
                            'toBlock': block_num
                        })
                        
                        if direct_logs:
                            print(f"         Found {len(direct_logs)} total logs in block")
                            
                            # Filter logs for this specific transaction
                            tx_logs = [log for log in direct_logs if log.transactionHash.hex() == tx_hash]
                            print(f"         TX-specific logs: {len(tx_logs)}")
                            
                            for j, log in enumerate(tx_logs):
                                if log.topics:
                                    topic0 = log.topics[0].hex()
                                    event_name = EVENT_SIGNATURES.get(topic0, "Unknown")
                                    print(f"            Log {j}: {topic0[:16]}... → {event_name}")
                        else:
                            print(f"         eth_getLogs returned None or empty")
                            
                    except Exception as e:
                        print(f"         ❌ eth_getLogs error: {e}")
                        
                        # Try alternative method - get logs by transaction hash
                        print(f"      🔍 Alternative: Try to get logs by transaction hash")
                        try:
                            # Some RPC nodes support getting logs for specific transaction
                            tx_logs = classifier.w3.eth.get_logs({
                                'fromBlock': block_num,
                                'toBlock': block_num,
                                'topics': [],
                                'transactionHash': tx_hash
                            })
                            if tx_logs:
                                print(f"         Found {len(tx_logs)} logs for this transaction")
                                for j, log in enumerate(tx_logs):
                                    if log.topics:
                                        topic0 = log.topics[0].hex()
                                        event_name = EVENT_SIGNATURES.get(topic0, "Unknown")
                                        print(f"            Log {j}: {topic0[:16]}... → {event_name}")
                            else:
                                print(f"         No logs found for transaction")
                        except Exception as e2:
                            print(f"         ❌ Alternative method also failed: {e2}")
                        
                except Exception as e:
                    print(f"   ❌ TX {i} error: {e}")
                    
        except Exception as e:
            print(f"   ❌ Block error: {e}")
        
        print("\n" + "=" * 50)
def test_log_scanning_2():
    with app.app_context():
        from core.chain_manager import ChainManager
        mgr = ChainManager()
        w3 = mgr.get_web3("Hardhat")
        """Quick test using q.get_block() + transaction receipts"""
        print("�� QUICK LOG SCANNING TEST")
        print("=" * 50)
        
        # Get block 27 using your working method
        block = q.get_block("27", "Hardhat", True)
        print(f"📦 Block {block['number']}: {len(block['transactions'])} transactions")
        
        # Check each transaction for logs
        for i, tx in enumerate(block['transactions']):
            try:
                tx_hash = tx['hash'].hex()
                print(f"\n TX {i}: {tx_hash}")
                
                # Get receipt for logs
                receipt = w3.eth.get_transaction_receipt(tx_hash)
                if receipt and receipt.logs:
                    print(f"    Found {len(receipt.logs)} logs")
                    for j, log in enumerate(receipt.logs):
                        if log.topics:
                            topic0 = log.topics[0].hex()
                            event_name = EVENT_SIGNATURES.get(topic0, "Unknown")
                            print(f"      Log {j}: {topic0} → {event_name}")
                else:
                    print(f"   📊 0 logs found")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    # test_config()
    # test_chain_manager()
    # test_queries()
    # # print(q.get_block_number("cronos"))
    # with app.app_context():
    #     print(q.get_block("27","Hardhat",True))
    # # print(q.latest_blocks(10, "cronos"))
    # test_database()
    # print(q.get_block("222", "Cronos"))
    # print(get_chains())
    # test_get_chains()
    # test_get_block()
    # test_direct_rpc()
    # test_find_blocks_by_address_or_token()
    # test_get_all_blocks_with_classifier()
    # test_classifier_full()  # Commented out - too verbose
    # test_classifier_clean()  # Clean output for troubleshooting
    # test_classifier_simple()
    # test_classifier_full_contract_creation()  # Focus on contract creations
    test_full_classify_demo()  # Demonstrate full_classify method
    # test_log_scanning()  # Quick log scanning test
    # test_log_scanning()  # Quick log scanning test