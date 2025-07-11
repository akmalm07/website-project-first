  document.addEventListener('DOMContentLoaded', function() {
    const scene = document.getElementById('vault-scene');
  
    if (scene) {
        setTimeout(() => {
            scene.classList.add('fade-out');
        }, 6000);
    } else {
        console.warn('intro-scene element not found');
    }
});