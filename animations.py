# animations.py

BLOOD_FLOW_HTML = """
<div style="background:#131313; padding:12px; border-radius:6px; border:1px solid #2d2d2d; color:#fff; font-family:sans-serif;">
    <div style="display:flex; justify-content:space-between; margin-bottom:10px; font-size:12px; gap:10px;">
        <label style="flex:1;">💧 Hydration Level: <span id="hydVal">100%</span>
            <input type="range" id="hydSlider" min="30" max="150" value="100" style="width:100%;">
        </label>
        <label style="flex:1;">🩸 Plasma Volume: <span id="plasVal">100%</span>
            <input type="range" id="plasSlider" min="50" max="150" value="100" style="width:100%;">
        </label>
    </div>
    <canvas id="bloodCanvas" style="width:100%; height:120px; background:#000; border-radius:4px; display:block;"></canvas>
    <div style="display:flex; gap:5px; margin-top:8px;">
        <button onclick="setBloodMode('healthy')" style="flex:1; background:#00cc66; color:#fff; border:none; padding:6px; font-weight:bold; border-radius:4px; cursor:pointer; font-size:11px;">Healthy (Negative Charge)</button>
        <button onclick="setBloodMode('sticky')" style="flex:1; background:#ff3333; color:#fff; border:none; padding:6px; font-weight:bold; border-radius:4px; cursor:pointer; font-size:11px;">Sticky/Clumped (Neutral)</button>
    </div>
</div>
<script>
    const bCanvas = document.getElementById('bloodCanvas'); const bCtx = bCanvas.getContext('2d');
    const hydSlider = document.getElementById('hydSlider'); const hydVal = document.getElementById('hydVal');
    const plasSlider = document.getElementById('plasSlider'); const plasVal = document.getElementById('plasVal');
    
    let bMode = 'healthy'; let bCells = [];
    function bResize() { bCanvas.width = bCanvas.clientWidth; bCanvas.height = bCanvas.clientHeight; }
    
    class BCell {
        constructor() { this.reset(); this.x = Math.random() * 250; }
        reset() { this.y = Math.random() * (bCanvas.height - 20) + 10; this.x = -15; this.radius = 6; }
        update() {
            let hMod = parseFloat(hydSlider.value) / 100;
            let pMod = parseFloat(plasSlider.value) / 100;
            
            if (bMode === 'healthy') { 
                this.x += 1.4 * hMod * pMod; 
                this.y += Math.sin(this.x * 0.04) * 0.2; 
            } else { 
                this.x += 0.4 * hMod; 
                let row = Math.floor(this.y / (18 * pMod)); 
                let tY = row * (18 * pMod) + 10; 
                this.y += (tY - this.y) * 0.05; 
            }
            if (this.x > bCanvas.width + 15) this.reset();
        }
        draw() {
            bCtx.save(); bCtx.translate(this.x, this.y); bCtx.scale(1.2, 0.7); bCtx.beginPath();
            bCtx.arc(0, 0, this.radius, 0, Math.PI * 2); bCtx.fillStyle = bMode === 'healthy' ? '#ff3333' : '#730000'; bCtx.fill(); bCtx.restore();
            if (bMode === 'healthy') { bCtx.fillStyle = '#00ffff'; bCtx.font = '8px sans-serif'; bCtx.fillText('-', this.x-2, this.y-4); }
        }
    }
    
    hydSlider.oninput = () => { hydVal.innerText = hydSlider.value + '%'; if(parseInt(hydSlider.value) < 60) bMode = 'sticky'; };
    plasSlider.oninput = () => plasVal.innerText = plasSlider.value + '%';

    window.addEventListener('load', () => {
        bResize(); for(let i=0; i<15; i++) bCells.push(new BCell());
        function anim() { bCtx.clearRect(0,0,bCanvas.width,bCanvas.height); if(bMode==='sticky') bCells.sort((a,b)=>a.x-b.x); bCells.forEach(c=>{c.update();c.draw();}); requestAnimationFrame(anim); }
        anim();
    });
    function setBloodMode(m) { bMode = m; if(m==='healthy' && parseInt(hydSlider.value)<60) hydSlider.value=100; hydVal.innerText=hydSlider.value+'%'; }
</script>
"""

REDUCTION_HTML = """
<div style="background:#131313; padding:12px; border-radius:6px; border:1px solid #2d2d2d; color:#fff; font-family:sans-serif;">
    <div style="display:flex; justify-content:space-between; margin-bottom:10px; font-size:12px; gap:10px;">
        <label style="flex:1;">🧬 Target Species:
            <select id="radicalSpecies" style="width:100%; background:#222; color:#fff; border:1px solid #444; padding:2px; border-radius:4px;">
                <option value="hydroxyl">Hydroxyl Radical (•OH)</option>
                <option value="superoxide">Superoxide (•O2-)</option>
                <option value="peroxynitrite">Peroxynitrite (ONOO-)</option>
            </select>
        </label>
        <label style="flex:1;">⚡ Simulation Speed: <span id="speedVal">1.0x</span>
            <input type="range" id="speedSlider" min="5" max="30" value="10" style="width:100%;">
        </label>
    </div>
    <canvas id="reduceCanvas" style="width:100%; height:120px; background:#000; border-radius:4px; display:block;"></canvas>
    <div style="text-align:center; margin-top:8px;">
        <button id="fireBtn" style="width:100%; background:#3399ff; color:#fff; border:none; padding:6px; font-weight:bold; border-radius:4px; cursor:pointer; font-size:11px;">Fire Hydride (H-) Reducing Agent</button>
    </div>
</div>
<script>
    const rCanvas = document.getElementById('reduceCanvas'); const rCtx = rCanvas.getContext('2d');
    const speedSlider = document.getElementById('speedSlider'); const speedVal = document.getElementById('speedVal');
    const speciesSelect = document.getElementById('radicalSpecies'); const fireBtn = document.getElementById('fireBtn');
    
    let electron = null; let radicalColor = '#ff3333';
    function rResize() { rCanvas.width = rCanvas.clientWidth; rCanvas.height = rCanvas.clientHeight; }
    
    fireBtn.onclick = function() {
        if(!electron) { 
            electron = { x: 30, y: rCanvas.height/2 }; 
            radicalColor = '#ff3333'; 
        }
    };
    
    speedSlider.oninput = () => speedVal.innerText = (speedSlider.value / 10).toFixed(1) + 'x';

    window.addEventListener('load', () => {
        rResize();
        function anim() {
            let spd = parseFloat(speedSlider.value) / 10;
            rCtx.clearRect(0,0,rCanvas.width,rCanvas.height);
            
            // Hydride Source
            rCtx.beginPath(); rCtx.arc(30, rCanvas.height/2, 10, 0, Math.PI*2); rCtx.fillStyle = '#00ffff'; rCtx.fill();
            rCtx.fillStyle = '#000'; rCtx.font = 'bold 9px sans-serif'; rCtx.fillText('H-', 25, rCanvas.height/2+3);
            
            // Free Radical Target
            rCtx.beginPath(); rCtx.arc(rCanvas.width-40, rCanvas.height/2, 10, 0, Math.PI*2); rCtx.fillStyle = radicalColor; rCtx.fill();
            rCtx.fillStyle = '#fff'; rCtx.font = '9px sans-serif';
            let label = radicalColor === '#ff3333' ? speciesSelect.value : 'Stable';
            rCtx.fillText(label, rCanvas.width-75, rCanvas.height/2+18);
            
            if(electron) {
                electron.x += 4 * spd;
                rCtx.beginPath(); rCtx.arc(electron.x, electron.y, 3, 0, Math.PI*2); rCtx.fillStyle = '#ffff00'; rCtx.fill();
                if(electron.x >= rCanvas.width-40) { electron = null; radicalColor = '#33cc33'; }
            }
            requestAnimationFrame(anim);
        }
        anim();
    });
</script>
"""

# Animation 3 remains unchanged from the previous setup
HYDRATION_HTML = """
<div style="background:#131313; padding:10px; border-radius:6px; border:1px solid #2d2d2d; color:#fff; font-family:sans-serif;">
    <canvas id="hydrationCanvas" style="width:100%; height:140px; background:#000; border-radius:4px; display:block;"></canvas>
    <div style="text-align:center; margin-top:8px;">
        <button id="hydBtn" style="width:100%; background:#00ccff; color:#000; border:none; padding:6px; font-weight:bold; border-radius:4px; cursor:pointer; font-size:11px;">Activate Microcluster Delivery</button>
    </div>
</div>
<script>
    const hCanvas = document.getElementById('hydrationCanvas'); const hCtx = hCanvas.getContext('2d');
    let waters = []; let isHydrating = false;
    
    function hResize() { hCanvas.width = hCanvas.clientWidth; hCanvas.height = hCanvas.clientHeight; }
    
    class Water {
        constructor() { this.x = Math.random() * 60 + 10; this.y = Math.random() * (hCanvas.height - 20) + 10; }
        update() {
            if(isHydrating) {
                let targetX = hCanvas.width - 40; let targetY = hCanvas.height / 2;
                this.x += (targetX - this.x) * 0.04; this.y += (targetY - this.y) * 0.04;
            }
        }
        draw() { hCtx.beginPath(); hCtx.arc(this.x, this.y, 4, 0, Math.PI*2); hCtx.fillStyle = '#33ccff'; hCtx.fill(); }
    }
    
    window.addEventListener('load', () => {
        hResize(); 
        for(let i=0; i<25; i++) waters.push(new Water());
        
        // FIX: Safely grab and bind the button click ONLY after the DOM layout is completely ready
        const readyHydBtn = document.getElementById('hydBtn');
        if (readyHydBtn) {
            readyHydBtn.onclick = () => { isHydrating = true; };
        }
        
        function anim() {
            hCtx.clearRect(0,0,hCanvas.width,hCanvas.height);
            hCtx.beginPath(); hCtx.arc(hCanvas.width + 20, hCanvas.height/2, 70, 0, Math.PI*2); hCtx.fillStyle = '#333'; hCtx.fill();
            hCtx.lineWidth = 3; hCtx.strokeStyle = '#ff4d4d'; hCtx.stroke();
            hCtx.fillStyle = '#fff'; hCtx.font = '10px sans-serif'; hCtx.fillText('CELL', hCanvas.width-35, hCanvas.height/2+4);
            waters.forEach(w => { w.update(); w.draw(); });
            requestAnimationFrame(anim);
        }
        anim();
    });
</script>
"""
