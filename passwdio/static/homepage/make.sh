#!/bin/bash
cat vendor/bootstrap.css vendor/bootstrap-responsive.css app.css > temp.css
yui-compressor temp.css > index.css
rm temp.css
cat vendor/jquery-1.7.1.min.js vendor/bootstrap.js app.js > temp.js
yui-compressor temp.js > index.js
rm temp.js

