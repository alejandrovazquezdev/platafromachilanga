let reigstrado=[{nombre:"Admin",contraseña:12345678}]
let nom=document.getElementById("input1")
let cont=document.getElementById("input2")
let btn=document.getElementById("inicio")

btn.addEventListener("click", ()=>{
e.preventDefault()
let usuario=nom.value
let contra=cont.value
if(usuario == registrado[0].nombre && contra == registrado[0].contraseña){
alert("Bienvenido"+ registrado[0].nombre)

window.location.href="dashboard.html"}
else{
alert("Datos incorrectos,vuelva intentar")
}
})
