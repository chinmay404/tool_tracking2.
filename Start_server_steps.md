install gunicorn  nginx django
sudo nano /etc/systemd/system/gunicorn.socket 
put this is above file To configure service socket auto starts server after kill of machine restart:
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target


then run this:
sudo vim /etc/systemd/system/gunicorn.service

add :
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=....ADD USERNAME HERE ....
Group=www-data
WorkingDirectory=/home/harry/projectdir
ExecStart=/home/harry/projectdir/env/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          textutils.wsgi:application

[Install]
WantedBy=multi-user.target



sudo vim /etc/systemd/system/gunicorn.service




[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=harry
Group=www-data
WorkingDirectory=/home/harry/projectdir
ExecStart=/home/harry/projectdir/env/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          textutils.wsgi:application

[Install]
WantedBy=multi-user.target


sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket

NGINX :
sudo vim /etc/nginx/sites-available/Project_name

server {
    listen 80;
    server_name www.codewithharry.in;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/harry/projectdir;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}



sudo ln -s /etc/nginx/sites-available/textutils /etc/nginx/sites-enabled/


sudo systemctl restart nginx










<!-- NONE -->


server {
    listen 80;
    server_name example.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /var/www/example.com;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}



sudo usermod -aG sirius www-data    