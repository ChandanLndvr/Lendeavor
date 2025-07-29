const lenderInfo = document.getElementById('lenderInfo');
const lenders = document.querySelectorAll('.lender');
const infoData = {
    lendeavor: "<h2>Lendeavor</h2><p>Lendeavor is a financing platform that partners with various lenders to provide smart funding options for your practice.</p>",
    iou: "<h2>IOU</h2><p> <strong>Funding Type: </strong>Merchant Cash Advance, Working Capital Advance<br/> <strong>Funding Amount: </strong>$15k - $1.5M <br/> <strong>Min Credit Score: </strong> 650+ <br/> <strong>Time To Fund: </strong>24 hours<br/> <strong>Terms: </strong>6-18 months</p>",
    kalamata: "<h2>Kalamata</h2><p> <strong>Funding Type: </strong>Revenue-Based Financing, Merchant Cash Advance<br/> <strong>Funding Amount: </strong>$50k - $500k <br/> <strong>Min Credit Score: </strong> 600+ <br/> <strong>Time To Fund: </strong>24 hours<br/> <strong>Terms: </strong>6-15 months</p>",
    pirs: "<h2>PIRS</h2><p> <strong>Funding Type: </strong>Merchant Cash Advance, Revenue-Based Financing<br/> <strong>Funding Amount: </strong>$15k - $750k <br/> <strong>Min Credit Score: </strong> 500+ <br/> <strong>Time To Fund: </strong>1-2 days<br/> <strong>Terms: </strong>3-12 months</p>",
    wallstreet: "<h2>Wall Street</h2> <p><strong>Funding Type: </strong>Merchant Cash Advance, Term Loans<br/> <strong>Funding Amount: </strong>$15k - $2.5M <br/> <strong>Min Credit Score: </strong> 600+ <br/> <strong>Time To Fund: </strong>1-2 days<br/> <strong>Terms: </strong>6-15 months</p>",
    channel: "<h2>Channel</h2><p> <strong>Funding Type: </strong>Business Loan, Business Advance<br/> <strong>Funding Amount: </strong>$100k - $250k <br/> <strong>Min Credit Score: </strong> 650+ <br/> <strong>Time To Fund: </strong>24 hours<br/> <strong>Terms: </strong>6-18 months</p>",
    libertas: "<h2>Libertas</h2><p> <strong>Funding Type: </strong>Revenue Based Financing, Business Term Loan<br/> <strong>Funding Amount: </strong>$25k - $10M <br/> <strong>Min Credit Score: </strong>	550+ <br/> <strong>Time To Fund: </strong>1-2 days<br/> <strong>Terms: </strong>12-36 months months</p>",
    peac: "<h2>PEAC</h2><p> <strong>Funding Type: </strong>Working Capital Loan, Equipment Financing<br/> <strong>Funding Amount: </strong>$5k - $250k <br/> <strong>Min Credit Score: </strong> 600+ <br/> <strong>Time To Fund: </strong>24 hours<br/> <strong>Terms: </strong>6-24 months</p>",
    mulligan: "<h2>Mulligan</h2> <p><strong>Funding Type: </strong>Business Lines of Credit, Working Capital Loans<br/> <strong>Funding Amount: </strong>$10k - $2M <br/> <strong>Min Credit Score: </strong> 625+ <br/> <strong>Time To Fund: </strong>24 hours<br/> <strong>Terms: </strong>3-24 months</p>",
    northeastern: "<h2>Northeastern</h2><p> <strong>Funding Type: </strong>SBA loans covering Working Capital, Equipment, etc.<br/>  <strong>Funding Amount: </strong>$2M – $50M <br/>  <strong>Min Credit Score: </strong>	600+ <br/>  <strong>Time To Fund: </strong>5-7 days<br/>  <strong>Terms: </strong>1–7 years</p>",
    tabbank: "<h2>Tab Bank</h2><p> <strong>Funding Type: </strong>Lines of Credit, Asset-based, A/R & Equipment Financing<br/>  <strong>Funding Amount: </strong>$30K – $300k <br/>  <strong>Min Credit Score: </strong> 600+ <br/>  <strong>Time To Fund: </strong>1–2 days<br/>  <strong>Terms: </strong>30-60 months</p>",
    idea: "<h2>Idea Financial</h2><p> <strong>Funding Type: </strong>Business Loans, Line of Credits<br/>  <strong>Funding Amount: </strong>$10k - $275k <br/>  <strong>Min Credit Score: </strong> 650+ <br/>  <strong>Time To Fund: </strong>24 hours<br/>  <strong>Terms: </strong>3-18 mont </p>",
    headway: "<h2>Headway</h2><p> <strong>Funding Type: </strong>Business Line of Credit<br/>  <strong>Funding Amount: </strong>$5k - $100k <br/>  <strong>Min Credit Score: </strong> 675+ <br/>  <strong>Time To Fund: </strong>24 hours<br/>  <strong>Terms: </strong>12-24 mont </p>",
    ondeck: "<h2>On Deck</h2><p> <strong>Funding Type: </strong>Term Loans, Business Line of Credit<br/>  <strong>Funding Amount: </strong>$5k - $250k <br/>  <strong>Min Credit Score: </strong> 625+ <br/>  <strong>Time To Fund: </strong>24 hours<br/>  <strong>Terms: </strong>12-24 mont </p>",
    finpart: "<h2>Fin Part Group</h2><p> <strong>Funding Type: </strong>Working Capital Loan, Equipment Financing<br/>  <strong>Funding Amount: </strong>$25k - $500k <br/>  <strong>Min Credit Score: </strong> 600+ <br/>  <strong>Time To Fund: </strong>1-2 days<br/>  <strong>Terms: </strong>12-60 mont </p>"
};


lenders.forEach(lender => {
    lender.addEventListener('click', () => {
        lenderInfo.innerHTML = infoData[lender.id] || "<p>No info available.</p>";
    });
});

let rotationAngle = 0;

function positionLenders(angleOffset = 0) {
    const spider = document.getElementById('spiderDiagram');
    const radius = 280;
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