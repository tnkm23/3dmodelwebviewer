import streamlit as st
import streamlit.components.v1 as components

st.title("Three.js Box in Streamlit")
st.write("Streamlit + Three.jsでボックスジオメトリを描画")

# Three.jsのHTMLコード
threejs_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; }
        canvas { display: block; }
    </style>
</head>
<body>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        // シーン、カメラ、レンダラーの設定
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x1a1a2e);
        
        const camera = new THREE.PerspectiveCamera(
            75,
            window.innerWidth / window.innerHeight,
            0.1,
            1000
        );
        camera.position.z = 5;
        
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);
        
        // ボックスジオメトリの作成
        const geometry = new THREE.BoxGeometry(2, 2, 2);
        const material = new THREE.MeshStandardMaterial({
            color: 0x00ffff,
            metalness: 0.5,
            roughness: 0.3
        });
        const cube = new THREE.Mesh(geometry, material);
        scene.add(cube);
        
        // ライトの追加
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        scene.add(ambientLight);
        
        const pointLight = new THREE.PointLight(0xffffff, 1);
        pointLight.position.set(5, 5, 5);
        scene.add(pointLight);
        
        // リサイズ対応
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
        
        // アニメーションループ
        function animate() {
            requestAnimationFrame(animate);
            
            // ボックスを回転
            cube.rotation.x += 0.01;
            cube.rotation.y += 0.01;
            
            renderer.render(scene, camera);
        }
        
        animate();
    </script>
</body>
</html>
"""

# Streamlitに埋め込み
components.html(threejs_html, height=600)

st.write("✅ Three.jsがブラウザのGPUを使用して描画しています")
st.write("次のステップ: `.glb`ファイルの読み込みに進みます")