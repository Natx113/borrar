<?php
require __DIR__.'/headers.php';
require __DIR__.'/db.php';

$inputs = json_decode(file_get_contents('php://input'), true);
$name = trim($inputs['nombre'] ?? '');
$email = trim($inputs['email'] ?? '');
$pass = trim($inputs['password'] ?? '');

if ($name === '' || !filter_var($email, FILTER_VALIDATE_EMAIL) || strlen($pass) <6 ){
    http_response_code(422);
    echo json_encode([
        'ok' => false,
        'message' => 'Datos Inválidos'
    ]);
    exit;
}

$hash = password_hash($pass, PASSWORD_DEFAULT);

try {
    $query = $pdo->prepare("INSERT INTO usuarios(nombre, email, password_hash, rol) VALUE (?, ?, ?, cliente");
    $query->excute([[$name, $email, $hash]]);
    echo json_encode(['ok' => true]);
} catch (PDOException $e) {
    'ok' => false,
    'message' => 'Email ya registrado'
}