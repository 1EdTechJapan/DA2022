<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title></title>
</head>
<body>
<form action="<?= $launchUrl ?>" method="post">
  <input type="hidden" name="id_token" value="<?= $idToken ?>"><br>
  <input type="hidden" name="state" value="<?= $state ?>"><br>
</form>
</body>
<script>
document.forms[0].submit()
</script>
</html>