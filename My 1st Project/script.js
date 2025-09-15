document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('ant-canvas');
    const ctx = canvas.getContext('2d');
    const startButton = document.getElementById('start-simulation');
    
    let ants = [];
    let food = [];
    let animationId;
    let simulationRunning = false;
    
    // Create food sources
    function createFood() {
        food = [];
        for (let i = 0; i < 5; i++) {
            food.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                size: 10 + Math.random() * 10,
                amount: 100
            });
        }
    }
    
    // Create an ant colony
    function createAnts() {
        ants = [];
        const nestX = canvas.width / 2;
        const nestY = canvas.height / 2;
        
        for (let i = 0; i < 50; i++) {
            const angle = Math.random() * Math.PI * 2;
            ants.push({
                x: nestX,
                y: nestY,
                speed: 1 + Math.random() * 0.5,
                direction: angle,
                hasFood: false,
                wanderCounter: 0,
                turnSpeed: 0.1,
                color: '#8B4513',
                pheromones: []
            });
        }
    }
    
    // Reset canvas
    function clearCanvas() {
        ctx.fillStyle = '#fff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }
    
    // Draw nest
    function drawNest() {
        ctx.fillStyle = '#D2B48C';
        ctx.beginPath();
        ctx.arc(canvas.width / 2, canvas.height / 2, 20, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#A0522D';
        ctx.beginPath();
        ctx.arc(canvas.width / 2, canvas.height / 2, 10, 0, Math.PI * 2);
        ctx.fill();
    }
    
    // Draw food sources
    function drawFood() {
        food.forEach(f => {
            if (f.amount > 0) {
                const alpha = f.amount / 100;
                ctx.fillStyle = `rgba(0, 128, 0, ${alpha})`;
                ctx.beginPath();
                ctx.arc(f.x, f.y, f.size, 0, Math.PI * 2);
                ctx.fill();
            }
        });
    }
    
    // Draw all ants
    function drawAnts() {
        ants.forEach(ant => {
            ctx.save();
            ctx.translate(ant.x, ant.y);
            ctx.rotate(ant.direction);
            
            // Draw ant body
            ctx.fillStyle = ant.hasFood ? '#CD853F' : ant.color;
            ctx.beginPath();
            ctx.ellipse(0, 0, 4, 2, 0, 0, Math.PI * 2);
            ctx.fill();
            
            // Draw ant head
            ctx.beginPath();
            ctx.arc(5, 0, 2, 0, Math.PI * 2);
            ctx.fill();
            
            // Draw legs
            ctx.strokeStyle = ant.color;
            ctx.lineWidth = 0.5;
            
            // Left legs
            ctx.beginPath();
            ctx.moveTo(0, -1);
            ctx.lineTo(-3, -5);
            ctx.moveTo(0, -1);
            ctx.lineTo(0, -5);
            ctx.moveTo(0, -1);
            ctx.lineTo(3, -5);
            
            // Right legs
            ctx.moveTo(0, 1);
            ctx.lineTo(-3, 5);
            ctx.moveTo(0, 1);
            ctx.lineTo(0, 5);
            ctx.moveTo(0, 1);
            ctx.lineTo(3, 5);
            ctx.stroke();
            
            // Draw food if ant has it
            if (ant.hasFood) {
                ctx.fillStyle = 'green';
                ctx.beginPath();
                ctx.arc(-3, 0, 1.5, 0, Math.PI * 2);
                ctx.fill();
            }
            
            ctx.restore();
        });
    }
    
    // Draw pheromones
    function drawPheromones() {
        ants.forEach(ant => {
            ant.pheromones.forEach(p => {
                const alpha = p.strength / 100;
                ctx.fillStyle = p.type === 'food' ? `rgba(0, 255, 0, ${alpha})` : `rgba(255, 0, 0, ${alpha})`;
                ctx.beginPath();
                ctx.arc(p.x, p.y, 1, 0, Math.PI * 2);
                ctx.fill();
            });
        });
    }
    
    // Update ant position and behavior
    function updateAnts() {
        const nestX = canvas.width / 2;
        const nestY = canvas.height / 2;
        
        ants.forEach(ant => {
            // Leave pheromones occasionally
            if (Math.random() < 0.05) {
                ant.pheromones.push({
                    x: ant.x,
                    y: ant.y,
                    type: ant.hasFood ? 'food' : 'home',
                    strength: 100
                });
                
                // Limit pheromones per ant
                if (ant.pheromones.length > 30) {
                    ant.pheromones.shift();
                }
            }
            
            // Fade pheromones
            ant.pheromones.forEach(p => {
                p.strength -= 0.5;
            });
            ant.pheromones = ant.pheromones.filter(p => p.strength > 0);
            
            // Move ant
            ant.x += Math.cos(ant.direction) * ant.speed;
            ant.y += Math.sin(ant.direction) * ant.speed;
            
            // Boundary check
            if (ant.x < 0) ant.x = 0;
            if (ant.y < 0) ant.y = 0;
            if (ant.x > canvas.width) ant.x = canvas.width;
            if (ant.y > canvas.height) ant.y = canvas.height;
            
            // Random wandering
            ant.wanderCounter += 1;
            if (ant.wanderCounter > 20) {
                ant.direction += (Math.random() - 0.5) * ant.turnSpeed;
                ant.wanderCounter = 0;
            }
            
            // Check if ant found food
            if (!ant.hasFood) {
                food.forEach(f => {
                    if (f.amount > 0 && Math.hypot(ant.x - f.x, ant.y - f.y) < f.size) {
                        ant.hasFood = true;
                        f.amount -= 1;
                        ant.direction += Math.PI; // Turn around
                    }
                });
            }
            
            // Return to nest with food
            if (ant.hasFood) {
                // Check if ant reached nest
                if (Math.hypot(ant.x - nestX, ant.y - nestY) < 20) {
                    ant.hasFood = false;
                    ant.direction += Math.PI; // Turn around
                }
                
                // Gradually turn toward nest
                const angleToNest = Math.atan2(nestY - ant.y, nestX - ant.x);
                let angleDiff = angleToNest - ant.direction;
                
                // Normalize angle difference
                if (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
                if (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
                
                ant.direction += angleDiff * 0.05;
            }
        });
    }
    
    // Main simulation loop
    function simulate() {
        clearCanvas();
        drawPheromones();
        drawFood();
        drawNest();
        updateAnts();
        drawAnts();
        
        if (simulationRunning) {
            animationId = requestAnimationFrame(simulate);
        }
    }
    
    // Event listeners
    startButton.addEventListener('click', () => {
        if (!simulationRunning) {
            simulationRunning = true;
            createFood();
            createAnts();
            startButton.textContent = 'Stop Simulation';
            simulate();
        } else {
            simulationRunning = false;
            cancelAnimationFrame(animationId);
            startButton.textContent = 'Start Simulation';
        }
    });
    
    // Initial setup - just draw the empty canvas
    clearCanvas();
});