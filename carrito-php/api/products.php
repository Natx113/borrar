<?php
require __DIR__ . '/_headers.php';
require __DIR__ . '/db.php';
$config = require __DIR__ . '/config.php';
$base = rtrim($config['base_url'], '/');

$rows = $pdo->query("SELECT * FROM productos ORDER BY id DESC")->fetchAll();
$rows = array_map(function($r) use ($base){
    $r['imagen_url'] = $r['imagen'] ? $base . '/uploads/' . $r['imagen'] : null;
    return $r;
}, $rows);

echo json_encode(['ok' => true, 'data' => $rows]);