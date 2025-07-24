const lenderInfo = document.getElementById('lenderInfo');
const lenders = document.querySelectorAll('.lender');
const infoData = {
    lendeavor: "<h2>Lendeavor</h2><p>Lendeavor is a financing platform that partners with various lenders to provide smart funding options for your practice.</p>",
    iou: "<h2>IOU</h2><p>IOU offers merchant cash advances and flexible business financing options for your practice needs.</p>",
    kalamata: "<h2>Kalamata</h2><p>Kalamata provides quick and accessible funding options tailored for healthcare practices.</p>",
    pirs: "<h2>PIRS</h2><p>PIRS specializes in structured financing solutions for growing practices.</p>",
    wallstreet: "<h2>Wall Street</h2><p>Wall Street Lending provides competitive rates and fast funding for various business needs.</p>",
    channel: "<h2>Channel</h2><p>Channel offers innovative working capital and advance funding solutions.</p>",
    libertas: "<h2>Libertas</h2><p>Libertas Financial provides equipment financing and working capital advances.</p>",
    peac: "<h2>PEAC</h2><p>PEAC offers equipment and technology financing for practices of all sizes.</p>",
    mulligan: "<h2>Mulligan</h2><p>Mulligan offers customized funding for specialized practice needs.</p>",
    northeastern: "<h2>Northeastern</h2><p>Northeastern provides flexible term loans and lines of credit.</p>",
    tabbank: "<h2>Tab Bank</h2><p>Tab Bank offers lines of credit and term loans for business growth.</p>",
    idea: "<h2>Idea Financial</h2><p>Idea Financial provides flexible, fast business funding with transparent terms.</p>",
    headway: "<h2>Headway</h2><p>Headway offers business advances and tailored funding for your practice.</p>",
    ondeck: "<h2>On Deck</h2><p>On Deck provides small business loans and lines of credit quickly and efficiently.</p>",
    finpart: "<h2>Fin Part Group</h2><p>Fin Part Group specializes in working capital and equipment financing solutions.</p>"
};

lenders.forEach(lender => {
    lender.addEventListener('click', () => {
        lenderInfo.innerHTML = infoData[lender.id] || "<p>No info available.</p>";
    });
});

let rotationAngle = 0;

function positionLenders(angleOffset = 0) {
    const spider = document.getElementById('spiderDiagram');
    const radius = 220;
    const centerX = spider.offsetWidth / 2 - 45; // 45 = lender width/2
    const centerY = spider.offsetHeight / 2 - 45; // 45 = lender height/2
    const outerLenders = document.querySelectorAll('.lender:not(.central)');
    const angleStep = (2 * Math.PI) / outerLenders.length;

    outerLenders.forEach((lender, index) => {
        const angle = index * angleStep + angleOffset - Math.PI / 2;
        const x = centerX + radius * Math.cos(angle);
        const y = centerY + radius * Math.sin(angle);
        lender.style.setProperty('--x', `${x}px`);
        lender.style.setProperty('--y', `${y}px`);
    });

    drawLines();
}


function drawLines() {
    const svg = document.querySelector('svg.lines');
    svg.innerHTML = "";

    const central = document.querySelector('.lender.central');
    const svgRect = svg.getBoundingClientRect();
    const centralRect = central.getBoundingClientRect();
    const centerX = centralRect.left + centralRect.width / 2 - svgRect.left;
    const centerY = centralRect.top + centralRect.height / 2 - svgRect.top;
    const centralRadius = centralRect.width / 2;
    const outerLenders = document.querySelectorAll('.lender:not(.central)');

    outerLenders.forEach(lender => {
        const lenderRect = lender.getBoundingClientRect();
        const lenderX = lenderRect.left + lenderRect.width / 2 - svgRect.left;
        const lenderY = lenderRect.top + lenderRect.height / 2 - svgRect.top;

        const dx = lenderX - centerX;
        const dy = lenderY - centerY;
        const length = Math.sqrt(dx * dx + dy * dy);

        const startX = centerX + (dx * centralRadius) / length;
        const startY = centerY + (dy * centralRadius) / length;

        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("x1", startX);
        line.setAttribute("y1", startY);
        line.setAttribute("x2", lenderX);
        line.setAttribute("y2", lenderY);
        line.setAttribute("stroke", "white");
        line.setAttribute("stroke-width", "2");
        svg.appendChild(line);
    });
}

function animateRotation() {
    rotationAngle += 0.002; // Adjust speed here if needed
    positionLenders(rotationAngle);
    requestAnimationFrame(animateRotation);
}

window.addEventListener('resize', () => positionLenders(rotationAngle));
window.addEventListener('load', () => animateRotation());
