import './style.css';
import ForceGraph3D from '3d-force-graph';
import * as THREE from 'three';

let taxonomyData = null;
let graph = null;
let nodes = [];
let links = [];

let nodeScale = 1.0;
let isAutoRotating = false;

// UI Elements
const sidebar = document.getElementById('sidebar');
const sidebarContent = document.getElementById('sidebar-content');
const closeBtn = document.getElementById('close-sidebar');

const btnRotate = document.getElementById('btn-rotate');
const btnCollapse = document.getElementById('btn-collapse');
const btnReset = document.getElementById('btn-reset');
const sizeSlider = document.getElementById('size-slider');
const sizeVal = document.getElementById('size-val');

// Event Listeners
closeBtn.addEventListener('click', () => {
  sidebar.classList.add('hidden');
});

btnRotate.addEventListener('click', () => {
  isAutoRotating = !isAutoRotating;
  btnRotate.textContent = isAutoRotating ? 'Stop Auto-Rotate' : 'Start Auto-Rotate';
  btnRotate.style.background = isAutoRotating ? 'rgba(56, 189, 248, 0.3)' : '';
});

btnCollapse.addEventListener('click', () => {
  // Reset data back to just Root and Domains
  nodes = nodes.filter(n => n.type === 'root' || n.type === 'domain');
  links = links.filter(l => l.source.type === 'root' || l.target.type === 'root');
  
  nodes.forEach(n => { n.expanded = false; });
  // Find root and ensure it's expanded
  const rootNode = nodes.find(n => n.type === 'root');
  if (rootNode) rootNode.expanded = true;

  updateGraphData();
  resetCamera();
});

btnReset.addEventListener('click', resetCamera);

sizeSlider.addEventListener('input', (e) => {
  nodeScale = parseFloat(e.target.value);
  sizeVal.textContent = nodeScale.toFixed(1);
  // Trigger a re-render of node sizes
  graph.nodeVal(node => getNodeRadius(node) * nodeScale);
});

window.addEventListener('resize', () => {
  if (graph) {
    graph.width(window.innerWidth);
    graph.height(window.innerHeight);
  }
});

async function init() {
  try {
    const response = await fetch('/taxonomy_data.json');
    if (!response.ok) throw new Error('Failed to load data');
    taxonomyData = await response.json();
    document.getElementById('loader').style.display = 'none';
    buildInitialGraph();
  } catch (err) {
    document.getElementById('loader').innerText = 'Error loading taxonomy data. Run python script.';
    document.getElementById('loader').style.color = '#ef4444';
  }
}

function getNodeRadius(node) {
  if (node.type === 'root') return 20;
  if (node.type === 'domain') return 12;
  if (node.type === 'discipline') return 6;
  return 3;
}

function getNodeColor(node) {
  if (node.type === 'root') return '#ffffff';
  if (node.type === 'domain') return '#38bdf8';
  if (node.type === 'discipline') return '#818cf8';
  return '#a78bfa';
}

function buildInitialGraph() {
  const rootNode = { id: 'root', name: 'Knowledge Catalogs', type: 'root', expanded: true };
  nodes.push(rootNode);

  taxonomyData.domains.forEach(domain => {
    const dNode = { 
      id: `domain_${domain.id}`, 
      name: domain.name, 
      type: 'domain', 
      expanded: false,
      data: domain 
    };
    nodes.push(dNode);
    links.push({ source: 'root', target: dNode.id });
  });

  setupGraph3D();
}

function setupGraph3D() {
  const elem = document.getElementById('viz-container');

  graph = ForceGraph3D()(elem)
    .graphData({ nodes, links })
    .nodeLabel('name')
    .nodeVal(node => getNodeRadius(node) * nodeScale)
    .nodeColor(node => getNodeColor(node))
    .nodeOpacity(0.9)
    .nodeResolution(32)
    .linkWidth(1.5)
    .linkOpacity(0.3)
    .linkColor(() => 'rgba(255,255,255,0.4)')
    .backgroundColor('#02040a')
    .onNodeClick(handleNodeClick)
    .onBackgroundClick(() => { sidebar.classList.add('hidden'); });

  // Add 3D Starfield Background directly to the Three.js Scene
  const scene = graph.scene();
  
  // Custom particle starfield
  const starGeometry = new THREE.BufferGeometry();
  const starCount = 3000;
  const positions = new Float32Array(starCount * 3);
  const colors = new Float32Array(starCount * 3);
  
  for(let i=0; i < starCount; i++) {
    const radius = 2000 + Math.random() * 3000;
    const theta = Math.random() * 2 * Math.PI;
    const phi = Math.acos(Math.random() * 2 - 1);
    
    positions[i*3] = radius * Math.sin(phi) * Math.cos(theta);
    positions[i*3+1] = radius * Math.sin(phi) * Math.sin(theta);
    positions[i*3+2] = radius * Math.cos(phi);
    
    // Slight color variation
    const mix = Math.random();
    colors[i*3] = 0.8 + mix * 0.2; // R
    colors[i*3+1] = 0.8 + mix * 0.2; // G
    colors[i*3+2] = 1.0; // B
  }
  
  starGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  starGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  
  const starMaterial = new THREE.PointsMaterial({
    size: 5,
    vertexColors: true,
    transparent: true,
    opacity: 0.8,
    sizeAttenuation: true
  });
  
  const starfield = new THREE.Points(starGeometry, starMaterial);
  scene.add(starfield);

  // Improve Lighting
  scene.add(new THREE.AmbientLight(0x404040, 2.0)); // soft white light

  // Custom force adjustments to spread things out beautifully in 3D
  graph.d3Force('charge').strength(-400);
  graph.d3Force('link').distance(link => {
    if (link.source.type === 'root' || link.target.type === 'root') return 200;
    if (link.source.type === 'domain' || link.target.type === 'domain') return 100;
    return 50;
  });

  // Start Animation Loop for Auto-Rotate
  let angle = 0;
  setInterval(() => {
    if (isAutoRotating) {
      angle += Math.PI / 1000;
      const distance = graph.cameraPosition().z || 1000;
      // maintain roughly current distance but orbit around center
      graph.cameraPosition({
        x: distance * Math.sin(angle),
        z: distance * Math.cos(angle)
      });
    }
  }, 10);
}

function updateGraphData() {
  graph.graphData({ nodes, links });
}

function resetCamera() {
  graph.cameraPosition(
    { x: 0, y: 0, z: 1000 }, 
    { x: 0, y: 0, z: 0 }, 
    2000 // ms transition
  );
}

function handleNodeClick(node) {
  // Focus Camera
  const distance = 300;
  const distRatio = 1 + distance / Math.hypot(node.x, node.y, node.z);
  graph.cameraPosition(
    { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio },
    node, // lookAt
    2000 // ms transition
  );

  // Disable auto-rotate when examining a node
  if (isAutoRotating) {
    isAutoRotating = false;
    btnRotate.textContent = 'Start Auto-Rotate';
    btnRotate.style.background = '';
  }

  // Handle Expansion
  if (node.type === 'domain') {
    if (node.expanded) {
      collapseNode(node);
    } else {
      expandDomain(node);
    }
  } else if (node.type === 'discipline') {
    if (node.expanded) {
      collapseNode(node);
    } else {
      expandDiscipline(node);
    }
  }

  // Update UI sidebar
  populateSidebar(node);
  sidebar.classList.remove('hidden');
}

function expandDomain(dNode) {
  dNode.expanded = true;
  const domainData = dNode.data;
  
  domainData.disciplines.forEach(disc => {
    const id = `disc_${disc.id}`;
    if (!nodes.find(n => n.id === id)) {
      nodes.push({
        id: id,
        name: disc.name,
        type: 'discipline',
        expanded: false,
        data: disc
      });
      links.push({ source: dNode.id, target: id });
    }
  });
  updateGraphData();
}

function expandDiscipline(discNode) {
  discNode.expanded = true;
  const discData = discNode.data;
  
  if (discData.concepts) {
    discData.concepts.forEach((concept, idx) => {
      const id = `concept_${discData.id}_${idx}`;
      if (!nodes.find(n => n.id === id)) {
        nodes.push({
          id: id,
          name: concept,
          type: 'concept',
          expanded: false
        });
        links.push({ source: discNode.id, target: id });
      }
    });
    updateGraphData();
  }
}

function collapseNode(node) {
  node.expanded = false;
  const descendants = getDescendants(node.id);
  nodes = nodes.filter(n => !descendants.includes(n.id));
  links = links.filter(l => !descendants.includes((l.source.id || l.source)) && !descendants.includes((l.target.id || l.target)));
  updateGraphData();
}

function getDescendants(nodeId) {
  let desc = [];
  const children = links.filter(l => (l.source.id || l.source) === nodeId)
                        .map(l => (l.target.id || l.target));
  
  desc.push(...children);
  children.forEach(childId => {
    desc.push(...getDescendants(childId));
  });
  return desc;
}

function populateSidebar(node) {
  let html = '';
  
  if (node.type === 'root') {
    html += `<h2 class="sidebar-title">Foundation Catalogs</h2>
             <p class="sidebar-subtitle">Audited Taxonomies & Indexes</p>
             <p style="color: #cbd5e1; font-size: 0.95rem;">This taxonomy was swept against these external catalogs.</p>
             <table class="audit-table">
               <thead><tr><th>Catalog</th><th>Outcome</th></tr></thead><tbody>`;
    taxonomyData.catalogs.forEach(audit => {
      html += `<tr><td><strong>${audit.catalog}</strong></td><td>${audit.outcome}</td></tr>`;
    });
    html += `</tbody></table>`;
             
  } else if (node.type === 'domain') {
    html += `<h2 class="sidebar-title">${node.data.name}</h2>
             <p class="sidebar-subtitle">Domain</p>
             <p style="color: #cbd5e1; margin-bottom: 1rem;">Contains ${node.data.disciplines.length} disciplines.</p>
             <p style="color: #94a3b8; font-size: 0.9rem;"><em>Click the node to expand its disciplines in 3D.</em></p>`;
             
  } else if (node.type === 'discipline') {
    html += `<h2 class="sidebar-title">${node.data.name}</h2>
             <p class="sidebar-subtitle">Discipline</p>
             <div class="sidebar-img-container">
               <div class="sidebar-img-fallback">${node.data.name.substring(0, 2).toUpperCase()}</div>
               <img src="/images/disciplines/${node.data.id}.jpg" class="sidebar-img" onerror="this.style.display='none'" />
             </div>
             <h3 style="color: white; margin-bottom: 0.5rem; font-size: 1.1rem;">Concepts</h3>`;
             
    if (node.data.concepts && node.data.concepts.length > 0) {
      html += `<div>`;
      node.data.concepts.forEach(c => { html += `<span class="concept-tag">${c}</span>`; });
      html += `</div>`;
    } else {
      html += `<p style="color: #94a3b8;">No concepts populated yet.</p>`;
    }
  } else if (node.type === 'concept') {
    html += `<h2 class="sidebar-title">${node.name}</h2>
             <p class="sidebar-subtitle">Concept</p>`;
  }
  
  sidebarContent.innerHTML = html;
}

init();
