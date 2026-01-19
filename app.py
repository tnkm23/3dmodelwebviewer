import streamlit as st
import os
from pathlib import Path
import streamlit.components.v1 as components

# ページ設定
st.set_page_config(
    page_title="3D Model Viewer",
    layout="wide"
)

st.title("3D Model Viewer with Three.js")
st.markdown("**Streamlit + Three.js を使用した .glb ファイルビューア**")

# .glb ファイルを検索
def find_glb_files(base_path="./models"):
    """指定されたディレクトリから.glbファイルを検索"""
    glb_files = []
    if os.path.exists(base_path):
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.endswith('.glb'):
                    file_path = os.path.join(root, file)
                    glb_files.append(file_path)
    return glb_files

# サイドバーでファイル選択
st.sidebar.header("モデル選択")

# .glbファイルのリストを取得
models_dir = "./models"
glb_files = find_glb_files(models_dir)

if not glb_files:
    st.sidebar.warning(f"'{models_dir}' ディレクトリに .glb ファイルが見つかりません")
    st.info("""
    ### 使い方
    1. プロジェクトルートに `models` ディレクトリを作成
    2. .glb ファイルを `models` ディレクトリに配置
    3. このアプリをリロード
    """)
    
    # デモ用のサンプルパス表示
    st.sidebar.info("サンプル: ./models/sample.glb")
    selected_file = None
else:
    # ファイル名のみ表示用リストを作成
    file_names = [os.path.basename(f) for f in glb_files]
    
    # ファイル選択
    selected_index = st.sidebar.selectbox(
        "モデルを選択",
        range(len(file_names)),
        format_func=lambda i: file_names[i]
    )
    
    selected_file = glb_files[selected_index]
    
    # 選択されたファイルのパス表示
    st.sidebar.success(f"選択中: {selected_file}")
    
    # ファイル情報表示
    file_size = os.path.getsize(selected_file)
    st.sidebar.metric("ファイルサイズ", f"{file_size / 1024:.2f} KB")

# ビューア設定
st.sidebar.header("ビューア設定")
width = st.sidebar.slider("幅 (px)", 400, 1200, 800)
height = st.sidebar.slider("高さ (px)", 300, 900, 600)
bg_color = st.sidebar.color_picker("背景色", "#1a1a1a")
show_grid = st.sidebar.checkbox("グリッド表示", True)
auto_rotate = st.sidebar.checkbox("自動回転", False)

# ボタン
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🔄 リセットビュー"):
        st.rerun()
with col2:
    if st.button("📷 スクリーンショット", help="右クリックで画像を保存できます"):
        st.info("ビューア上で右クリック → 画像を保存")
with col3:
    if st.button("🔍 リロード"):
        st.rerun()

# Three.jsビューアの埋め込み
if selected_file:
    # ファイルパスをBase64エンコードして埋め込むか、直接パスを使用
    # ここではシンプルにファイルを読み込んでBase64エンコード
    import base64
    
    with open(selected_file, 'rb') as f:
        glb_data = f.read()
        glb_base64 = base64.b64encode(glb_data).decode()
    
    # Three.js + GLTFLoader を使用した3Dビューア
    threejs_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                overflow: hidden;
            }}
            #viewer-container {{
                width: 100%;
                height: 100vh;
            }}
        </style>
    </head>
    <body>
        <div id="viewer-container"></div>
        
        <script type="importmap">
        {{
            "imports": {{
                "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
                "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
            }}
        }}
        </script>
        
        <script type="module">
            import * as THREE from 'three';
            import {{ GLTFLoader }} from 'three/addons/loaders/GLTFLoader.js';
            import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';
            
            // シーン設定
            const container = document.getElementById('viewer-container');
            const scene = new THREE.Scene();
            scene.background = new THREE.Color('{bg_color}');
            
            // カメラ設定
            const camera = new THREE.PerspectiveCamera(
                45,
                {width} / {height},
                0.1,
                1000
            );
            camera.position.set(0, 2, 5);
            
            // レンダラー設定（GPU活用）
            const renderer = new THREE.WebGLRenderer({{
                antialias: true,
                powerPreference: 'high-performance' // GPU優先
            }});
            renderer.setSize({width}, {height});
            renderer.setPixelRatio(window.devicePixelRatio);
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            renderer.outputEncoding = THREE.sRGBEncoding;
            renderer.toneMapping = THREE.ACESFilmicToneMapping;
            renderer.toneMappingExposure = 1.0;
            container.appendChild(renderer.domElement);
            
            // ライト設定
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
            scene.add(ambientLight);
            
            const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
            directionalLight.position.set(5, 10, 5);
            directionalLight.castShadow = true;
            scene.add(directionalLight);
            
            const pointLight = new THREE.PointLight(0xffffff, 0.5);
            pointLight.position.set(-5, 5, -5);
            scene.add(pointLight);
            
            // グリッドヘルパー
            {'const gridHelper = new THREE.GridHelper(10, 10); scene.add(gridHelper);' if show_grid else ''}
            
            // 軸ヘルパー
            const axesHelper = new THREE.AxesHelper(2);
            scene.add(axesHelper);
            
            // コントロール設定
            const controls = new OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.autoRotate = {str(auto_rotate).lower()};
            controls.autoRotateSpeed = 2.0;
            
            // GLTFローダー
            const loader = new GLTFLoader();
            
            // Base64データをBlobに変換
            const glbData = atob('{glb_base64}');
            const glbArray = new Uint8Array(glbData.length);
            for (let i = 0; i < glbData.length; i++) {{
                glbArray[i] = glbData.charCodeAt(i);
            }}
            const glbBlob = new Blob([glbArray], {{ type: 'model/gltf-binary' }});
            const glbUrl = URL.createObjectURL(glbBlob);
            
            // モデルロード
            loader.load(
                glbUrl,
                function(gltf) {{
                    const model = gltf.scene;
                    
                    // モデルのバウンディングボックスを計算してカメラ位置を調整
                    const box = new THREE.Box3().setFromObject(model);
                    const center = box.getCenter(new THREE.Vector3());
                    const size = box.getSize(new THREE.Vector3());
                    const maxDim = Math.max(size.x, size.y, size.z);
                    const fov = camera.fov * (Math.PI / 180);
                    let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2));
                    cameraZ *= 2.5; // オフセット
                    
                    camera.position.set(center.x, center.y + maxDim * 0.5, center.z + cameraZ);
                    camera.lookAt(center);
                    controls.target.copy(center);
                    
                    // シャドウ設定
                    model.traverse((node) => {{
                        if (node.isMesh) {{
                            node.castShadow = true;
                            node.receiveShadow = true;
                        }}
                    }});
                    
                    scene.add(model);
                    console.log('Model loaded successfully');
                }},
                function(xhr) {{
                    console.log((xhr.loaded / xhr.total * 100) + '% loaded');
                }},
                function(error) {{
                    console.error('Error loading model:', error);
                }}
            );
            
            // アニメーションループ
            function animate() {{
                requestAnimationFrame(animate);
                controls.update();
                renderer.render(scene, camera);
            }}
            animate();
            
            // リサイズ対応
            window.addEventListener('resize', () => {{
                camera.aspect = {width} / {height};
                camera.updateProjectionMatrix();
                renderer.setSize({width}, {height});
            }});
        </script>
    </body>
    </html>
    """
    
    # Streamlitにビューアを埋め込み
    st.subheader("3D ビューア")
    components.html(threejs_html, height=height + 20, scrolling=False)
    
    st.markdown("""
    ### 操作方法
    - **左クリック + ドラッグ**: モデルを回転
    - **右クリック + ドラッグ**: カメラ移動
    - **マウスホイール**: ズームイン/アウト
    """)
else:
    st.warning("モデルファイルを選択してください")

# フッター
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <small>Powered by Streamlit + Three.js | GPU加速レンダリング対応</small>
</div>
""", unsafe_allow_html=True)
