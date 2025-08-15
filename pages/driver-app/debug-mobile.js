// Mobile debug helper
function debugMobile() {
    const debugInfo = {
        userAgent: navigator.userAgent,
        viewport: {
            width: window.innerWidth,
            height: window.innerHeight,
            orientation: window.orientation
        },
        touch: 'ontouchstart' in window,
        pointer: 'onpointerdown' in window
    };
    
    // Create debug panel
    const panel = document.createElement('div');
    panel.style.cssText = `
        position: fixed;
        top: 10px;
        right: 10px;
        background: rgba(0,0,0,0.8);
        color: white;
        padding: 10px;
        font-size: 12px;
        z-index: 9999;
        max-width: 200px;
    `;
    panel.innerHTML = `
        <div>Debug Info:</div>
        <div>Width: ${debugInfo.viewport.width}</div>
        <div>Height: ${debugInfo.viewport.height}</div>
        <div>Touch: ${debugInfo.touch}</div>
        <div>UA: ${debugInfo.userAgent.substring(0, 50)}...</div>
    `;
    document.body.appendChild(panel);
    
    // Log navigation events
    document.addEventListener('click', (e) => {
        console.log('Click event:', e.target);
    }, true);
    
    document.addEventListener('touchstart', (e) => {
        console.log('Touch start:', e.target);
    }, true);
    
    document.addEventListener('touchend', (e) => {
        console.log('Touch end:', e.target);
    }, true);
}

// Auto-run on mobile
if (/Android|iPhone|iPad/i.test(navigator.userAgent)) {
    debugMobile();
}