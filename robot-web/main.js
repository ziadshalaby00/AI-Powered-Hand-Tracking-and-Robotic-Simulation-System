import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById("scene"), antialias: true });

renderer.setSize(window.innerWidth, window.innerHeight);
camera.position.z = 5;

scene.add(new THREE.AmbientLight(0xffffff, 0.5));
const light = new THREE.DirectionalLight(0xffffff, 1);
light.position.set(2, 2, 5);
scene.add(light);

let robot;
const loader = new GLTFLoader();
let upperArmR, forearmR, handR;
loader.load("./source/sin_nombre1.glb", (gltf) => {
    robot = gltf.scene;
    const box = new THREE.Box3().setFromObject(robot);
    const center = box.getCenter(new THREE.Vector3());
    robot.scale.set(0.5, 0.5, 0.5);
    robot.position.sub(center);
    robot.position.y += -1;

    robot.traverse((child) => {
        if (child.isBone) {
            if (child.name === "upper_armR") upperArmR = child;
            if (child.name === "forearmR") forearmR = child;
            if (child.name === "handR") handR = child;
        }
    });

    scene.add(robot);
});


function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}
animate();


const socket = new WebSocket("ws://localhost:8765");

socket.onopen = () => {
    console.log("Connected to WebSocket Server ✔️");
};

socket.onerror = (error) => {
    console.error("WebSocket Error ❌:", error);
};

socket.onclose = () => {
    console.log("Disconnected from Server ⚠️");
};

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);

    console.log(data)

    if (upperArmR && forearmR) {
        upperArmR.rotation.z = (data.hand_y - 0.5) * 2; 
        upperArmR.rotation.y = -(data.hand_x - 0.5) * 2;

        forearmR.rotation.z = (data.hand_y - 0.5) * 1.5;

        handR.rotation.x = (data.hand_x - 0.5) * 1.5;
    }
};