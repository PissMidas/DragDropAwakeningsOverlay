# DragDropAwakeningsOverlay
A GUI that enables stream runners to read awakening data from logs and create an overlay about awakenings.



To compile this program...
1. Download this repo.
2. install relevant libraries (and pyinstaller)
3. go to command terminal and type in
   pyinstaller --onefile --icon=images/nao_thumbnail.ico --add-data "images;images" --noconsole --name "DragDropAwakeningsOverlay" main.py
