<?php

include("conexion.php");

$nombre = $_POST['nombre'];
$correo = $_POST['correo'];
$password = $_POST['password'];
$rol = $_POST['rol'];

$sql = "INSERT INTO usuarios
(nombre, correo, password, rol)
VALUES
('$nombre', '$correo', '$password', '$rol')";

if($conn->query($sql)){

    header("Location: ../login.html");
    exit();

}else{

    echo "Error al registrar usuario";

}

?>