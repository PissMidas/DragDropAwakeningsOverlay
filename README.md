# DragDropAwakeningsOverlay
A GUI that enables stream runners to read awakening data from logs and create an overlay about awakenings.

## These steps below are for stream runners that want to download this app
1. go to https://github.com/PissMidas/DragDropAwakeningsOverlay/releases to download the .exe file. download and double click the .exe to start.
2. Once all slots are filled manually on the gui, the app outputs 6 text files. 'player0.txt', 'player1.txt', etc.
3. contact me if you are a stream runner and are confused about anything.




## These steps below are for people who want to build on top of this project, or for people who want to compile the program themselves.
To compile this program...
1. Download this repo.
2. install relevant libraries (and pyinstaller)
3. go to command terminal and type in
   pyinstaller --onefile --icon=images/nao_thumbnail.ico --add-data "images;images" --noconsole --name "DragnDropAwakeningsOverlay" main.py

  the above comands uses '--noconsole' flag which disables print statements.


   pyinstaller --onefile --icon=images/nao_thumbnail.ico --add-data "images;images" --name "DragnDropAwakeningsOverlay" main.py
   the above command does not use '--noconsole'. you can see print statements, which is useful for debugging.

4. you do not have to compile the program, you can also just run 'python main.py'. but these steps above are for if you want to compile the app.
