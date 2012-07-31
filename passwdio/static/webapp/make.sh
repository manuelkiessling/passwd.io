#!/bin/bash
cat vendor/jquery.mobile-1.1.1.min.css app.css > temp.css
yui-compressor temp.css > index.1.css
rm temp.css
cat vendor/jquery-1.7.1.min.js vendor/jquery.mobile-1.1.1.min.js vendor/sjcl.js app.js > temp.js
yui-compressor temp.js > index.1.js
rm temp.js

