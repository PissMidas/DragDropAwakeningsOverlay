# DragDropAwakeningsOverlay
A GUI that enables stream runners to read awakening data from logs and create an overlay about awakenings.



To compile this program...
1. Download this repo.
2. install relevant libraries (and pyinstaller)
3. go to command terminal and type in
   pyinstaller --onefile --icon=images/nao_thumbnail.ico --add-data "images;images" --noconsole --name "DragnDropAwakeningsOverlay" main.py

   use --no console flag for now to be able to see print statements.


   pyinstaller --onefile --icon=images/nao_thumbnail.ico --add-data "images;images" --name "DragnDropAwakeningsOverlay" main.py


4. being able to see the console is useful for debugging. I mostly expect developrs to want to be able to see the console.
5. Once all slots on the gui are filled manually, it outputs 6 text files locally: player0.txt, player1.txt, etc.
6. If you are not a developer, simply go to https://api.github.com/repos/PissMidas/DragDropAwakeningsOverlay/releases to download the .exe file. download and double click the .exe to start.
7. contact me if you are a stream runner and are confused about this.
