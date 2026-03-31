/**
 * Periodiek Systeembeheer v4.5 "Whitelabel & Animation Engine"
 * "Ultra Visual" Animation Engine (GSAP powered)
 */

document.addEventListener('DOMContentLoaded', () => {
    initAnimations();
});

// HTMX Sync: Re-apply to injected content
document.body.addEventListener('htmx:afterSwap', (evt) => {
    initAnimations(evt.detail.elt);
});

function initAnimations(container = document) {
    // 1. Staggered Page Load for .glass-card
    const cards = container.querySelectorAll('.glass-card:not(.ani-init)');
    if (cards.length > 0) {
        gsap.from(cards, {
            duration: 0.8,
            y: 40,
            opacity: 0,
            stagger: {
                amount: 0.4,
                from: "start"
            },
            ease: "expo.out",
            onComplete: () => {
                cards.forEach(c => c.classList.add('ani-init'));
            }
        });
    }

    // 2. Magnetic Buttons (.btn-ultra, .nav-link)
    const magneticElements = container.querySelectorAll('.btn-ultra:not(.mag-init), .nav-link:not(.mag-init)');
    
    magneticElements.forEach(el => {
        el.classList.add('mag-init');
        el.addEventListener('mousemove', (e) => {
            const rect = el.getBoundingClientRect();
            const x = (e.clientX - rect.left - rect.width / 2) * 0.4;
            const y = (e.clientY - rect.top - rect.height / 2) * 0.4;
            
            gsap.to(el, {
                duration: 0.3,
                x: x,
                y: y,
                scale: 1.05,
                ease: "power2.out"
            });
        });
        
        el.addEventListener('mouseleave', () => {
            gsap.to(el, {
                duration: 0.6,
                x: 0,
                y: 0,
                scale: 1,
                ease: "elastic.out(1, 0.4)"
            });
        });
    });

    // 3. Interactive Rips (Liquid Pulse on click)
    const pulseElements = container.querySelectorAll('.btn-ultra:not(.pulse-init), button:not(.pulse-init), .nav-link:not(.pulse-init)');
    
    pulseElements.forEach(el => {
        el.classList.add('pulse-init');
        el.addEventListener('mousedown', () => {
            gsap.to(el, {
                scale: 0.92,
                duration: 0.1,
                ease: "power2.inOut"
            });
        });
        
        el.addEventListener('mouseup', () => {
            gsap.to(el, {
                scale: 1,
                duration: 0.5,
                ease: "elastic.out(1.2, 0.5)"
            });
        });
        
        el.addEventListener('mouseleave', () => {
            gsap.to(el, {
                scale: 1,
                duration: 0.5,
                ease: "power2.out"
            });
        });
    });
}
