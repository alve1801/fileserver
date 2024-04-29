# Basic python file upload server

Since I keep remaking this from scratch every couple months and then proceed to loose it, I decided to put up this time's version on github.

Opens a socket on localhost:8000 (can be accessed via lan/wlan, eg on a smartphone) and serves a html upload form. Processes response and saves files in `uploads` folder.
TODO: figure out how to circumvent the delay in line 84 - I put it there because `client_connection.recv` was too hasty and requested data before it had arrived, which doesn't feel like the best way to solve this.
