const crypto = require('crypto');

// Global state for serverless function
const renderMemoryState = {
  nodes: {},
  gpuMemoryRegions: [],
  refreshRates: {},
  timingData: {},
  blockchainData: {
    blocks: [],
    pendingTransactions: [],
    nodeId: crypto.randomUUID()
  }
};

function getGPUMemoryRegions() {
  const regions = [
    { baseAddress: "0x100000000", sizeBytes: 405218000896, sizeGB: 405218000896 / (1024**3), type: "render_frame_buffer", protection: "read_write" },
    { baseAddress: "0x200000000", sizeBytes: 400923033600, sizeGB: 400923033600 / (1024**3), type: "render_frame_buffer", protection: "read_write" },
    { baseAddress: "0x300000000", sizeBytes: 396628066304, sizeGB: 396628066304 / (1024**3), type: "render_frame_buffer", protection: "read_write" }
  ];
  renderMemoryState.gpuMemoryRegions = regions;
  return regions;
}

function getHighPrecisionRefreshRate() {
  const timing = {
    timerFrequencyHz: 10000000,
    timerResolutionMicroseconds: 0.1,
    availableRefreshRatesHz: [60, 75, 120, 144],
    maxRefreshRate: 144,
    frameTimeMicroseconds: 6944.44
  };
  renderMemoryState.refreshRates = timing;
  return timing;
}

function createBlock(data) {
  const blockchain = renderMemoryState.blockchainData;
  const previousBlock = blockchain.blocks[blockchain.blocks.length - 1];
  const previousHash = previousBlock ? previousBlock.hash : "0".repeat(64);
  
  const block = {
    index: blockchain.blocks.length,
    timestamp: new Date().toISOString(),
    data: data,
    previousHash: previousHash,
    nodeId: blockchain.nodeId,
    hash: ""
  };
  
  const blockString = JSON.stringify(block, Object.keys(block).sort());
  block.hash = crypto.createHash('sha256').update(blockString).digest('hex');
  return block;
}

function addBlock(data) {
  const block = createBlock(data);
  renderMemoryState.blockchainData.blocks.push(block);
  return block;
}

export default function handler(req, res) {
  // Handle Vercel's request structure
  const { url, method } = req;
  
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  // Parse URL path (Vercel provides full URL)
  const path = url || '/';
  
  // Route handling
  if (path === '/' || path === '/api') {
    return res.json({
      server: "Render Space - Distributed GPU Memory Server",
      version: "1.0.0",
      nodeId: renderMemoryState.blockchainData.nodeId,
      status: "active"
    });
  }
  
  if (path === '/api/gpu-memory') {
    const regions = getGPUMemoryRegions();
    addBlock({
      type: "gpu_memory_update",
      regions: regions,
      nodeId: renderMemoryState.blockchainData.nodeId
    });
    return res.json({
      nodeId: renderMemoryState.blockchainData.nodeId,
      gpuMemoryRegions: regions
    });
  }
  
  if (path === '/api/refresh-rate') {
    const timing = getHighPrecisionRefreshRate();
    addBlock({
      type: "refresh_rate_update",
      timing: timing,
      nodeId: renderMemoryState.blockchainData.nodeId
    });
    return res.json({
      nodeId: renderMemoryState.blockchainData.nodeId,
      timingData: timing
    });
  }
  
  if (path === '/api/nodes') {
    return res.json({
      nodes: renderMemoryState.nodes,
      count: Object.keys(renderMemoryState.nodes).length
    });
  }
  
  if (path === '/api/blockchain') {
    return res.json({
      blocks: renderMemoryState.blockchainData.blocks,
      nodeId: renderMemoryState.blockchainData.nodeId,
      length: renderMemoryState.blockchainData.blocks.length
    });
  }
  
  if (path === '/api/bitcoin-integration') {
    return res.json({
      bitcoinIntegration: {
        status: "ready",
        network: "mainnet",
        nodeAddress: renderMemoryState.blockchainData.nodeId,
        features: [
          "decentralized_render_memory",
          "gpu_sharing_protocol",
          "refresh_rate_synchronization",
          "timing_data_distribution"
        ]
      }
    });
  }
  
  if (path === '/api/network-stats') {
    const totalMemory = renderMemoryState.gpuMemoryRegions.reduce((sum, region) => sum + region.sizeGB, 0);
    return res.json({
      totalNodes: Object.keys(renderMemoryState.nodes).length,
      totalGpuMemoryGB: totalMemory,
      blockchainLength: renderMemoryState.blockchainData.blocks.length,
      serverUptime: "active"
    });
  }
  
  if (path === '/api/register-node' && method === 'POST') {
    const data = req.body;
    const node = {
      nodeId: data.nodeId || crypto.randomUUID(),
      ipAddress: req.headers['x-forwarded-for'] || req.socket.remoteAddress || 'unknown',
      gpuMemoryRegions: data.gpuMemoryRegions || [],
      refreshRate: data.refreshRate || 60,
      timestamp: new Date().toISOString(),
      blockchainAddress: data.blockchainAddress || ''
    };
    
    renderMemoryState.nodes[node.nodeId] = node;
    addBlock({
      type: "node_registration",
      node: node,
      nodeId: renderMemoryState.blockchainData.nodeId
    });
    
    return res.json({
      status: "registered",
      nodeId: node.nodeId,
      timestamp: node.timestamp
    });
  }
  
  if (path === '/api/share-memory' && method === 'POST') {
    const data = req.body;
    const memoryShare = {
      sourceNode: renderMemoryState.blockchainData.nodeId,
      memoryRegions: data.memoryRegions || [],
      refreshRate: data.refreshRate || 60,
      timestamp: new Date().toISOString(),
      shareId: crypto.randomUUID()
    };
    
    addBlock({
      type: "memory_share",
      share: memoryShare,
      nodeId: renderMemoryState.blockchainData.nodeId
    });
    
    return res.json({
      status: "shared",
      shareId: memoryShare.shareId,
      timestamp: memoryShare.timestamp
    });
  }
  
  // 404 for unknown routes
  return res.status(404).json({ error: "Not Found" });
}
