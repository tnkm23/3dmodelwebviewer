import streamlit as st
import streamlit.components.v1 as components
import trimesh
import os
import json
from pathlib import Path
from datetime import datetime

# ディレクトリ設定
UPLOAD_DIR = Path("uploaded_files")
GLB_DIR = Path("glb_files")
DB_FILE = Path("file_database.json")

# ディレクトリ作成
UPLOAD_DIR.mkdir(exist_ok=True)
GLB_DIR.mkdir(exist_ok=True)

# 簡易データベース（JSON）初期化
if not DB_FILE.exists():
    with open(DB_FILE, 'w') as f:
        json.dump([], f)

def load_database():
    """データベース読み込み"""
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_to_database(entry):
    """データベースに保存"""
    db = load_database()
    db.append(entry)
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=2)

def convert_stl_to_glb(stl_path, glb_path):
    """STLをGLBに変換"""
    try:
        mesh = trimesh.load(stl_path)
        mesh.export(glb_path)
        return True, "変換成功"
    except Exception as e:
        return False, f"変換エラー: {str(e)}"

def create_threejs_viewer(glb_path):
    """Three.jsビューアーHTML生成"""
    # 相対パスに変換
    glb_relative = glb_path.replace("\\", "/")
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; overflow: hidden; }}
            canvas {{ display: block; }}
            #loading {{ 
                position: absolute; 
                top: 50%; 
                left: 50%; 
                transform: translate(-50%, -50%);
                color: white;
                font-size: 20px;
            }}
        </style>
    </head>
    <body>
        <div id="loading">モデル読み込み中...</div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script>
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0x1a1a2e);
            
            const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(5, 5, 5);
            
            const renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);
            
            // ライト設定
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
            scene.add(ambientLight);
            
            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
            directionalLight.position.set(10, 10, 10);
            scene.add(directionalLight);
            
            // GLBローダー
            const loader = new THREE.GLTFLoader();
            loader.load(
                '{glb_relative}',
                function(gltf) {{
                    const model = gltf.scene;
                    
                    // モデルをセンタリング
                    const box = new THREE.Box3().setFromObject(model);
                    const center = box.getCenter(new THREE.Vector3());
                    model.position.sub(center);
                    
                    // スケール調整
                    const size = box.getSize(new THREE.Vector3());
                    const maxDim = Math.max(size.x, size.y, size.z);
                    const scale = 4 / maxDim;
                    model.scale.multiplyScalar(scale);
                    
                    scene.add(model);
                    document.getElementById('loading').style.display = 'none';
                }},
                function(xhr) {{
                    console.log((xhr.loaded / xhr.total * 100) + '% loaded');
                }},
                function(error) {{
                    console.error('読み込みエラー:', error);
                    document.getElementById('loading').innerText = '読み込み失敗';
                }}
            );
            
            // マウス操作（簡易版）
            let isDragging = false;
            let previousMousePosition = {{ x: 0, y: 0 }};
            
            renderer.domElement.addEventListener('mousedown', () => {{ isDragging = true; }});
            renderer.domElement.addEventListener('mouseup', () => {{ isDragging = false; }});
            renderer.domElement.addEventListener('mousemove', (e) => {{
                if (isDragging) {{
                    const deltaX = e.offsetX - previousMousePosition.x;
                    const deltaY = e.offsetY - previousMousePosition.y;
                    
                    camera.position.x += deltaX * 0.01;
                    camera.position.y -= deltaY * 0.01;
                    camera.lookAt(scene.position);
                }}
                previousMousePosition = {{ x: e.offsetX, y: e.offsetY }};
            }});
            
            // リサイズ対応
            window.addEventListener('resize', () => {{
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            }});
            
            // アニメーション
            function animate() {{
                requestAnimationFrame(animate);
                renderer.render(scene, camera);
            }}
            animate();
        </script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
    </body>
    </html>
    """
    return html

# ========== Streamlit UI ==========
st.set_page_config(page_title="CAD変換・管理システム", layout="wide")
st.title("🔧 CADファイル変換・管理システム")

tab1, tab2 = st.tabs(["📤 ファイルアップロード", "📚 ファイル一覧"])

with tab1:
    st.header("STL/STEPファイルをアップロード")
    
    uploaded_file = st.file_uploader(
        "ファイルを選択 (.stl, .step, .stp)",
        type=['stl', 'step', 'stp']
    )
    
    if uploaded_file:
        file_ext = uploaded_file.name.split('.')[-1].lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = uploaded_file.name.rsplit('.', 1)[0]
        
        # ファイル保存
        original_path = UPLOAD_DIR / f"{timestamp}_{uploaded_file.name}"
        with open(original_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"✅ アップロード完了: {uploaded_file.name}")
        
        # 変換処理
        with st.spinner("GLBに変換中..."):
            glb_filename = f"{timestamp}_{base_name}.glb"
            glb_path = GLB_DIR / glb_filename
            
            if file_ext == 'stl':
                success, message = convert_stl_to_glb(str(original_path), str(glb_path))
            else:  # step/stp
                st.warning("⚠️ STEP変換は次のステップで実装します（現在はSTLのみ対応）")
                success = False
                message = "STEP変換未実装"
            
            if success:
                st.success(f"✅ {message}")
                
                # データベースに登録
                entry = {
                    "id": timestamp,
                    "original_name": uploaded_file.name,
                    "original_path": str(original_path),
                    "glb_path": str(glb_path),
                    "file_type": file_ext,
                    "upload_date": datetime.now().isoformat()
                }
                save_to_database(entry)
                
                # プレビュー表示
                st.subheader("🎨 3Dプレビュー")
                viewer_html = create_threejs_viewer(str(glb_path))
                components.html(viewer_html, height=600)
                
                # ダウンロードボタン
                col1, col2 = st.columns(2)
                with col1:
                    with open(original_path, 'rb') as f:
                        st.download_button(
                            label=f"📥 元ファイルをダウンロード ({file_ext.upper()})",
                            data=f,
                            file_name=uploaded_file.name,
                            mime="application/octet-stream"
                        )
                with col2:
                    with open(glb_path, 'rb') as f:
                        st.download_button(
                            label="📥 GLBをダウンロード",
                            data=f,
                            file_name=glb_filename,
                            mime="model/gltf-binary"
                        )
            else:
                st.error(f"❌ {message}")

with tab2:
    st.header("📚 登録済みファイル一覧")
    
    db = load_database()
    
    if not db:
        st.info("まだファイルが登録されていません")
    else:
        for entry in reversed(db):  # 新しい順
            with st.expander(f"📄 {entry['original_name']} ({entry['upload_date'][:10]})"):
                st.write(f"**ファイル形式**: {entry['file_type'].upper()}")
                st.write(f"**アップロード日時**: {entry['upload_date']}")
                
                # プレビュー
                if os.path.exists(entry['glb_path']):
                    viewer_html = create_threejs_viewer(entry['glb_path'])
                    components.html(viewer_html, height=400)
                    
                    # ダウンロード
                    col1, col2 = st.columns(2)
                    with col1:
                        if os.path.exists(entry['original_path']):
                            with open(entry['original_path'], 'rb') as f:
                                st.download_button(
                                    label=f"📥 {entry['file_type'].upper()}",
                                    data=f,
                                    file_name=entry['original_name'],
                                    key=f"dl_orig_{entry['id']}"
                                )
                    with col2:
                        with open(entry['glb_path'], 'rb') as f:
                            st.download_button(
                                label="📥 GLB",
                                data=f,
                                file_name=os.path.basename(entry['glb_path']),
                                key=f"dl_glb_{entry['id']}"
                            )
                else:
                    st.warning("GLBファイルが見つかりません")