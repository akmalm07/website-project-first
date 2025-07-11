
  document.addEventListener('DOMContentLoaded', function() {
    const scene = document.getElementById('intro-scene');
  
    if (scene) {
        setTimeout(() => {
            scene.classList.add('fade-out');
        }, 1000);
    } else {
        console.warn('intro-scene element not found');
    }
});