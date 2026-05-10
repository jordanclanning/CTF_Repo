<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['username'] ?? '';
    $password = $_POST['password'] ?? '';
    
    try {
        // Connect to SQLite database
        $pdo = new PDO('sqlite:database.db');
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        
        // Vulnerable SQL query - intentionally allows SQL injection
        $sql = "SELECT * FROM users WHERE username = '$username' AND password = '$password'";
        $stmt = $pdo->prepare($sql);
        $stmt->execute();
        
        $user = $stmt->fetch(PDO::FETCH_ASSOC);
        
        if ($user) {
            $success = true;
            $flag = "Summit{SQLInjectionsAreFun}";
        } else {
            $success = false;
            $error = "Invalid username or password.";
        }
        
    } catch (PDOException $e) {
        $success = false;
        $error = "Database error occurred.";
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Summit International Airport - Login Result</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <!-- Header -->
    <header class="header">
        <h1>Summit International Airport</h1>
        <p>Passenger Services & Operations Portal</p>
    </header>

    <!-- Hero Image -->
    <div class="hero"></div>

    <!-- Main Container -->
    <main class="container">
        <?php if (isset($success) && $success): ?>
            <div class="success-message">
                <h2>Login Successful</h2>
                <p>Welcome, authorized user.</p>
                <p><strong><?= htmlspecialchars($flag) ?></strong></p>
            </div>
        <?php elseif (isset($error)): ?>
            <div class="error-message">
                <h2>Login Failed</h2>
                <p><?= htmlspecialchars($error) ?></p>
                <p><a href="index.html">← Back to Login</a></p>
            </div>
        <?php else: ?>
            <p><a href="index.html">← Back to Login</a></p>
        <?php endif; ?>
    </main>

    <!-- Footer -->
    <footer class="footer">
        <p>&copy; 2024 Summit International Airport. All rights reserved.</p>
    </footer>
</body>
</html>
