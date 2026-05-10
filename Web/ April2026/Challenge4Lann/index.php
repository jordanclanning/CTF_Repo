<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Summit International Airport – Network Operations Console</title>
    <style>
        body {
            background-color: #0b1c2d;
            color: #e6edf3;
            font-family: monospace;
            padding: 40px;
        }
        h1 {
            color: #4db8ff;
        }
        h3 {
            color: #9cd3ff;
        }
        input[type="text"] {
            background-color: #102a43;
            color: #ffffff;
            border: 1px solid #4db8ff;
            padding: 6px;
            width: 260px;
        }
        input[type="submit"] {
            background-color: #1f6fb2;
            color: #ffffff;
            border: none;
            padding: 6px 12px;
            margin-left: 6px;
            cursor: pointer;
        }
        pre {
            background-color: #071521;
            padding: 15px;
            border: 1px solid #4db8ff;
            margin-top: 20px;
            white-space: pre-wrap;
        }
    </style>
</head>
<body>
<h1>Summit International Airport</h1>
<h3>Network Operations & Diagnostics Console</h3>
<p>Enter beacon IP or hostname for ICMP validation:</p>
<form method="GET">
    <input type="text" name="host" placeholder="127.0.0.1">
    <input type="submit" value="Run Diagnostics">
</form>
<pre>
<?php
if (isset($_GET['host'])) {
    // Raw user input
    $host = $_GET['host'];
    // ❌ Naive blacklist filtering (intentionally flawed)
    $blocked = [';', '&', '|', '&&', '||'];
    $host = str_replace($blocked, '', $host);
    // Execute diagnostics (stderr redirected to stdout)
    system("ping -c 1 " . $host . " 2>&1");
}
?>
</pre>
</body>
</html>
