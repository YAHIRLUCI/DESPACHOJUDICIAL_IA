<?php

session_start();

include("conexion.php");

$correo = $_POST['correo'];
$password = $_POST['password'];

$sql = "SELECT * FROM usuarios
        WHERE correo='$correo'
        AND password='$password'";

$resultado = $conn->query($sql);

if($resultado->num_rows > 0){

    $usuario = $resultado->fetch_assoc();

    $_SESSION['usuario'] = $usuario['nombre'];
    $_SESSION['rol'] = strtoupper($usuario['rol']);

    // Rol USUARIO
    if($_SESSION['rol'] == "USUARIO"){

        header("Location: ../index_publico.php");
        exit();

    }

    // Roles EMPLEADO y ADMINISTRADOR
    header("Location: ../index.php");
    exit();

}else{

    header("Location: ../login.html");
    exit();

}

?>