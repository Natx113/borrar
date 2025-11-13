<?php
require __DIR__ . '/_headers.php';
require __DIR__ . '/db.php';
$config = require __DIR__ . '/config.php';

$nombre = trim($_POST['nombre'] ?? '');
$precio = (float)($_POST['precio'] ?? '');
$descrip = trim($_POST['descrip'] ?? '');

if($nombre === '' || $precio <= 0){
    http_response_code(422);
    echo json_encode(['ok' => false, 'message' => 'Nombre y precio son obligatorios']);
    exit;
}
$imagenPath = null;
if (!empty($_FILES['imagen']['name'])) {
    $ext = strtolower(pathinfo($_FILES['imagen']['name'], PATHINFO_EXTENSION));
    $allowed = ['jpg','jpeg','png','webp'];
    if (!in_array($ext, $allowed)) {
        http_response_code(415);
        echo json_encode(['ok'=>false, 'message'=>'Formato de imagen no permitido']); exit;
    }
    $fname = 'prod_' . time() . '_' . bin2hex(random_bytes(4)) . '.' . $ext;
    $dest = realpath($config['upload_dir']) . DIRECTORY_SEPARATOR . $fname;
    if (!move_uploaded_file($_FILES['imagen']['tmp_name'], $dest)) {
        http_response_code(500);
        echo json_encode(['ok'=>false, 'message'=>'No se pudo guardar la imagen']); exit;
    }
    $imagenPath = $fname;
}

$query = $pdo->prepare("INSERT INTO productos ( nombre, descrip, precio, imagen) VALUES(?, ?, ?, ?");
$query->execute([$nombre, $descrip, $precio, $imagenPath]);

echo json_encode(['ok' => true, 'id' => $pdo->lastInsertId()]);