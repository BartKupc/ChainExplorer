#!/usr/bin/env python3
from web3 import Web3

# Your IdentityRegistry events from the ABI
events = [
    # IdentityRegistry (ERC-3643)
    "IdentityRegistered(address,address)",
    "IdentityRemoved(address,address)", 
    "IdentityUpdated(address,address)",
    
    # ClaimTopicsRegistry
    "ClaimTopicAdded(uint256)",
    "ClaimTopicRemoved(uint256)",
    
    # TrustedIssuersRegistry  
    "TrustedIssuerAdded(address,uint256[])",
    "TrustedIssuerRemoved(address)",
    "ClaimTopicsUpdated(address,uint256[])",
    
    # ComplianceRegistry
    "ComplianceAdded(address)",
    "TokenBound(address)",
    
    # T-REX Token (ERC-3643) - CORRECTED
    "AgentAdded(address)",
    "AgentRemoved(address)",
    "Transfer(address,address,uint256)",  

    # T-REX Factory - NEW
    "Deployed(address)",
    "IdFactorySet(address)",
    "ImplementationAuthoritySet(address)",
    "TREXSuiteDeployed(address,address,address,address,address,address,string)",

    #onchainid
    "createIdentity(address,string)",
    "addTokenFactory(address)",
    "createIdentityWithManagementKeys(address,string,bytes32[])",
    "createTokenIdentity(address,address,string)",
    "getIdentity(address)",
    "getToken(address)",
    "getWallets(address)",
    "implementationAuthority()",
    "isSaltTaken(string)",
    "isTokenFactory(address)",
    "linkWallet(address)",
    "removeTokenFactory(address)",
    "unlinkWallet(address)"
    
    "IdentityCreated(address,address)",

    "KeyAdded(bytes32,uint256,uint256)",
    "IdentityInitialized(address)",
    "ManagementKeySet(bytes32,address)"

]

print("IdentityRegistry Event Hashes:")
print("=" * 40)

for event in events:
    # Calculate keccak256 hash
    topic0_hash = Web3.keccak(text=event).hex()
    print(f'"{topic0_hash}": "{event}",')
    with open("abi_signature.txt", "a") as f:
        f.write(f'"{topic0_hash}"\n')

print("\nCopy these to your EVENT_SIGNATURES dictionary!")

