from web3 import Web3
from core.chain_manager import ChainManager
from typing import Dict, List, Optional, Any

from config import get_chains, get_default_chain

# ERC Standards
ERC20_INTERFACE = "0x36372b07"        # totalSupply()
ERC721_INTERFACE = "0x80ac58cd"       # transferFrom(address,address,uint256)
ERC1155_INTERFACE = "0xd9b67a26"      # balanceOf(address,uint256)

# T-REX specific (ERC-3643)
TREX_IDENTITY_REGISTRY = "0x8da5cb5b"  # identityRegistry()
TREX_COMPLIANCE = "0x9d63848a"         # compliance()

# Other useful interfaces
ERC165_INTERFACE = "0x01ffc9a7"        # supportsInterface(bytes4)

# Event signatures (topic0 hashes) - FROM YOUR HARDHAT DEPLOYMENT
EVENT_SIGNATURES = {
    # ERC-20/721/1155
    "ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef": "Transfer(address,address,uint256)",  # ERC-20/721
    "c3d58168c5ae7397731d063d5bbf3d657854427343f4c083240f7aacaa2d0f62": "TransferSingle(address,address,address,uint256,uint256)",  # ERC-1155
    "4a39dc06d4c0dbc64b70af90fd698a233a518aa5d07e595d983b8c0526c8f7fb": "TransferBatch(address,address,address,uint256[],uint256[])",  # ERC-1155
    
    # T-REX (ERC-3643) Identity Registry
    "6ae73635c50d24a45af6fbd5e016ac4bed179addbc8bf24e04ff0fcc6d33af19": "IdentityRegistered(address,address)",
    "59d6590e225b81befe259af056324092801080acbb7feab310eb34678871f327": "IdentityRemoved(address,address)",
    "e98082932c8056a0f514da9104e4a66bc2cbaef102ad59d90c4b24220ebf6010": "IdentityUpdated(address,address)",
    
    # T-REX Claim Topics Registry - FROM YOUR HARDHAT
    "01c928b7f7ade2949e92366aa9454dbef3a416b731cf6ec786ba9595bbd814d6": "ClaimTopicAdded(uint256)",
    "0b1381093c776453c1bbe54fd68be1b235c65db61d099cb50d194b2991e0eec5": "ClaimTopicRemoved(uint256)",
    
    # T-REX Trusted Issuers Registry - FROM YOUR HARDHAT
    "fedc33fd34859594822c0ff6f3f4f9fc279cc6d5cae53068f706a088e4500872": "TrustedIssuerAdded(address,uint256[])",
    "2214ded40113cc3fb63fc206cafee88270b0a903dac7245d54efdde30ebb0321": "TrustedIssuerRemoved(address)",
    "ec753cfc52044f61676f18a11e500093a9f2b1cd5e4942bc476f2b0438159bcf": "ClaimTopicsUpdated(address,uint256[])",
    
    # T-REX Modular Compliance
    "7f3a888862559648ec01d97deb7b5012bff86dc91e654a1de397170db40e35b6": "ComplianceAdded(address)",
    "2de35142b19ed5a07796cf30791959c592018f70b1d2d7c460eef8ffe713692b": "TokenBound(address)",
    
    # T-REX Token (ERC-3643)
    "f68e73cec97f2d70aa641fb26e87a4383686e2efacb648f2165aeb02ac562ec5": "AgentAdded(address)",
    "ed9c8ad8d5a0a66898ea49d2956929c93ae2e8bd50281b2ed897c5d1a6737e0b": "AgentRemoved(address)",
    
    # T-REX Factory - FROM YOUR HARDHAT
    "f40fcec21964ffb566044d083b4073f29f7f7929110ea19e1b3ebe375d89055e": "Deployed(address)",
    "ae81f4fee1b2d830e39ae449967642aaa0e5a1771aa200d0a50853010992242c": "IdFactorySet(address)",
    "3b1074392ed8e8424715d0dda2197eede67080b377fc8370e26f3e882207f6b8": "ImplementationAuthoritySet(address)",
    "057adae5fa3e9caa8a0d584edff60f61558d33f073412ec2d66d558b739e0a41": "TREXSuiteDeployed(address,address,address,address,address,address,string)",
    
    # Additional T-REX Events from Your Hardhat
    "8be0079c531659141344cd1fd0a4f28419497f9722a3daafe3b4186f6b6457e0": "OwnershipTransferred(address,address)",
    "7f26b83ff96e1f2b6a682f133852f6798a09c465da95921460cefb3847402498": "RoleGranted(bytes32,address,address)",
    "45eb8ac5344d2d3f306550fe6e969ca4190526313c512afed851d052bf2ab2fd": "RoleRevoked(bytes32,address,address)",
    "2a6aba4ff896a38777fb29a590abf5d340a4ba64314bcadf68be9c3ee92b485a": "AgentAdded(address)",
    "5fb25b36f93b3d8443f7502abdc1157f581f15db724459ffb2800fce6132a008": "AgentRemoved(address)",
    "1edf3afd4ac789736e00d216cd88be164ddcef26a6eedcc30cdb0cb62f3741b1": "IdentityRegistered(address,address)",
    "f8be33baa430c4b62d2c9d79ab319d10cc41755a1fb65f85e64ca0632c29d0a4": "IdentityUpdated(address,address)",
    "7170bf15b246e880b2369cd7c67d057760d8a35149e8c64dde91efa22bcc76d0": "ClaimTopicRemoved(uint256)",
    "1b98cb79e6f73020175fe87333f1b91ad6a881519c0afe30340c2599b2b4bde0": "TrustedIssuerRemoved(address)",
    "d2be862d755bca7e0d39772b2cab3a5578da9c285f69199f4c063c2294a7f36c": "ComplianceAdded(address)",
    "480000bb1edad8ca1470381cc334b1917fbd51c6531f3a623ea8e0ec7e38a6e9": "Transfer(address,address,uint256)",
    "585a4aef50f8267a92b32412b331b20f7f8b96f2245b253b9cc50dcc621d3397": "Approval(address,address,uint256)",
                    
         # Identity Factory Events (OnchainID interactions)
     "fedc33fd34859594822c0ff6f3f4f9fc279cc6d5cae53068f706a088e4500872": "WalletLinked(address,address)",  # Wallet linked to identity
     "2214ded40113cc3fb63fc206cafee88270b0a903dac7245d54efdde30ebb0321": "WalletUnlinked(address,address)",  # Wallet unlinked from identity
     "c3d58168c5ae7397731d063d5bbf3d657854427343f4c083240f7aacaa2d0f62": "TokenLinked(address,address)",  # Token linked to identity
     "7f3a888862559648ec01d97deb7b5012bff86dc91e654a1de397170db40e35b6": "TokenFactoryAdded(address)",  # Token factory added
     "2de35142b19ed5a07796cf30791959c592018f70b1d2d7c460eef8ffe713692b": "TokenFactoryRemoved(address)",  # Token factory removed
     
     # OnchainID Function/Event (from your deployment logs)
     "8e0c709111388f5480579514d86663489ab1f206fe6da1a0c4d03ac8c318b3c6": "OnchainID Function/Event",
     
     # T-REX Contract Implementation Hashes
     "db6bc5fa5c8ded2eb390b0eaf5adf69d4af049848b4ff1010c637ad9ddc1d378": "ClaimTopicsRegistry Implementation",
     "51b017f5c0d168047ec77d696ea8c20649ec5c339e0915a069a120f0854ed211": "TrustedIssuersRegistry Implementation", 
     "0401140f25d20a90e617b80108fafb47628ee8dfba5322c37471d5b35b40b895": "IdentityRegistry Implementation",
     "040301259c7fafe9975715c02f6ce221d0854acdf651ccae709b4746dcadf260": "Identity Registry Storage Implementation",
     "b2a852655e7872efbd4b7e29581f5bf3ace9ca1e0c65e94a95cef0c04250ee4f": "Modular Compliance Implementation",
     "aef7d1cc8d456021485e015ac43ded32c6f18707ab98aeaf169066c6063f1d93": "Token Implementation",
     "fd6c383b6abb071dbf6866cd210d24d511a3ccde7feb872ffa5c2732c9b421ca": "Identity Implementation",
     "725319ebb491a615e95b6e478cd1fba70997df8268f1b87f32737c3e9482dba9": "Identity Implementation Authority",
     "bd9eb0621eddca8064cc58e44ac2800a9ac44e1eb3cd36a0797802c4e05f1f62": "Identity Factory",
     "7fec71c125d4c678b60e9bf7dafcbdffdd606d7506693de9de9091379766c9b0": "TREX Implementation Authority",
     "6dde89072a4987f86a73f68a5b8cdcaf8dafef17fdfcfd43dc352396b591d621": "TREX Factory",
     "b4e506dee6f08e1bad98e4fab32f0c9fdd2a7a1538a43fb119c559b260e1292a": "TREX Gateway",
     
     # Missing TREX Gateway Event (from your transaction)
     "861a21548a3ee34d896ccac3668a9d65030aaf2cb7367a2ed13608014016a032": "TREX Gateway Event",
}

# Transaction function signatures
TX_FUNCTION_SIGNATURES = {
    # ERC-20
    "0xa9059cbb": "transfer(address,uint256)",
    "0x23b872dd": "transferFrom(address,uint256)",
    "0x095ea7b3": "approve(address,uint256)",
    "0x40c10f19": "mint(address,uint256)",
    "0x42966c68": "burn(uint256)",
    
    # ERC-721
    "0x42842e0e": "transferFrom(address,address,uint256)",
    "0xb88d4fde": "safeTransferFrom(address,address,uint256)",
    "0x23b872dd": "transferFrom(address,address,uint256)",
    "0x40c10f19": "mint(address,uint256)",
    
    # ERC-1155
    "0xf242432a": "safeTransferFrom(address,address,uint256,uint256,bytes)",
    "0x2eb2c2d6": "safeBatchTransferFrom(address,address,uint256[],uint256[],bytes)",
    
    # T-REX specific
    "0x8da5cb5b": "identityRegistry()",
    "0x9d63848a": "compliance()",
    "0x40c10f19": "mint(address,uint256)",
    "0x42966c68": "burn(uint256)",
    
    # TREX Gateway function (from your transaction)
    "0x880f4039": "TREX Gateway Function",
    
    # Additional T-REX function signatures
    "0x9fc1d0e7": "TREX Function Call",
}


class ContractClassifier:
    def __init__(self, chain: str):
        self.chain = chain
        self.mgr = ChainManager()
        self.w3 = self.mgr.get_web3(chain)
        
    def _normalize_address(self, address: str) -> str:
        """Normalize address to checksum format"""
        try:
            return self.w3.to_checksum_address(address)
        except:
            return address.lower()
    
    def _get_recent_logs(self, address: str, blocks_window: int = 5000) -> List[Dict]:
        """Get recent logs for event fingerprinting (step 2)"""
        try:
            latest_block = self.w3.eth.block_number
            from_block = max(0, latest_block - blocks_window)
            
            logs = self.w3.eth.get_logs({
                'address': address,
                'fromBlock': from_block,
                'toBlock': latest_block
            })
            return logs
        except Exception as e:
            print(f"Error getting logs for {address}: {e}")
            return []
    
    def _fingerprint_from_logs(self, logs):
        """Step 2: Quick event fingerprinting from logs with classification hierarchy"""
        if not logs:
            return None
            
        event_counts = {}
        found_events = []
        
        for log in logs:
            topic0 = log['topics'][0].hex()
            if topic0 in EVENT_SIGNATURES:
                event_name = EVENT_SIGNATURES[topic0]
                event_counts[event_name] = event_counts.get(event_name, 0) + 1
                found_events.append(event_name)
        
        # If we found any events, classify based on contract type
        if found_events:
            # Check if any events contain T-REX related keywords
            if any('T-REX' in event or 'ERC-3643' in event or 'Identity' in event or 'Claim' in event or 'Compliance' in event for event in found_events):
                classification = "ERC-3643 (T-REX)"
            # Check for ERC-721 specific events
            elif any('TransferSingle' in event or 'TransferBatch' in event for event in found_events):
                classification = "ERC-1155"
            # Check for ERC-20/721 Transfer events
            elif any('Transfer(address,address,uint256)' in event for event in found_events):
                # Default to ERC-20 (most common)
                classification = "ERC-20"
            else:
                # If we found events but can't determine type, classify as generic contract
                classification = "Generic Contract"
        else:
            # No events found
            classification = "Generic Contract"
        
        details = {
            'events_found': found_events,
            'event_counts': event_counts
        }
        
        return {
            'classification': classification,
            'details': details
        }
    
    def _check_bytecode_fingerprint(self, code_hash: str) -> Optional[str]:
        """Check if bytecode hash matches known contracts (step 5)"""
        return KNOWN_BYTECODE_HASHES.get(code_hash)
    
    def _erc165_probe(self, address: str, logs_hint: str) -> str:
        """ERC-165 interface probing (step 3)"""
        if logs_hint == "ERC-20/721":
            # Try ERC-721 first (more specific)
            if self.supports_interface(address, ERC721_INTERFACE):
                return "ERC-721"
            elif self.supports_interface(address, ERC1155_INTERFACE):
                return "ERC-1155"
            else:
                return "ERC-20"  # Default assumption
        return logs_hint
    
    def _fallback_classify(self, address: str, code_info: Dict) -> str:
        """Fallback classification when event fingerprinting fails"""
        # Try ERC-165 for any contract
        if self.supports_interface(address, ERC721_INTERFACE):
            return "ERC-721"
        elif self.supports_interface(address, ERC1155_INTERFACE):
            return "ERC-1155"
        elif self.supports_interface(address, TREX_IDENTITY_REGISTRY):
            return "T-REX/ERC-3643"
        else:
            return f"Contract ({code_info['code_size']} bytes)"
    
    def _lightweight_confirmation(self, address: str, classification: str) -> Dict[str, Any]:
        """Lightweight metadata confirmation (step 4)"""
        metadata = {}
        
        if classification == "ERC-20":
            try:
                # Try to get basic ERC-20 metadata
                symbol = self.w3.eth.call({
                    'to': address,
                    'data': '0x95d89b41'  # symbol()
                })
                if symbol:
                    metadata['symbol'] = symbol.decode('utf-8').rstrip('\x00')
            except:
                pass
                
            try:
                decimals = self.w3.eth.call({
                    'to': address,
                    'data': '0x313ce567'  # decimals()
                })
                if decimals:
                    metadata['decimals'] = int(decimals.hex(), 16)
            except:
                pass
                
        elif classification == "T-REX/ERC-3643":
            # Optional T-REX confirmation
            try:
                ir = self.w3.eth.call({
                    'to': address,
                    'data': '0x8da5cb5b'  # identityRegistry()
                })
                if ir:
                    metadata['identity_registry'] = self.w3.to_checksum_address(ir)
            except:
                pass
                
        return metadata
    
    def _classify_contract_creation(self, tx_hash):
        """Classify what type of contract was created using implementation hashes"""
        try:
            # Get transaction receipt to find the created contract address
            tx_receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            if not tx_receipt or not tx_receipt.contractAddress:
                return "Contract Creation (Unknown)"
            
            contract_address = tx_receipt.contractAddress
            
            # Check if the TRANSACTION HASH matches any of our known implementation hashes
            # This identifies contracts by their transaction hash - works for any future contracts you add
            for hash_prefix, contract_type in EVENT_SIGNATURES.items():
                # Check if the transaction hash starts with this hash prefix
                if tx_hash.lower().startswith(hash_prefix.lower()):
                    return f"Contract Creation: {contract_type}"
            
            # If no hash match, try to classify by analyzing the created contract
            try:
                # Get the contract's bytecode
                contract_code = self.w3.eth.get_code(contract_address)
                if contract_code:
                    # Try to classify the created contract
                    contract_type = self.classify_address(contract_address)
                    return f"Contract Creation: {contract_type['classification']}"
                else:
                    return "Contract Creation (Failed)"
            except Exception as e:
                return f"Contract Creation (Error: {str(e)})"
                
        except Exception as e:
            return f"Contract Creation (Error: {str(e)})"
    
    def classify_address(self, address: str) -> Dict:
        """
        Enhanced address classifier following the decision tree
        Returns: Dict with classification and details including address
        """
        # Step 1: Is it a contract? (1 RPC call)
        code_info = self.get_code_info(address)
        if not code_info["is_contract"]:
            return {
                'classification': 'EOA',
                'address': address,
                'details': {'type': 'External Owned Account'}
            }
        
        # Step 2: Quick event fingerprint (1 RPC call)
        logs = self._get_recent_logs(address, blocks_window=5000)
        logs_classification = self._fingerprint_from_logs(logs)
        
        if logs_classification and logs_classification['classification'] != "Generic Contract":
            return {
                'classification': logs_classification['classification'],
                'address': address,
                'details': logs_classification['details']
            }
        
        # Step 3: ERC-165 probes for ambiguous cases
        if logs_classification and "ERC-20" in logs_classification['classification']:
            erc165_result = self._erc165_probe(address, logs_classification['classification'])
            return {
                'classification': erc165_result,
                'address': address,
                'details': logs_classification['details']
            }
        
        # Step 4: Fallback classification
        fallback_result = self._fallback_classify(address, code_info)
        return {
            'classification': fallback_result,
            'address': address,
            'details': {'code_size': code_info['code_size']}
        }
    
    def classify_transaction(self, tx_hash: str) -> str:
        try:
            tx = self.w3.eth.get_transaction(tx_hash)
            
            if not tx:
                return "Not Found"
            
            # Check if it's contract creation
            if tx.get('to') is None:
                return self._classify_contract_creation(tx_hash)
            
            # Check if it's a simple transfer (no input data)
            if tx.get('input') == '0x' or tx.get('input') == '':
                # Don't assume it's native token - could be any token!
                return "Token Transfer"  # Generic, not "ETH Transfer"
            
            # Always check logs for event fingerprinting first (this is more reliable)
            try:
                tx_receipt = self.w3.eth.get_transaction_receipt(tx_hash)
                if tx_receipt and tx_receipt.get('logs'):
                    # Use the same event fingerprinting logic as classify_address
                    fingerprint_result = self._fingerprint_from_logs(tx_receipt['logs'])
                    if fingerprint_result and 'classification' in fingerprint_result:
                        contract_type = fingerprint_result['classification']
                        if 'T-REX' in contract_type or 'ERC-3643' in contract_type:
                            return 'T-REX Interaction'
                        elif 'ERC-721' in contract_type:
                            return 'ERC-721 Interaction'
                        elif 'ERC-1155' in contract_type:
                            return 'ERC-1155 Interaction'
                        elif 'ERC-20' in contract_type:
                            return 'ERC-20 Interaction'
                        else:
                            return f'{contract_type} Interaction'
            except Exception as e:
                pass
            
            # If receipt logs are incomplete, try to classify by target contract
            if tx.get('to'):
                try:
                    target_address = tx['to']
                    target_result = self.classify_address(target_address)
                    if target_result and 'classification' in target_result:
                        target_type = target_result['classification']
                        if 'T-REX' in target_type or 'ERC-3643' in target_type:
                            return 'T-REX Interaction'
                        elif 'ERC-721' in target_type:
                            return 'ERC-721 Interaction'
                        elif 'ERC-1155' in target_type:
                            return 'ERC-1155 Interaction'
                        elif 'ERC-20' in target_type:
                            return 'ERC-20 Interaction'
                except Exception as e:
                    pass
            
            # Analyze input data for function calls (fallback)
            if tx.get('input') and tx['input'] != '0x':
                function_sig = tx['input'][:10]
                function_name = TX_FUNCTION_SIGNATURES.get(function_sig, "Unknown Function")
                
                if "transfer" in function_name.lower():
                    return 'Token Transfer'
                elif "mint" in function_name.lower():
                    return 'Token Mint'
                elif "burn" in function_name.lower():
                    return 'Token Burn'
                elif "approve" in function_name.lower():
                    return 'Token Approval'
                else:
                    return 'Contract Interaction'
            
            return "Contract Interaction"
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def full_classify(self, address: str = None, tx_hash: str = None) -> Dict[str, Any]:
        """
        Comprehensive classification method that can handle both addresses and transactions
        Returns detailed information including addresses for manual decoding
        """
        result = {}
        
        if address:
            result['address_classification'] = self.classify_address(address)
        
        if tx_hash:
            tx_classification = self.classify_transaction(tx_hash)
            tx_details = self._get_transaction_details(tx_hash)
            result['transaction_classification'] = {
                'type': tx_classification,
                'hash': tx_hash,
                'details': tx_details
            }
        
        return result
    
    def _get_transaction_details(self, tx_hash: str) -> Dict:
        """Get detailed transaction information including addresses"""
        try:
            tx = self.w3.eth.get_transaction(tx_hash)
            tx_receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            
            if not tx:
                return {'error': 'Transaction not found'}
            
            details = {
                'from': tx.get('from'),
                'to': tx.get('to'),
                'value': tx.get('value'),
                'input': tx.get('input'),
                'gas': tx.get('gas'),
                'gas_price': tx.get('gasPrice'),
                'nonce': tx.get('nonce'),
                'block_number': tx.get('blockNumber'),
                'logs': []
            }
            
            # Add logs with decoded topics if possible
            if tx_receipt and tx_receipt.get('logs'):
                for log in tx_receipt['logs']:
                    # Process topics safely
                    topics = []
                    for topic in log.get('topics', []):
                        if isinstance(topic, bytes):
                            topics.append(topic.hex())
                        else:
                            topics.append(str(topic))
                    
                    log_info = {
                        'address': log.get('address'),
                        'topics': topics,
                        'data': log.get('data')
                    }
                    
                    # Try to decode topic0 if it's in our signatures
                    if log.get('topics') and len(log['topics']) > 0:
                        topic0 = log['topics'][0]
                        # Handle both bytes and hex string formats
                        if isinstance(topic0, bytes):
                            topic0 = topic0.hex()
                        elif not topic0.startswith('0x'):
                            topic0 = '0x' + topic0
                        
                        if topic0 in EVENT_SIGNATURES:
                            log_info['event_name'] = EVENT_SIGNATURES[topic0]
                    
                    details['logs'].append(log_info)
            
            return details
            
        except Exception as e:
            return {'error': str(e)}

    def get_code_info(self, address):
        """Get code and basic info about an address"""
        code = self.w3.eth.get_code(address)
        code_size = len(code)
        code_hash = self.w3.keccak(code) if code_size > 0 else None
    
        return {
            'is_contract': code_size > 0,
            'code_size': code_size,
            'code_hash': code_hash.hex() if code_hash else None
        }

    def supports_interface(self, address, interface_id):
        """Check if contract supports ERC-165 interface"""
        try:
            # ERC-165 function signature: supportsInterface(bytes4)
            result = self.w3.eth.call({
                'to': address,
                'data': '0x01ffc9a7' + interface_id[2:]  # supportsInterface + interface_id
            })
            return result == b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01'
        except:
            return False

    def classify_block(self, block_data):
        """Classify what type of block this is based on all transactions"""
        if not block_data or 'transactions' not in block_data:
            return None
        
        # Check if transactions is a list or an integer
        transactions = block_data['transactions']
        if isinstance(transactions, int):
            # If it's an integer (transaction count), return basic classification
            return {
                'block_type': 'Standard Block',
                'classifications': {
                    'contract_creations': 0,
                    'trex_interactions': 0,
                    'erc20_transfers': 0,
                    'erc721_transfers': 0,
                    'generic_contracts': transactions,
                    'total_transactions': transactions
                },
                'primary_activity': f"Generic Contracts ({transactions})",
                'gas_efficiency': 'Unknown'
            }
            
        classifications = {
            'contract_creations': 0,
            'trex_interactions': 0,
            'erc20_transfers': 0,
            'erc721_transfers': 0,
            'generic_contracts': 0,
            'total_transactions': len(transactions)
        }
        
        # Analyze each transaction in the block with error handling
        print(f"DEBUG: Starting to analyze {len(transactions)} transactions")
        for i, tx in enumerate(transactions):
            try:
                print(f"DEBUG: Processing transaction {i}")
                # Check if hash exists and is valid
                if not tx or 'hash' not in tx or tx['hash'] is None:
                    classifications['generic_contracts'] += 1
                    print(f"Warning: Transaction missing hash: {tx}")
                    continue
                
                # Convert AttributeDict to regular dict if needed
                if hasattr(tx, '_asdict'):
                    tx_dict = dict(tx._asdict())
                elif hasattr(tx, '__dict__'):
                    tx_dict = dict(tx.__dict__)
                else:
                    tx_dict = dict(tx) if hasattr(tx, '__iter__') else tx
                
                print(f"DEBUG: Transaction {i} converted to dict, keys: {list(tx_dict.keys())}")
                
                # Debug: Show transaction data for classification
                print(f"DEBUG: Transaction {i} data:")
                print(f"  to: {tx_dict.get('to')}")
                print(f"  input: {tx_dict.get('input')}")
                print(f"  value: {tx_dict.get('value')}")
                
                # Use the same classification logic as the transaction classifier
                # This ensures consistency between block and transaction views
                tx_type = self._classify_transaction_from_data(tx_dict)
                print(f"DEBUG: Transaction {i} classified as: {tx_type}")
                
                # Store the classification data for the template
                tx_dict['classification'] = {
                    'type': tx_type,
                    'category': self._categorize_transaction(tx_type),
                    'priority': self._get_transaction_priority(tx_type),
                    'details': self._extract_transaction_details(tx_dict)
                }
                
                # Debug: Print what we're classifying
                print(f"DEBUG: Transaction {i}: {tx_type}")
                
                if 'Contract Creation' in tx_type:
                    classifications['contract_creations'] += 1
                    print(f"  -> Counted as Contract Creation")
                elif 'T-REX Interaction' in tx_type:
                    classifications['trex_interactions'] += 1
                    print(f"  -> Counted as T-REX Interaction")
                elif 'Token Transfer' in tx_type or 'Token Mint' in tx_type or 'Token Burn' in tx_type or 'Token Approval' in tx_type:
                    classifications['erc20_transfers'] += 1
                    print(f"  -> Counted as ERC-20 Transfer")
                elif 'ERC-721' in tx_type:
                    classifications['erc721_transfers'] += 1
                    print(f"  -> Counted as ERC-721")
                else:
                    classifications['generic_contracts'] += 1
                    print(f"  -> Counted as Generic Contract")
                
                print(f"DEBUG: Current counts - Contract Creations: {classifications['contract_creations']}, T-REX: {classifications['trex_interactions']}, ERC-20: {classifications['erc20_transfers']}, Generic: {classifications['generic_contracts']}")
                
                # Replace the original transaction with the mutable copy
                transactions[i] = tx_dict
                
            except Exception as e:
                # If transaction classification fails, count as generic
                print(f"DEBUG: Error processing transaction {i}: {e}")
                classifications['generic_contracts'] += 1
                continue
        
        # Debug: Print final classification counts
        print(f"DEBUG: Final block classifications:")
        print(f"  Contract Creations: {classifications['contract_creations']}")
        print(f"  T-REX Interactions: {classifications['trex_interactions']}")
        print(f"  ERC-20 Transfers: {classifications['erc20_transfers']}")
        print(f"  ERC-721 Transfers: {classifications['erc721_transfers']}")
        print(f"  Generic Contracts: {classifications['generic_contracts']}")
        
        # Determine block type
        if classifications['contract_creations'] > 0:
            block_type = "Deployment Block"
        elif classifications['trex_interactions'] > 0:
            block_type = "T-REX Activity Block"
        elif classifications['erc20_transfers'] > 0:
            block_type = "Token Transfer Block"
        elif classifications['erc721_transfers'] > 0:
            block_type = "NFT Activity Block"
        else:
            block_type = "Standard Block"
        
        print(f"DEBUG: Block type determined: {block_type}")
            
        return {
            'block_type': block_type,
            'classifications': classifications,
            'primary_activity': self._get_primary_activity(classifications),
            'gas_efficiency': self._calculate_gas_efficiency(block_data)
        }
    
    def _get_primary_activity(self, classifications):
        """Determine the primary activity in this block"""
        if classifications['contract_creations'] > 0:
            return f"Contract Deployments ({classifications['contract_creations']})"
        elif classifications['trex_interactions'] > 0:
            return f"T-REX Operations ({classifications['trex_interactions']})"
        elif classifications['erc20_transfers'] > 0:
            return f"Token Transfers ({classifications['erc20_transfers']})"
        elif classifications['erc721_transfers'] > 0:
            return f"NFT Operations ({classifications['erc721_transfers']})"
        else:
            return f"Generic Contracts ({classifications['generic_contracts']})"
    
    def _calculate_gas_efficiency(self, block_data):
        """Calculate gas efficiency metrics for the block"""
        if not block_data or 'gasUsed' not in block_data or 'gasLimit' not in block_data:
            return "Unknown"
            
        gas_used = int(block_data['gasUsed'])
        gas_limit = int(block_data['gasLimit'])
        efficiency = (gas_used / gas_limit) * 100
        
        if efficiency < 30:
            return "Low"
        elif efficiency < 70:
            return "Medium"
        else:
            return "High"
    
    def get_transaction_classification_details(self, tx_hash):
        """Get detailed classification for a single transaction"""
        try:
            # Check if tx_hash is valid
            if not tx_hash or tx_hash is None:
                return {
                    'type': "Invalid Transaction Hash",
                    'hash': 'None',
                    'details': {'error': 'Transaction hash is None or invalid'},
                    'category': 'Error',
                    'priority': 'Low'
                }
            
            tx_classification = self.classify_transaction(tx_hash)
            tx_details = self._get_transaction_details(tx_hash)
            
            # Enhanced classification details
            classification_details = {
                'type': tx_classification,
                'hash': tx_hash,
                'details': tx_details,
                'category': self._categorize_transaction(tx_classification),
                'priority': self._get_transaction_priority(tx_classification)
            }
            
            return classification_details
        except Exception as e:
            print(f"Warning: Failed to get transaction classification details for {tx_hash}: {e}")
            return {
                'type': "Transaction Classification Failed",
                'hash': tx_hash,
                'details': {'error': str(e)},
                'category': 'Error',
                'priority': 'Low'
            }
    
    def _categorize_transaction(self, tx_type):
        """Categorize transaction into high-level groups"""
        if 'Contract Creation' in tx_type:
            return 'Deployment'
        elif 'T-REX' in tx_type or 'ERC-3643' in tx_type:
            return 'T-REX'
        elif 'ERC-20' in tx_type:
            return 'Token'
        elif 'ERC-721' in tx_type:
            return 'NFT'
        elif 'ERC-1155' in tx_type:
            return 'NFT'
        else:
            return 'Contract'
    
    def _get_transaction_priority(self, tx_type):
        """Get priority level for transaction display"""
        if 'Contract Creation' in tx_type:
            return 'High'
        elif 'T-REX' in tx_type or 'ERC-3643' in tx_type:
            return 'High'
        elif 'Transfer' in tx_type:
            return 'Medium'
        else:
            return 'Low'
    
    def _classify_transaction_from_data(self, tx_dict):
        """Classify transaction using only the data we already have (NO RPC CALLS!)"""
        try:
            # Check if it's contract creation
            if tx_dict.get('to') is None:
                return "Contract Creation"
            
            # Check if it's a simple transfer (no input data)
            if tx_dict.get('input') == '0x' or tx_dict.get('input') == '':
                return "Token Transfer"
            
            # Analyze input data for function calls
            if tx_dict.get('input') and tx_dict['input'] != '0x':
                function_sig = tx_dict['input'][:10]
                function_name = TX_FUNCTION_SIGNATURES.get(function_sig, "Unknown Function")
                
                if "transfer" in function_name.lower():
                    return 'Token Transfer'
                elif "mint" in function_name.lower():
                    return 'Token Mint'
                elif "burn" in function_name.lower():
                    return 'Token Burn'
                elif "approve" in function_name.lower():
                    return 'Token Approval'
                elif "TREX" in function_name:
                    return 'T-REX Interaction'
                else:
                    return 'Contract Interaction'
            
            # If we can't determine from input, check if target address is known T-REX
            if tx_dict.get('to'):
                # Check if the target address matches any known T-REX contract patterns
                # This is a simple heuristic - you could expand this
                target = tx_dict['to'].lower()
                if any(keyword in target for keyword in ['trex', 'identity', 'claim', 'compliance']):
                    return 'T-REX Interaction'
            
            return "Contract Interaction"
            
        except Exception as e:
            return "Unknown"
    
    def _extract_transaction_details(self, tx_dict):
        """Extract transaction details from data we already have (NO RPC CALLS!)"""
        try:
            details = {
                'from': tx_dict.get('from'),
                'to': tx_dict.get('to'),
                'value': tx_dict.get('value'),
                'input': tx_dict.get('input'),
                'gas': tx_dict.get('gas'),
                'gas_price': tx_dict.get('gasPrice'),
                'nonce': tx_dict.get('nonce'),
                'block_number': tx_dict.get('blockNumber'),
                'logs': []  # We don't have logs from get_block, but that's OK
            }
            
            # Try to extract function name from input data
            if tx_dict.get('input') and tx_dict['input'] != '0x':
                function_sig = tx_dict['input'][:10]
                function_name = TX_FUNCTION_SIGNATURES.get(function_sig, "Unknown Function")
                details['function'] = function_name
            
            return details
            
        except Exception as e:
            return {'error': str(e)}
