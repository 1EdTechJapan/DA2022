const express = require('express')
const favicon = require('serve-favicon')
const path = require('path')
const cookieParser = require('cookie-parser')
const bodyParser = require('body-parser')
const logger = require('morgan')
const extend = require('extend')
const fs = require('fs')

require('dotenv').config()

const app = express()

app.use(logger('dev'))
app.use(bodyParser.json({limit: '50mb'}))
app.use(bodyParser.urlencoded({ limit:'50mb', extended: true }))
app.use(favicon(path.join(__dirname, 'public/favicon.ico')))
app.set('views', __dirname + '/views')
app.set('view engine', 'ejs')

app.use(cookieParser())

app.use(express.static(__dirname + '/public'))

app.use(function(req, res, next) {
	res.header("Accept-CH", "UA, Platform")
	res.header("Access-Control-Allow-Origin", "*")
	res.header("Access-Control-Allow-Headers", "Origin, Authorization, X-Requested-With, Content-Type, Accept")
	res.header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
	next()
});

const root = require('./routes/index')
app.use('/', root)

const users = require('./routes/users/index')
app.use('/users', users)

app.use(function(err, req, res, next) {
    res.status(404)
    next("Not found")
});

const port = process.env.PORT || '3001'

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`)
})