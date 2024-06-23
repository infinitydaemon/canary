<?php
session_start();

$usersFile = 'users.txt';

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $username = $_POST['username'];
    $password = $_POST['password'];

    // Validate credentials
    if (validateCredentials($username, $password, $usersFile)) {
        $_SESSION['username'] = $username;
        header('Location: dashboard.php');
        exit;
    } else {
        echo 'Invalid username or password';
    }
}

function validateCredentials($username, $password, $usersFile) {
    $users = file($usersFile, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);

    foreach ($users as $user) {
        list($storedUsername, $storedPassword) = explode(':', $user);
        if ($username == $storedUsername && password_verify($password, $storedPassword)) {
            return true;
        }
    }
    return false;
}
?>
