<?php
session_start();

// Jika belum login, alihkan ke login.php
if (!isset($_SESSION['username'])) {
    header('Location: login.php');
    exit();
}

// Logout jika tombol logout ditekan
if (isset($_POST['logout'])) {
    session_destroy();
    header('Location: login.php');
    exit();
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Home - Stub</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css">
</head>
<body class="container mt-5">
    <h2>Selamat datang, <?= htmlspecialchars($_SESSION['username']); ?>!</h2>
    <p>Anda berhasil login ke sistem.</p>

    <form method="POST">
        <button type="submit" name="logout" class="btn btn-danger">Logout</button>
    </form>
</body>
</html>
