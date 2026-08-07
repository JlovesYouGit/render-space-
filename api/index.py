from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import hashlib
import uuid
from datetime import datetime
from dataclasses import dataclass, asdict

app = Flask(__name__)
CORS(app)

# Global state for serverless function
render_memory_state = {
    "nodes": {},
    "gpu_memory_regions": [],
    "refresh_rates": {},
    "timing_data": {},
    "blockchain_data": {
        "blocks": [],
        "pending_transactions": [],
        "node_id": str(uuid.uuid4())
    }
}

def get_gpu_memory_regions():
    """Get GPU memory regions"""
    regions = [
        {"base_address": "0x100000000", "size_bytes": 405218000896, "size_gb": 405218000896 / (1024**3), "type": "render_frame_buffer", "protection": "read_write"},
        {"base_address": "0x200000000", "size_bytes": 400923033600, "size_gb": 400923033600 / (1024**3), "type": "render_frame_buffer", "protection": "read_write"},
        {"base_address": "0x300000000", "size_bytes": 396628066304, "size_gb": 396628066304 / (1024**3), "type": "render_frame_buffer", "protection": "read_write"}
    ]
    render_memory_state["gpu_memory_regions"] = regions
    return regions

def get_high_precision_refresh_rate():
    """Get high-precision refresh rate data"""
    timing = {
        "timer_frequency_hz": 10000000,
        "timer_resolution_microseconds": 0.1,
        "available_refresh_rates_hz": [60, 75, 120, 144],
        "max_refresh_rate": 144,
        "frame_time_microseconds": 6944.44
    }
    render_memory_state["refresh_rates"] = timing
    return timing

def create_block(data):
    """Create a blockchain block"""
    blockchain = render_memory_state["blockchain_data"]
    previous_block = blockchain["blocks"][-1] if blockchain["blocks"] else None
    previous_hash = previous_block["hash"] if previous_block else "0" * 64
    
    block = {
        "index": len(blockchain["blocks"]),
        "timestamp": datetime.utcnow().isoformat(),
        "data": data,
        "previous_hash": previous_hash,
        "node_id": blockchain["node_id"],
        "hash": ""
    }
    
    block_string = json.dumps(block, sort_keys=True)
    block["hash"] = hashlib.sha256(block_string.encode()).hexdigest()
    return block

def add_block(data):
    """Add a block to the blockchain"""
    block = create_block(data)
    render_memory_state["blockchain_data"]["blocks"].append(block)
    return block

@app.route('/')
def index():
    """Server status"""
    return jsonify({
        "server": "Render Space - Distributed GPU Memory Server",
        "version": "1.0.0",
        "node_id": render_memory_state["blockchain_data"]["node_id"],
        "status": "active"
    })

@app.route('/gpu-memory')
def get_gpu_memory():
    """Get GPU memory regions"""
    regions = get_gpu_memory_regions()
    add_block({
        "type": "gpu_memory_update",
        "regions": regions,
        "node_id": render_memory_state["blockchain_data"]["node_id"]
    })
    return jsonify({
        "node_id": render_memory_state["blockchain_data"]["node_id"],
        "gpu_memory_regions": regions
    })

@app.route('/refresh-rate')
def get_refresh_rate():
    """Get high-precision refresh rate data"""
    timing = get_high_precision_refresh_rate()
    add_block({
        "type": "refresh_rate_update",
        "timing": timing,
        "node_id": render_memory_state["blockchain_data"]["node_id"]
    })
    return jsonify({
        "node_id": render_memory_state["blockchain_data"]["node_id"],
        "timing_data": timing
    })

@app.route('/register-node', methods=['POST'])
def register_node():
    """Register a render node"""
    data = request.json
    
    @dataclass
    class RenderNode:
        node_id: str
        ip_address: str
        gpu_memory_regions: list
        refresh_rate: int
        timestamp: str
        blockchain_address: str
    
    node = RenderNode(
        node_id=data.get('node_id', str(uuid.uuid4())),
        ip_address=request.remote_addr if request.remote_addr else "unknown",
        gpu_memory_regions=data.get('gpu_memory_regions', []),
        refresh_rate=data.get('refresh_rate', 60),
        timestamp=datetime.utcnow().isoformat(),
        blockchain_address=data.get('blockchain_address', '')
    )
    
    render_memory_state["nodes"][node.node_id] = asdict(node)
    add_block({
        "type": "node_registration",
        "node": asdict(node),
        "node_id": render_memory_state["blockchain_data"]["node_id"]
    })
    
    return jsonify({
        "status": "registered",
        "node_id": node.node_id,
        "timestamp": node.timestamp
    })

@app.route('/nodes')
def get_nodes():
    """Get all registered nodes"""
    return jsonify({
        "nodes": render_memory_state["nodes"],
        "count": len(render_memory_state["nodes"])
    })

@app.route('/blockchain')
def get_blockchain():
    """Get blockchain data"""
    return jsonify({
        "blocks": render_memory_state["blockchain_data"]["blocks"],
        "node_id": render_memory_state["blockchain_data"]["node_id"],
        "length": len(render_memory_state["blockchain_data"]["blocks"])
    })

@app.route('/share-memory', methods=['POST'])
def share_memory():
    """Share GPU memory space with network"""
    data = request.json
    
    memory_share = {
        "source_node": render_memory_state["blockchain_data"]["node_id"],
        "memory_regions": data.get('memory_regions', []),
        "refresh_rate": data.get('refresh_rate', 60),
        "timestamp": datetime.utcnow().isoformat(),
        "share_id": str(uuid.uuid4())
    }
    
    add_block({
        "type": "memory_share",
        "share": memory_share,
        "node_id": render_memory_state["blockchain_data"]["node_id"]
    })
    
    return jsonify({
        "status": "shared",
        "share_id": memory_share["share_id"],
        "timestamp": memory_share["timestamp"]
    })

@app.route('/bitcoin-integration')
def bitcoin_integration():
    """Bitcoin network integration status"""
    return jsonify({
        "bitcoin_integration": {
            "status": "ready",
            "network": "mainnet",
            "node_address": render_memory_state["blockchain_data"]["node_id"],
            "features": [
                "decentralized_render_memory",
                "gpu_sharing_protocol",
                "refresh_rate_synchronization",
                "timing_data_distribution"
            ]
        }
    })

@app.route('/network-stats')
def network_stats():
    """Network statistics"""
    total_memory = sum(region["size_gb"] for region in render_memory_state["gpu_memory_regions"])
    
    return jsonify({
        "total_nodes": len(render_memory_state["nodes"]),
        "total_gpu_memory_gb": total_memory,
        "blockchain_length": len(render_memory_state["blockchain_data"]["blocks"]),
        "server_uptime": "active"
    })

# Vercel serverless function handler
def handler(event, context):
    return app(event, context)
