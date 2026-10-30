# genealogy.py
import streamlit as st
import streamlit.components.v1 as components

def get_downlines_recursive(db, root_email, visited=None):
    """Recursively fetches all downlines for a given node to display complete downline branches."""
    if visited is None:
        visited = set()
    
    downlines = []
    if root_email in visited:
        return downlines
    visited.add(root_email)
    
    try:
        docs = db.collection("users").where("upline", "==", root_email).stream()
        for doc in docs:
            data = doc.to_dict()
            email = data.get("email", "").strip().lower()
            if email:
                # Recursive call to gather nested layers
                children = get_downlines_recursive(db, email, visited)
                downlines.append({
                    "name": data.get("name", "Unknown Node"),
                    "email": email,
                    "children": children
                })
    except Exception:
        pass
    return downlines

def get_upline_chain(db, start_email):
    """Linearly traces upward parent connections to the ultimate root element."""
    chain = []
    current_email = start_email.strip().lower()
    visited = set()
    
    while current_email and current_email not in visited:
        visited.add(current_email)
        try:
            doc = db.collection("users").document(current_email).get()
            if not doc.exists:
                break
            data = doc.to_dict()
            chain.append({
                "name": data.get("name", "Unknown Node"),
                "email": current_email
            })
            # Move up to next parent node
            current_email = data.get("upline", "").strip().lower()
        except Exception:
            break
    return chain

def build_tree_data(db, view_mode, session_email):
    """Assembles the correct structural tree mapping based on the selected viewing mode."""
    session_email = session_email.strip().lower()
    
    # Mode A: Only downlines originating from the logged-in user node
    if view_mode == "⬇️ Downline Branch View":
        try:
            root_doc = db.collection("users").document(session_email).get()
            root_name = root_doc.to_dict().get("name", "Me") if root_doc.exists else "Me"
        except Exception:
            root_name = "Me"
            
        return {
            "name": root_name,
            "email": session_email,
            "children": get_downlines_recursive(db, session_email)
        }
        
    # Mode B: Linear path going upward to the root matrix supervisor
    elif view_mode == "⬆️ Upward Lineage View":
        chain = get_upline_chain(db, session_email)
        if not chain:
            return {"name": "No Node Found", "email": session_email, "children": []}
            
        # Reverse structural layout so the highest ancestor is drawn at the top
        root_node = {"name": chain[-1]["name"], "email": chain[-1]["email"], "children": []}
        current_tier = root_node
        
        for parent in reversed(chain[:-1]):
            new_node = {"name": parent["name"], "email": parent["email"], "children": []}
            current_tier["children"].append(new_node)
            current_tier = new_node
        return root_node

    # Mode C: Complete system mapping starting from a common root administrative node
    else:
        try:
            # Look for an entry with no upline to serve as the global system origin
            root_query = db.collection("users").where("upline", "==", None).limit(1).stream()
            root_docs = list(root_query)
            if not root_docs:
                root_query = db.collection("users").where("upline", "==", "").limit(1).stream()
                root_docs = list(root_query)
                
            if root_docs:
                r_data = root_docs[0].to_dict()
                r_email = r_data.get("email", "").strip().lower()
                return {
                    "name": r_data.get("name", "System Root"),
                    "email": r_email,
                    "children": get_downlines_recursive(db, r_email)
                }
        except Exception:
            pass
        return {"name": "Empty Registry", "email": "", "children": []}

def render_genealogy_tree(db, session_email):
    """Renders the dropdown selectors and the canvas component tree inside Streamlit."""
    st.subheader("🌲 Dynamic Affiliate Tree Visualizer")
    
    # 3 View Selection Options Provided Cleanly to User
    view_option = st.selectbox(
        "Select Network Perspective Frame:",
        [
            "⬇️ Downline Branch View",
            "⬆️ Upward Lineage View",
            "🌐 Complete Global Tree Map"
        ]
    )
    
    # Build tree structural data dynamically
    tree_data = build_tree_data(db, view_option, session_email)
    
    import json
    json_tree = json.dumps(tree_data)
    
    # HTML5 Canvas Tree Rendering Code Logic - Braces doubled to prevent f-string errors
    html_canvas = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                margin: 0; background-color: #0b0f19; color: #ffffff;
                font-family: system-ui, -apple-system, sans-serif; overflow: hidden;
            }}
            #canvas-wrap {{
                position: relative; width: 100%; height: 500px;
                border: 1px solid #1e293b; border-radius: 8px; background: #0f172a;
            }}
            canvas {{ display: block; width: 100%; height: 100%; }}
        </style>
    </head>
    <body>
    <div id="canvas-wrap">
        <canvas id="treeCanvas"></canvas>
    </div>
    <script>
        const treeData = {json_tree};
        const canvas = document.getElementById('treeCanvas');
        const ctx = canvas.getContext('2d');
        
        let width = canvas.width = canvas.offsetWidth;
        let height = canvas.height = canvas.offsetHeight;

        // Structured Layout Logic computing leaf placements linearly
        function computeLayout(node, depth, xOffset) {{
            node.depth = depth;
            if (!node.children || node.children.length === 0) {{
                node.x = xOffset.val;
                xOffset.val += 140; 
                return;
            }}
            node.children.forEach(child => computeLayout(child, depth + 1, xOffset));
            
            // Parent nodes center perfectly above their children nodes
            let sumX = 0;
            node.children.forEach(child => sumX += child.x);
            node.x = sumX / node.children.length;
        }}

        function drawConnections(node) {{
            if (!node.children) return;
            node.children.forEach(child => {{
                ctx.beginPath();
                ctx.moveTo(node.x, node.depth * 90 + 50);
                ctx.lineTo(child.x, child.depth * 90 + 50);
                ctx.strokeStyle = '#334155';
                ctx.lineWidth = 2;
                ctx.stroke();
                drawConnections(child);
            }});
        }}

        function drawNodes(node) {{
            const y = node.depth * 90 + 50;
            
            // Node background block glow styling parameters
            ctx.beginPath();
            ctx.arc(node.x, y, 22, 0, Math.PI * 2);
            ctx.fillStyle = '#1e293b';
            ctx.strokeStyle = '#38bdf8';
            ctx.lineWidth = 2;
            ctx.fill();
            ctx.stroke();
            
            // Text Label Layout Render Elements
            ctx.fillStyle = '#f8fafc';
            ctx.font = 'bold 11px sans-serif';
            ctx.textAlign = 'center';
            let shortName = node.name.length > 12 ? node.name.substring(0,10)+'..' : node.name;
            ctx.fillText(shortName, node.x, y + 4);
            
            ctx.fillStyle = '#94a3b8';
            ctx.font = '9px sans-serif';
            let shortEmail = node.email.length > 16 ? node.email.substring(0,14)+'..' : node.email;
            ctx.fillText(shortEmail, node.x, y + 36);

            if (node.children) {{
                node.children.forEach(child => drawNodes(child));
            }}
        }}

        function initTree() {{
            let xOffset = {{ val: 70 }};
            computeLayout(treeData, 0, xOffset);
            
            // Center viewport shifting computations
            let minX = Infinity, maxX = -Infinity;
            function findBounds(n) {{
                if (n.x < minX) minX = n.x;
                if (n.x > maxX) maxX = n.x;
                if (n.children) n.children.forEach(findBounds);
            }}
            findBounds(treeData);
            
            let treeWidth = maxX - minX;
            let shiftX = (width - treeWidth) / 2 - minX;
            
            function applyShift(n) {{
                n.x += shiftX;
                if (n.children) n.children.forEach(applyShift);
            }}
            if(treeWidth > 0 && treeWidth < width) applyShift(treeData);

            ctx.clearRect(0, 0, width, height);
            drawConnections(treeData);
            drawNodes(treeData);
        }}

        window.onload = initTree;
    </script>
    </body>
    </html>
    """
    components.html(html_canvas, height=520)
