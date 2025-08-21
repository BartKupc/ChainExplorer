# 🚀 CronoExplorer

**A powerful blockchain explorer for Ethereum-compatible chains with intelligent transaction and contract classification.**

CronoExplorer provides real-time blockchain analysis with advanced transaction classification, contract detection, and user-friendly web interface. It automatically identifies ERC-20, ERC-721, ERC-1155, and T-REX (ERC-3643) contracts and transactions.

## ✨ Features

- 🔍 **Smart Transaction Classification**: Automatically identifies token transfers, contract interactions, and deployments
- 🦖 **T-REX Protocol Support**: Full detection of ERC-3643 compliant contracts and transactions
- 🪙 **Multi-Token Support**: ERC-20, ERC-721, ERC-1155 detection and analysis
- 🌐 **Multi-Chain Support**: Works with any Ethereum-compatible blockchain
- 📊 **Real-time Block Analysis**: Live block monitoring with transaction breakdowns
- 🎯 **Event Log Decoding**: Intelligent parsing of blockchain events and logs
- 🚀 **High Performance**: Optimized RPC calls with smart caching strategies
- 💻 **Modern Web Interface**: Clean, responsive Flask-based web application

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- Access to Ethereum-compatible RPC endpoint
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/CronoExplorer.git
   cd CronoExplorer
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your chains**
   ```bash
   # Edit chains.yaml with your RPC endpoints
   nano chains.yaml
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**
   ```
   http://localhost:5001
   ```

## ⚙️ Configuration

### Chains Configuration (`chains.yaml`)

```yaml
chains:
  Cronos:
    rpc_url: "https://evm.cronos.org"
    chain_id: 25
    name: "Cronos Mainnet"
    enabled: true
  
  Ethereum:
    rpc_url: "https://mainnet.infura.io/v3/YOUR_API_KEY"
    chain_id: 1
    name: "Ethereum Mainnet"
    enabled: true
  
  Polygon:
    rpc_url: "https://polygon-rpc.com"
    chain_id: 137
    name: "Polygon Mainnet"
    enabled: true
```

### Environment Variables

Create a `.env` file for sensitive configuration:

```bash
# Database configuration
DATABASE_URL=sqlite:///instance/cronoexplorer.db

# Flask secret key
SECRET_KEY=your-secret-key-here

# RPC rate limiting
RPC_TIMEOUT=30
MAX_RPC_RETRIES=3
```

## 🎯 Usage

### Web Interface

1. **Home Page**: View latest blocks with transaction summaries
2. **Block Details**: Click on any block to see detailed transaction analysis
3. **All Blocks**: Browse blocks with pagination and search
4. **Chain Management**: Switch between different blockchain networks

### Transaction Classification

CronoExplorer automatically classifies transactions into:

- **Token Transfers**: ERC-20, ERC-721, ERC-1155 transfers
- **Contract Deployments**: New contract creations
- **T-REX Interactions**: ERC-3643 protocol transactions
- **Generic Contracts**: Other smart contract interactions
- **ETH Transfers**: Native cryptocurrency transfers

### Block Analysis

Each block shows:
- Primary activity type
- Gas efficiency metrics
- Transaction classification breakdown
- Contract creation counts
- Token interaction summaries

## 🔧 Development

### Project Structure

```
CronoExplorer/
├── app.py                 # Main Flask application
├── config.py             # Configuration management
├── core/                 # Core classification logic
│   ├── contract.py       # Contract and transaction classifiers
│   └── queries.py        # Blockchain RPC queries
├── models/               # Database models
├── services/             # Business logic services
├── templates/            # HTML templates
├── static/               # CSS, JS, and static assets
├── tests.py              # Test suite
└── requirements.txt      # Python dependencies
```

### Running Tests

```bash
python tests.py
```

### Adding New Chain Support

1. Add chain configuration to `chains.yaml`
2. Test RPC connectivity
3. Verify transaction format compatibility

## 🌟 Advanced Features

### Smart Caching

- Transaction classification results are cached for performance
- Block summaries reuse detailed transaction analysis
- Minimizes redundant RPC calls

### Event Fingerprinting

- Fast contract type detection using event signatures
- Topic0 matching against known event patterns
- ERC-165 interface detection for standard compliance

### Performance Optimization

- Parallel RPC calls where possible
- Lazy classification for non-critical data
- Efficient log parsing and event decoding

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
