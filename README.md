# <p align=center>postgres-geoserver-bridge</p>
__________________________________________________________________________________________________________________________________________


  <p align=center> This aplications works like a bridge between geoserver and registered database.</p>
  <br />
  <h1>:construction_worker: HOW IT WORKS</h1>
  
 <p>When running, this application has the purpose of create Workspaces, Datastores and publish layers on Geoserver, all this had previously registered.
 </p>
 
 ![schema](https://user-images.githubusercontent.com/78693116/189120712-f8d98f32-3ef6-42ef-823f-fc5e1361bbf5.png)
 
 On django admin the administration user must record information about database connection and geoserver connection, other way the application won't works. 
 
With this information the application going to read the metadata on each database registered and with this will operate on geoserver.
 
 ```bash
 '{
            "bio": "#TODO",
            "author": null,
            "contact": "Contact <contact@email.com>",
            "source": [
                null
            ],
            "source_uri_s": [
                null
            ],
            "keywords": [
                null
            ],
            "geoserver": [
                {
                    "geoserver_workspace": null,
                    "geoserver_layer_title": null,
                    "geoserver_layer_name": null,
                    "geoserver_style_uri": null,
                    "geoserver_instance_name": null
                }
            ],
            "update_frequency": null,
            "scale": null,
            "structure_creation_date": null,
            "structure_modification_date": null,
            "last_commit_date": null,
            "comment_update_date": null
        }'
 ```
 
 This part, above, is read by the application. Its the most important part.

  
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
  
 `localhost:8000/user/token`
  
  Or by shell
 ```bash
 curl -X POST -H "Content-Type: application/json" -d '{"username": "YOUR_NAME", "password": "YOUR_PASSWORD"}'  http://localhost:8000/user/token/
 ```
</p>
<br><p><b>(FOUR)</b></p>
 <p>Refresh Geoserver with this command.<br>
  
 ```bash
 curl  http://localhost:8000/geoserver/ -H "Authorization: Bearer YOUR_TOKEN"
 ```
</p>

<h2>:grey_exclamation: Settings </h2>

<p><b> 1.(.ENV):</b><p>
<p>You need to create an .Env file, with this params:<br>
  <ul>
<li>&emsp;<b>'dbname':</b> Name of django database</li><br>
<li>&emsp;<b>'user': </b>name of database user</li><br>
<li>&emsp;<b>'password':</b> passwd of database user</li><br>
<li>&emsp;<b>'host': </b>database host</li><br>
<li>&emsp;<b>'port':</b> database port</li><br>
<li>&emsp;<b>'SECRET_KEY':</b> django secret key</li><br>
<li>&emsp;<b>'secret':</b> a random secret to generate passwords</li>


