import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById("scene"), antialias: true });

renderer.setSize(window.innerWidth, window.innerHeight);
camera.position.set(0, 1, 5);

scene.add(new THREE.AmbientLight(0xffffff, 0.8));
const light = new THREE.DirectionalLight(0xffffff, 1);
light.position.set(2, 5, 5);
scene.add(light);

let robot;
let mixer;
let animations = {}; 
let currentActionName = '';
const clock = new THREE.Clock();
const loader = new GLTFLoader();

const animationFiles = [
    { name: 'run', url: './source/Fast Run.glb' },
    { name: 'punch', url: './source/Punching Bag.glb' }, 
    { name: 'dance', url: './source/Rumba Dancing.glb' }, 
    { name: 'sit', url: './source/Sitting.glb' }, 
    { name: 'walk-left', url: './source/Walk Strafe Left.glb' }, 
    { name: 'walk-right', url: './source/Walk Strafe right.glb' }, 
    { name: 'Walking', url: './source/Walking.glb' }, 
];

loader.load("./source/sin_nombre1.glb", (gltf) => {
    robot = gltf.scene;
    
    const box = new THREE.Box3().setFromObject(robot);
    const center = box.getCenter(new THREE.Vector3());
    robot.scale.set(0.5, 0.5, 0.5);
    robot.position.sub(center);
    robot.position.y = -1; 

    scene.add(robot);

    mixer = new THREE.AnimationMixer(robot);

    const loadPromises = animationFiles.map(file => {
        return new Promise((resolve) => {
            loader.load(file.url, (animGltf) => {
                if (animGltf.animations && animGltf.animations.length > 0) {
                    const clip = animGltf.animations[0];
                    const action = mixer.clipAction(clip);
                    animations[file.name] = action;
                }
                resolve();
            }, undefined, (error) => {
                console.error(`Error loading: ${file.url}`, error);
                resolve();
            });
        });
    });

    Promise.all(loadPromises).then(async () => {

    });
});

function playAction(name) {
    if (currentActionName === name || !animations[name]) return;

    const newAction = animations[name];
    const oldAction = animations[currentActionName];

    newAction.reset();
    newAction.enabled = true;
    newAction.setEffectiveTimeScale(1);
    newAction.setEffectiveWeight(1);

    if (oldAction) {
        newAction.crossFadeFrom(oldAction, 0, true);
    }
    
    newAction.play();
    currentActionName = name;
}

function idleRobot() {
    Object.values(animations).forEach(action => action.fadeOut(0.5));
    currentActionName = '';
}

function animate() {
    requestAnimationFrame(animate);

    const delta = clock.getDelta();

    if (mixer) {
        mixer.update(delta);
    }

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
    playAction(data)
};

// Data Type
// ['walk-right', 'Walking', 'dance', 'sit', 'punch', 'walk-left', 'run']