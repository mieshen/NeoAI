@echo off
set PORT=7821
echo Server will run on port %PORT%  
echo http://localhost:%PORT%
python -m http.server %PORT%