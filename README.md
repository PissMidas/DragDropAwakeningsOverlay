# DragDropAwakeningsOverlay
A GUI that enables stream runners to read awakening data from logs and create an overlay about awakenings.



To compile this program...
1. Download this repo.
2. install relevant libraries (and pyinstaller)
3. go to command terminal and type in
   pyinstaller --onefile --icon=images/nao_thumbnail.ico --add-data "images;images" --noconsole --name "DragDropAwakeningsOverlay" main.py

   use --no console flag for now to be able to see print statements.


   pyinstaller --onefile --icon=images/nao_thumbnail.ico --add-data "images;images" --name "DragDropAwakeningsOverlay" main.py


4. Currently this is a WIP. it only prints to terminal. if you are a stream runner and would like to use this, contact me if you need help.


5. next update i will have the program spit out a text file (or 6) about player info instead of a print statement.
