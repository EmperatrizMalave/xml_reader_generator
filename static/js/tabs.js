// Función que maneja el cambio entre pestañas
function openTab(evt, tabName) {
    // Oculta todo el contenido de las pestañas
    const contents = document.getElementsByClassName("tabcontent");
    for (let i = 0; i < contents.length; i++) {
    contents[i].classList.remove("active");
    }
    // Desactiva todos los botones del menú
    const buttons = document.getElementsByClassName("tablinks");
    for (let i = 0; i < buttons.length; i++) {
    buttons[i].classList.remove("active");
    }
    // Muestra el contenido de la pestaña seleccionada
    document.getElementById(tabName).classList.add("active");
    // Activa visualmente el botón que fue clicado
    evt.currentTarget.classList.add("active");
}
