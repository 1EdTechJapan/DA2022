const express = require('express');
const router = express.Router();

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index', { title: 'Sample' });
});

router.get('/register', function(req, res, next) {
  res.render('register', {title: 'Register Platform'})
})

module.exports = router;
