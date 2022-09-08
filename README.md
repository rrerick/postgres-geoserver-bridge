# <p align=center>geoserver-api </p>
__________________________________________________________________________________________________________________________________________


  <p align=center> This aplications works like a bridge between geoserver and registered database.</p>
  <br />
  <h1>:construction_worker: STEPS </h1>
  <br />

  <p><b>(ONE)</b></p>When U build the docker-compose an SuperUser is create, and with this user you can add another user and manager the app.<br><br>
  <b>&emsp;&emsp;&emsp;:bangbang: You shouldn't create, at this moment,more than one admin login user. Just one is necessary, the others can have a user just to authenticated to a view.</b>
 
  <br><p><b>(TWO)</b></p>
    
<p align=left>:small_blue_diamond:Create a Geoserver User <br>
:small_blue_diamond:Create a Postgresql User(pg_user)<br>
  <b>if another person will request;<br></b>
&emsp;&emsp;:small_blue_diamond:create a non-admin user:</p>


  
 <br><p><b>(THREE)</b></p>
 <p>Get your token acess and refresh on:<br>
  
 `localhost:8000/geoserver/api/token`
  
  Or by shell
 ```bash
 curl -X POST -H "Content-Type: application/json" -d '{"username": "YOUR_NAME", "password": "YOUR_PASSWORD"}'  http://localhost:8000/geoserver/api/token/
 ```
</p>
<br><p><b>(FOUR)</b></p>
 <p>Refresh Geoserver with this command.<br>
  
 ```bash
 curl  http://localhost:8000/geoserver/api/ -H "Authorization: Bearer YOUR_TOKEN"
 ```
</p>
