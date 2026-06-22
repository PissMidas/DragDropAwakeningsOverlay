# DragDropAwakeningsOverlay
A GUI that enables that stream runners can use while spectating an Omega Strikers game. After dragging the images and names in the GUI, an overlay is created that can be broadcasted to OBS.

## These steps below are for stream runners that want to download this app
1. go to https://github.com/PissMidas/DragDropAwakeningsOverlay/releases to download the project zip file. Extract the project, and then double click the .exe to start the app while Omega Strikers is running. You must be spectating a full game to generate an overlay. Generally a 3v3 custom, although the app technically works in ranked/normals. App does not work with games less than 6 players.
2. Once all slots are filled manually on the gui (it requires the user to match which players are playing which characters; dragging and dropping icons and names present on the GUI), the app outputs two overlays to...
  http://localhost:8765/blue and http://localhost:8765/red

3. Go to OBS. Add a new source. Select Browser. Name it 'blue team' (or something similar). Set the url to http://localhost:8765/blue . set width to 1920, and height to 1080. Delete whatever is in the "Custom CSS" field. Press OK (You do not need to mess with the other settings, just keep them to whatever they default came with). Resize the overlay as needed.

5. Repeat, for red team.

6. contact me if you are a stream runner and are confused about anything. if you encounter a bug, contact me and be prepared to provide the .log files and a description. A vod of it occuring is useful. 

7. nothing is stopping you from modifying the files in the 'website' folder (except time and expertise)! if you don't like an offset, change the css. you can redesign the overlay UI by replacing the asset files. If you are interested in this, please share your assets.

8. click the 'clear all' button after a game. You do not need to use this button, it's just there for quality of life.

## These steps below are for people who want to build on top of this project, or for people who want to compile the program themselves.
To compile this program...
1. Download this repo.
2. install relevant libraries (and pyinstaller)
3. go to command terminal and type in
   
   pyinstaller --onefile --icon=images/nao_thumbnail.ico --add-data "images;images" --noconsole --name "DragnDropAwakeningsOverlay" main.py

  the above comands uses '--noconsole' flag which disables print statements.


   pyinstaller --onefile --icon=images/nao_thumbnail.ico --add-data "images;images" --name "DragnDropAwakeningsOverlay" main.py
   
   the above command does not use '--noconsole'. you can see print statements, which is useful for debugging.

4. you do not have to compile the program into an executable, you can also just run 'python main.py'. but these steps above are for if you want to compile the app.

## Acknowledgements
Thank you to zzZ for the original overlay design.
