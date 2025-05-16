const canvas = document.getElementById('pdfCanvas');
const ctx = canvas.getContext('2d');
let isDrawing = false;
let startX, startY;
let selections = [];
let currentPdf = null;

// Cargar el PDF seleccionado
document.getElementById('pdfUpload').addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file.type !== "application/pdf") {
        alert("Por favor, selecciona un archivo PDF válido.");
        return;
    }

    const fileReader = new FileReader();
    fileReader.onload = function () {
        const typedArray = new Uint8Array(this.result);
        pdfjsLib.getDocument(typedArray).promise.then(pdf => {
            currentPdf = pdf;
            renderPage(1); // Solo la primera página por ahora
        });
    };
    fileReader.readAsArrayBuffer(file);
});

// Renderizar la página del PDF
function renderPage(pageNumber) {
    currentPdf.getPage(pageNumber).then(page => {
        const viewport = page.getViewport({ scale: 1.5 });
        canvas.width = viewport.width;
        canvas.height = viewport.height;

        const renderContext = {
            canvasContext: ctx,
            viewport: viewport
        };
        page.render(renderContext);
    });
}

// Selección de campos con el mouse
canvas.addEventListener('mousedown', (e) => {
    startX = e.offsetX;
    startY = e.offsetY;
    isDrawing = true;
});

canvas.addEventListener('mousemove', (e) => {
    if (!isDrawing) return;
    const width = e.offsetX - startX;
    const height = e.offsetY - startY;
    redrawCanvas();
    drawSelection(startX, startY, width, height);
});

canvas.addEventListener('mouseup', (e) => {
    isDrawing = false;
    const width = e.offsetX - startX;
    const height = e.offsetY - startY;
    const label = prompt("Nombre del campo (Ej: Total, RFC, Fecha):");
    if (label) {
        selections.push({ label, x: startX, y: startY, width, height });
        updateFieldList();
    }
    redrawCanvas();
});

function drawSelection(x, y, width, height, color = 'red') {
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.strokeRect(x, y, width, height);
}

function redrawCanvas() {
    renderPage(1); // Redibuja base del PDF
    selections.forEach(s => drawSelection(s.x, s.y, s.width, s.height));
}

function updateFieldList() {
    const container = document.getElementById('selectedFields');
    container.innerHTML = "<label>Campos seleccionados:</label>";
    selections.forEach(s => {
        const p = document.createElement('p');
        p.textContent = `${s.label} → x:${s.x}, y:${s.y}`;
        container.appendChild(p);
    });
}

document.getElementById('extractButton').addEventListener('click', () => {
    fetch('/exportar-editor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(selections)
    })
    .then(res => res.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'factura_editada.xlsx';
        a.click();
    });
});



