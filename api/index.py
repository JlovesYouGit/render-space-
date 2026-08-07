import json
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Import the render server functionality
import sys
sys.path.insert(0, '..')
from render_space_server import RenderMemoryServer

render_server = RenderMemoryServer()

@app.route('/')
def index():
    """Server status"""
    return jsonify({
        "server": "Render Space - Distributed GPU Memory Server",
        "version": "1.0.0",
        "node_id": render_server.local_node_id,
        "status": "active"
    })

@app.route('/gpu-memory')
def get_gpu_memory():
    """Get GPU memory regions"""
    regions = render_server.get_gpu_memory_regions()
    return jsonify({
        "node_id": render_server.local_node_id,
        "gpu_memory_regions": regions
    })

@app.route('/refresh-rate')
def get_refresh_rate():
    """Get high-precision refresh rate data"""
    timing = render_server.get_high_precision_refresh_rate()
    return jsonify({
        "node_id": render_server.local_node_id,
        "timing_data": timing
    })

@app.route('/register-node', methods=['POST'])
def register_node():
    """Register a render node"""
    data = request.json
    
    from dataclasses import dataclass, asdict
    from datetime import datetime
    import uuid
    
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
        ip_address=request.remote_addr,
        gpu_memory_regions=data.get('gpu_memory_regions', []),
        refresh_rate=data.get('refresh_rate', 60),
        timestamp=datetime.utcnow().isoformat(),
        blockchain_address=data.get('blockchain_address', '')
    )
    
    render_server.add_block({
        "type": "node_registration",
        "node": asdict(node),
        "node_id": render_server.local_node_id
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
    import uuid
    
    memory_share = {
        "source_node": render_server.local_node_id,
        "memory_regions": data.get('memory_regions', []),
        "refresh_rate": data.get('refresh_rate', 60),
        "timestamp": datetime.utcnow().isoformat(),
        "share_id": str(uuid.uuid4())
    }
    
    render_server.add_block({
        "type": "memory_share",
        "share": memory_share,
        "node_id": render_server.local_node_id
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

# Global state for the serverless function
render_memory_state = {
    "nodes": {},
    "gpu_memory_regions": [],
    "refresh_rates": {},
    "timing_data": {},
    "blockchain_data": {
        "blocks": [],
        "pending_transactions": [],
        "node_id": render_server.local_node_id
    }
}

# Vercel serverless function handler
def handler(event, context):
    return app(event, context)
