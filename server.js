//server.js 
const express = require('express');
const app = express();

//route files
const screenshotRoutes = require('./routes/screenshot');
const camera_controlRoutes = require('./routes/camera_control');
const recalibrate_mountRoutes = require('./routes/recalibrate_mount');
const spectrum_analysisRoutes = require('./routes/spectrum_analysis');

//use routes
app.use('/screenshot', screenshotRoutes);
app.use('/camera_control', camera_controlRoutes);
app.use('/recalibrate_mount', recalibrate_mountRoutes);
app.use('/spectrum_analysis', spectrum_analysisRoutes);

//defining a route in Express
app.get('/', (req, res) => {
   res.send('<h1>Welcome to Project StarSpec!</h1>');
});

//specifying the port & starting the server
const port = process.env.PORT || 3000; // You can use environment variables for port configuration

app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});