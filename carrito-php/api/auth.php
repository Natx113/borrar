<?php
require __DIR__ . '/db.php';

function current_user_or_401(){
    $token = $_COOKIE['token'] ?? null;
    if(!$token) {
        http_response_code(401);
        echo json_encode([
            'ok' => false,
            'message' => 'No token'
        ]);
        exit;
    }
    global $pdo;
    $query = $pdo->prepare("SELECT u.id, u.nombre, u.email, u.rol FROM session s JOIN usuarios u ON u.id = s.user_id WHERE s.token = ? AND s.expires_at > NOW ()");
    $query->execute([$token]);
    $user = $query->fetch();
    if (!$user) {
        http_response_code(401);
        echo json_encode([
            'ok' => false,
            'message' => 'Token Inválido'
        ]);
        exit;
    }
    return $user;
}