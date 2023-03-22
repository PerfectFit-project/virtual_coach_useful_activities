// Based on this post: https://adamtheautomator.com/https-nodejs/

// Import the express module
var express = require('express');

// Instantiate an Express application
const app = express();
var path = require('path')

// Create listener on port 3000 that points to the Express app
const https = require('https');
const server = https.createServer(
		// Provide the private and public key to the server by reading each
		// file's content with the readFileSync() method.
    {
      key: fs.readFileSync("key.pem"),
      cert: fs.readFileSync("cert.pem"),
    },
    app
  )
var cors = require('cors')
const PORT = 3000;
server.listen(PORT);
console.log(`Server is running on port ${PORT}`);

app.use(cors())
app.use(express.static(path.join(__dirname, 'static')));

// This code tells the service to listen to any request coming to the / route.
// Once the request is received, the line res.sendFile() is executed.
app.get('/', (req, res) => {
    res.sendFile(__dirname + '/index.html');
 });