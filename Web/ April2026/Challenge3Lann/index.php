<?php
// Read flag from file (not visible in source)
$flag_content = "";
if (file_exists("flag.txt")) {
    $flag_content = trim(file_get_contents("flag.txt"));
}
// Deliberately insecure cookie (NOT HttpOnly)
// Looks like an ops token, but actually the flag
setcookie(
    "ops_session",
    $flag_content,
    time() + 3600,
    "/"
);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Summit International Airport – Passenger Feedback</title>
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
        input[type="text"] {
            width: 520px;
            padding: 6px;
            background-color: #102a43;
            color: #ffffff;
            border: 1px solid #4db8ff;
        }
        input[type="submit"] {
            background-color: #1f6fb2;
            color: #ffffff;
            border: none;
            padding: 6px 12px;
            margin-left: 6px;
            cursor: pointer;
        }
        .comment-box {
            margin-top: 20px;
            padding: 15px;
            border: 1px solid #4db8ff;
            background-color: #071521;
        }
    </style>
</head>
<body>
<h1>Summit International Airport</h1>
<h3>Passenger Feedback Portal</h3>
<p>
Help us improve airport operations.  
All feedback is reviewed by airport staff.
</p>
<form method="GET">
    <input type="text" name="comment" placeholder="Enter feedback here">
    <input type="submit" value="Submit Feedback">
</form>
<hr>
<p><strong>Latest Comment:</strong></p>
<div class="comment-box">
<?php
if (isset($_GET['comment'])) {
    $comment = $_GET['comment'];
    // ❌ Naive XSS filtering (intentionally flawed)
    $blocked = ['<script>', '</script>'];
    $comment = str_ireplace($blocked, '', $comment);
    echo $comment;
}
?>
</div>
</body>
</html>
