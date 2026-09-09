
function runCanvas() {
    // window.onload = function() {
    
        
        console.log('Lets go canvas!');
    
        // setup
        const canvas = document.getElementById('canvas1');
        const ctx = canvas.getContext('2d');
    
    
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    
        console.log(ctx);
        const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
        gradient.addColorStop(0, '#FF0000');     // Red
        gradient.addColorStop(0.08, '#FF3300');  // Orange
        gradient.addColorStop(0.16, '#FF6600');  // Orange
        gradient.addColorStop(0.24, '#FF9900');  // Orange
        gradient.addColorStop(0.32, '#FF66FF');  // Pink
        gradient.addColorStop(0.40, '#FF33FF');  // Magenta
        gradient.addColorStop(0.48, '#CC33FF');  // Purple
        gradient.addColorStop(0.56, '#9933FF');  // Darker Purple
        gradient.addColorStop(0.64, '#6633FF');  // Dark Blue
        gradient.addColorStop(0.72, '#3366FF');  // Blue
        gradient.addColorStop(0.80, '#0099FF');  // Light Blue
        gradient.addColorStop(0.85, '#00CCFF');  // Cyan
        gradient.addColorStop(0.90, '#00FFFF');  // Bright Cyan
        gradient.addColorStop(0.95, '#66FFFF');  // Lighter Cyan
        gradient.addColorStop(1, '#CCFFFF');     // Very Light Cyan
        ctx.fillStyle = gradient;
        ctx.strokeStyle = 'white';
        
        
        
    
        class Particle {
            constructor(effect){
                this.effect = effect;
                this.radius = Math.floor(Math.random() * 10 + 1);
                this.x = this.radius + Math.random() * (this.effect.width - this.radius * 2);
                this.y = this.radius + Math.random() * (this.effect.height - this.radius * 2);
                this.vx = Math.random() * 1 - 0.5;
                this.vy = Math.random() * 1 - 0.5;
                this.pushX = 0;
                this.pushY = 0;
                this.friction = 0.95;
            }
            draw(context){
                context.beginPath();
                context.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                context.fill();
                //context.stroke();
            }
            update(){
                if (this.effect.mouse.pressed){
                    const dx = this.x - this.effect.mouse.x;
                    const dy = this.y - this.effect.mouse.y;
                    const distance = Math.hypot(dx, dy);
                    const force = (this.effect.mouse.radius / distance);
                    if (distance < this.effect.mouse.radius){
                        const angle = Math.atan2(dy, dx);
                        this.pushX += Math.cos(angle) * force;
                        this.pushY += Math.sin(angle) * force;
                    }
                }
    
                this.x += (this.pushX *= this.friction) + this.vx;
                this.y += (this.pushY *= this.friction) + this.vy;
    
                if (this.x < this.radius){
                    this.x = this.radius;
                    this.vx *= -1;
                } else if (this.x > this.effect.width - this.radius){
                    this.x = this.effect.width - this.radius;
                    this.vx *= -1;
                }
                if (this.y < this.radius){
                    this.y = this.radius;
                    this.vy *= -1;
                } else if (this.y > this.effect.height - this.radius){
                    this.y = this.effect.height - this.radius;
                    this.vy *= -1;
                }
            }
            reset(){
                this.x = this.radius + Math.random() * (this.effect.width - this.radius * 2);
                this.y = this.radius + Math.random() * (this.effect.height - this.radius * 2);
            }
        }
    
        class Effect {
            constructor(canvas, context){
                this.canvas = canvas;
                this.context = context;
                this.width = this.canvas.width;
                this.height = this.canvas.height;
                this.particles = [];
                this.numberOfParticles = 400;
                this.createParticles();
    
                this.mouse = {
                    x: 0,
                    y: 0,
                    pressed: false,
                    radius: 200
                }
    
                window.addEventListener('resize', e => {
                    this.resize(e.target.window.innerWidth, e.target.window.innerHeight);
                });
                window.addEventListener('mousemove', e => {
                    if (this.mouse.pressed){
                        this.mouse.x = e.x;
                        this.mouse.y = e.y;
                    }
                });
                window.addEventListener('mousedown', e => {
                    this.mouse.pressed = true;
                    this.mouse.x = e.x;
                    this.mouse.y = e.y;
                });
                window.addEventListener('mouseup', e => {
                    this.mouse.pressed = false;
                });
            }
            createParticles(){
                for (let i = 0; i < this.numberOfParticles; i++){
                    this.particles.push(new Particle(this));
                }
            }
            handleParticles(context){
                this.connectParticles(context);
                this.particles.forEach(particle => {
                    particle.draw(context);
                    particle.update();
                });
            }
            connectParticles(context){
                const maxDistance = 80;
                for (let a = 0; a < this.particles.length; a++){
                    for (let b = a; b < this.particles.length; b++){
                        const dx = this.particles[a].x - this.particles[b].x;
                        const dy = this.particles[a].y - this.particles[b].y;
                        const distance = Math.hypot(dx, dy);
                        if (distance < maxDistance){
                            context.save();
                            const opacity = 1 - (distance/maxDistance);
                            context.globalAlpha = opacity;
                            context.beginPath();
                            context.moveTo(this.particles[a].x, this.particles[a].y);
                            context.lineTo(this.particles[b].x, this.particles[b].y);
                            context.stroke();
                            context.restore();
                        }
                    }
                }
            }
            resize(width, height){
                this.canvas.width = width;
                this.canvas.height = height;
                this.width = width;
                this.height = height;
                const gradient = this.context.createLinearGradient(0,0, width, height);
                gradient.addColorStop(0, 'white');
                gradient.addColorStop(0.5, 'gold');
                gradient.addColorStop(1, 'orangered');
                this.context.fillStyle = gradient;
                this.context.strokeStyle = 'white';
                this.particles.forEach(particle => {
                    particle.reset();
                });
            }
        }
        const effect = new Effect(canvas, ctx);
    
        function animate(){
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            effect.handleParticles(ctx);
            requestAnimationFrame(animate);
        }
        animate();
    
    
        const angle = 20;
        const rotateCard = window;
        
        const lerp = (start, end, amount) => {
            return (1 - amount) * start + amount * end;
        };
        
        const remap = (value, oldMax, newMax) => {
            const newValue = ((value + oldMax) * (newMax * 2)) / (oldMax * 2) - newMax;
            return Math.min(Math.max(newValue, -newMax), newMax);
        };
        
            const cards = document.querySelectorAll(".card");
            cards.forEach((e) => {		
                e.addEventListener("mousemove", (event) => {
                    const rect = e.getBoundingClientRect();
                    const centerX = (rect.left + rect.right) / 2;
                    const centerY = (rect.top + rect.bottom) / 2;
                    const posX = event.pageX - centerX;
                    const posY = event.pageY - centerY;
                    const x = remap(posX, rect.width / 2, angle);
                    const y = remap(posY, rect.height / 2, angle);
                    e.dataset.rotateX = x;
                    e.dataset.rotateY = -y;
                });
                
                e.addEventListener("mouseout", (event) => {
                    e.dataset.rotateX = 0;
                    e.dataset.rotateY = 0;
                });
            });
            
            const update = () => {
                cards.forEach((e) => {
                    let currentX = parseFloat(e.style.getPropertyValue('--rotateY').slice(0, -1));
                    let currentY = parseFloat(e.style.getPropertyValue('--rotateX').slice(0, -1));
                    if (isNaN(currentX)) currentX = 0;
                    if (isNaN(currentY)) currentY = 0;
                    const x = lerp(currentX, e.dataset.rotateX, 0.05);
                    const y = lerp(currentY, e.dataset.rotateY, 0.05);
                    e.style.setProperty("--rotateY", x + "deg");
                    e.style.setProperty("--rotateX", y + "deg");
                })
            }
            setInterval (update,1000/60)
        
    }