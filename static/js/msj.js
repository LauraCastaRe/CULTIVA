window.addEventListener("load", function(){
    this.document.getElementById("log").addEventListener("click",function(){
        swal("Algo esta mal...!", "Usuario o contraseña incorrecta!", "error");
    })
    this.document.getElementById("enviarRegistro").addEventListener("click",function(){
        swal("Perfecto!", "Usuario creado correctamente!", "success");
    })

})
