// Espera a que el documento esté completamente cargado
document.addEventListener("DOMContentLoaded", function () {

    // Selecciona todos los formularios de la página
    const forms = document.querySelectorAll("form");
    // Recorre cada formulario encontrado
    forms.forEach(form => {
      // Escucha el evento 'submit' de cada formulario
    form.addEventListener("submit", function () {
        // Encuentra todos los campos de tipo archivo dentro del formulario
        const fileInputs = form.querySelectorAll('input[type="file"]');
        // Espera 1 segundo (para permitir la descarga) y luego limpia los archivos
        setTimeout(() => {
        fileInputs.forEach(input => {
            input.value = ''; // Limpia el campo de archivo
        });
        }, 1000);
    });
    });
});

