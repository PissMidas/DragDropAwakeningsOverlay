from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy, QPushButton
from PyQt5.QtCore import pyqtSignal, Qt, QObject, QThread, QMimeData, QPoint, QRect, QUrl,QCoreApplication
from PyQt5.QtGui import QPixmap, QDrag, QPainter, QFont, QColor
import os
import sys
import pygetwindow
import re
import ast
import time
from collections import Counter

# Keywords to filter log entries
KEYWORDS = ["Application Will Terminate", "PostGameCelebration", "Tags: {'", "equipping trainings", "Num Trainings: 2"]
KEYWORDS.extend(["EMatchPhase::VersusScreen", "LogPMSkinDataManager: UPMSkinDataManagerComponent::DetermineLobbyAnimation",
"EMatchPhase::CharacterSelect"])  # Marks the start of a new game

CURRENT_GAME_LOGS = []  # List to store the current logs of the current game
DICT_IGN_TRAININGS = {}  # Dictionary to map player IGNs to their trainings
CHARACTERS_IN_LOBBY = []  # List of character names in the lobby
PLAYER_LIST = []  # Convenience list for player IGNs

#DISPLAYED_PLAYER_LIST
#DISPLAYED_CHARACTERS_IN_LOBBY

# Internal to external character names mapping
dict_internal_to_external = {
    "C_AngelicSupport_C": "Atlas", "C_ChaoticRocketeer_C": "Luna", "C_CleverSummoner_C": "Juno",
    "C_EDMOni_C": "Octavia", "C_EmpoweringEnchanter_C": "Era", "C_FlashySwordsman_C": "Zentaro",
    "C_FlexibleBrawler_C": "Juliette", "C_GravityMage_C": "Finii", "C_HulkingBeast_C": "X",
    "C_MagicalPlaymaker_C": "Ai.Mi", "C_ManipulatingMastermind_C": "Rune", "C_NimbleBlaster_C": "Drek'ar",
    "C_RockOni_C": "Vyce", "C_Shieldz_C": "Asher", "C_SpeedySkirmisher_C": "Kai",
    "C_StalwartProtector_C": "Dubu", "C_TempoSniper_C": "Estelle", "C_UmbrellaUser_C": "Kazan",
    "C_WhipFighter_C": "Rasmus", "C_Healer_C": "Nao", "C_DrumOni_C": "Mako",

    "AngelicSupport": "Atlas", "ChaoticRocketeer": "Luna", "CleverSummoner": "Juno",
    "EDMOni": "Octavia", "EmpoweringEnchanter": "Era", "FlashySwordsman": "Zentaro",
    "FlexibleBrawler": "Juliette", "GravityMage": "Finii", "HulkingBeast": "X",
    "MagicalPlaymaker": "Ai.Mi", "ManipulatingMastermind": "Rune", "NimbleBlaster": "Drek'ar",
    "RockOni": "Vyce", "ShieldUser": "Asher", "SpeedySkirmisher": "Kai",
    "StalwartProtector": "Dubu", "TempoSniper": "Estelle", "UmbrellaUser": "Kazan",
    "WhipFighter": "Rasmus", "Healer": "Nao", "DrumOni": "Mako",
}   #bottom half is used for reading lines with "DetermineLobbyAnimation". asher's arbitrarily is different [Shieldz and ShieldUser]

# Check if Omega Strikers window is open
def is_omega_strikers_window_open():
    game_title = "OmegaStrikers"
    windows = pygetwindow.getAllWindows()
    for window in windows:
        if game_title in window.title:
            return True
    print("Omega strikers is not running. closing app.")
    return False  # Set to True for testing; change to False for actual use

class LogEventHandler(FileSystemEventHandler):
    def __init__(self, log_file_path, update_signal):
        super().__init__()
        self.log_file_path = log_file_path
        self.file_size = 0  # Track the last read position in the file
        self.update_signal = update_signal  # Signal to communicate with the GUI

    def on_modified(self, event):
        if not event.is_directory and event.src_path == self.log_file_path:
            current_size = os.path.getsize(self.log_file_path)

            with open(self.log_file_path, "r", encoding="utf-8") as file:
                file.seek(self.file_size)
                new_content = file.read()

            self.file_size = current_size
            log_lines = new_content.splitlines()
            for line in log_lines:
                cleaned_line = re.sub(r'^\[.*?\]\[.*?\]', '', line).strip()  # Remove brackets and trim whitespace

                if any(keyword in cleaned_line for keyword in KEYWORDS):
                    # Soft reset if new game is detected
                    #time.sleep(0.01)
                    if "Current[EMatchPhase::CharacterSelect]" in cleaned_line:
                        time.sleep(0.1)
                        self.reset_global_lists()
                        self.update_signal.emit("reset_dropzone_display")
                    # Avoid duplicate log entries
                    if cleaned_line not in CURRENT_GAME_LOGS:
                        if("LogPMSkinDataManager: UPMSkinDataManagerComponent::DetermineLobbyAnimation" in cleaned_line):
                            #then we need to check if EMatchPhase::VersusScreen is a substring in an element of CURRENT_GAME_LOGS which is a list of strings.
                            if(any("EMatchPhase::VersusScreen" in log_line for log_line in CURRENT_GAME_LOGS)== False): #check
                                continue #if EmatchPhase::VersusScreen is not in the logs, then we should not append the current line.

                        CURRENT_GAME_LOGS.append(cleaned_line)
                        #time.sleep(0.1)
                        #self.update_signal.emit(cleaned_line)  # Emit signal for new log entry

                        # Extract character tags and convert to external names

                        if "LogPMSkinDataManager: UPMSkinDataManagerComponent::DetermineLobbyAnimation" in cleaned_line:
                            if(len(CHARACTERS_IN_LOBBY)<6):
                                #print(f"line 109 Characters in the lobby so far {CHARACTERS_IN_LOBBY}")
                                match = re.search(r"SD_([^_]+)", cleaned_line)
                                if match:
                                    extracted_value = match.group(1)
                                    converted_value = dict_internal_to_external.get(extracted_value)

                                # Optionally, handle the case where the key might not exist
                                if converted_value is None:
                                    continue
                                else:
                                    print("Converted value:", converted_value)
                                    if (converted_value not in CHARACTERS_IN_LOBBY):
                                        CHARACTERS_IN_LOBBY.append(converted_value)
                                    if(len(CHARACTERS_IN_LOBBY)>5):
                                        time.sleep(0.1)
                                        print(f"line 112, all 6 characters in the lobby: {CHARACTERS_IN_LOBBY}")
                                        self.update_signal.emit("update_characters_display")  # Emit signal to update characters
                        # Update player trainings with external names
                        if "equipping trainings" in cleaned_line:
                            match = re.search(r"Player '(.+?)' equipping trainings (.*)", cleaned_line)
                            if match:
                                player = match.group(1)
                                if player not in PLAYER_LIST:
                                    PLAYER_LIST.append(player)  # Add player to PLAYER_LIST
                                    #time.sleep(0.1)
                                    #print(f"line 98 printing player_list {PLAYER_LIST}")
                                    if(len(PLAYER_LIST)==6):
                                        print(f"line 99 printing player_list {PLAYER_LIST}")
                                        time.sleep(0.1)
                                        self.update_signal.emit("update_player_display")  # Emit signal to update players

                                trainings = [dict_internal_to_external.get(t, t) for t in re.findall(r"TD_\w+", match.group(2)) if t.startswith("TD_")]
                                existing_trainings = DICT_IGN_TRAININGS.get(player, [])  # Use get to avoid KeyError
                                if existing_trainings == trainings:
                                    pass
                                    #print(f"Trainings for player {player} have not changed.")
                                else:
                                    # Update the trainings list and trigger the function
                                    time.sleep(0.01)
                                    #print(f"Trainings for player {player} have changed.")
                                    DICT_IGN_TRAININGS[player] = trainings
                                    # Call the function you want to trigger when the trainings change
                                    self.update_signal.emit("equipped_awakenings_has_changed")  # Emit signal to update players


                        if "Application Will Terminate" in cleaned_line:
                            time.sleep(0.01)
                            self.update_signal.emit(cleaned_line)
                            print(f"Application will terminate line found. we should end this program.")

    def reset_global_lists(self):
        CURRENT_GAME_LOGS.clear()
        DICT_IGN_TRAININGS.clear()
        CHARACTERS_IN_LOBBY.clear()
        PLAYER_LIST.clear()
        print("Starting new game - logs, trainings, character data, and player list reset.")


class DraggableLabel(QLabel):
    def __init__(self, player_name=None, character_name=None, image_path=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if player_name is None and character_name is None and image_path is None:
            raise ValueError("DraggableLabel needs to be either a player or character")

        self.player_name = player_name
        self.character_name = character_name
        self.image_path = image_path  # Store the image path

        self.isPlayer = image_path is None  # True if no image path provided
        self.isCharacter = not self.isPlayer  # True if image path is provided
        self.setContentsMargins(5, 5, 5, 5)  # 3 pixels padding on all sides
        if self.isPlayer and self.player_name:
            self.setText(self.player_name)
            # Set a custom font with a larger size
            font = QFont()
            font.setPointSize(16)  # Adjust the font size as needed
            self.setFont(font)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        drag = QDrag(self)
        mime_data = QMimeData()

        # Set the character or player name in mime data text
        if self.isCharacter:
            mime_data.setText(self.character_name)
            mime_data.setData("application/is-character", b"true")  # Custom flag for character
        elif self.isPlayer:
            mime_data.setText(self.player_name)
            mime_data.setData("application/is-player", b"true")  # Custom flag for player

        # Set the image data if available
        if self.image_path:
            mime_data.setUrls([QUrl.fromLocalFile(self.image_path)])  # Set URL for the image file
            pixmap = QPixmap(self.image_path)  # Load the image
            mime_data.setImageData(pixmap)  # Set the image in mime data

        drag.setMimeData(mime_data)

        # Set a pixmap for visual feedback during the drag
        if self.image_path:
            pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio)  # Scale the pixmap if needed
            drag.setPixmap(pixmap)
        drag.exec_(Qt.MoveAction)

    def dropEvent(self, event):
        print('line 210 DROP EVENT')
        # Here we check if the dragged item is valid
        mime_data = event.mimeData()

        if mime_data.hasText():
            # Check if the dragged text is still valid
            dragged_text = mime_data.text()

            # Replace this with the actual validation logic
            if not self.is_valid_item(dragged_text):
                print(f"Dropped item '{dragged_text}' is no longer available. Ignoring drop.")
                event.ignore()  # Ignore the drop if the item is invalid
                return

            # Proceed with processing the drop
            self.handle_drop(dragged_text)

        event.accept()  # Accept the event if it is valid


class DropZone(QFrame):
    def __init__(self, slot_type, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        #self.setFrameStyle(QFrame.Sunken)
        #self.setStyleSheet("background-color: black;")

        if (slot_type == "Player"):
            self.setMinimumSize(140, 80)
            self.setFixedSize(140, 80)

        else:
            self.setMinimumSize(80, 80)
            self.setFixedSize(80, 80)

        self.slot_type = slot_type  # Store the slot type (Player or Character)
        self.setProperty("slot_type", slot_type)
        self.text = ""
        self.character_image_path = None

    def set_text(self, new_text):
        self.text = str(new_text)

    def get_text(self):
        return self.text

    def set_character_image_path(self, new_image_path):
        self.character_image_path = str(new_image_path)

    def get_character_image_path(self):
        return self.character_image_path



    def dragEnterEvent(self, event):
        if event.mimeData().hasText() or event.mimeData().hasImage():
            event.accept()
        else:
            event.ignore()


    def dropEvent(self, event):
        mime_data = event.mimeData()

        source_widget = event.source()  # This gets the source widget of the drag event
        player_name = source_widget.player_name
        character_name = source_widget.character_name
        image_path = source_widget.image_path
        is_player = source_widget.isPlayer
        is_character = source_widget.isCharacter


        if is_player or is_character:
            name = mime_data.text()
            # Check the type of slot (Player or Character)
            if self.slot_type == "Player" and is_player:
                self.handle_player_drop(name)
            elif self.slot_type == "Character" and is_character:
                self.character_image_path = image_path
                self.handle_character_drop(name)

            event.accept()
        else:
            event.ignore()

    def handle_player_drop(self, player_name):
        # Implement logic to handle the player drop
        self.text = player_name
        # TODO: call function that prints to overlay output file.
        print(f"Dropped player: {player_name}")
        parent_widget = self.parent()
        if hasattr(parent_widget, 'write_to_text_overlay_output'):
            parent_widget.write_to_text_overlay_output()  # Call the function on the parent widget

        self.update()
        if parent_widget:
            #parent_widget.adjustSize()
            parent_widget.repaint()

    def handle_character_drop(self, character_name):
        # Implement logic to handle the character drop


        print(f"Dropped character: {character_name}")
        self.text= character_name

        parent_widget = self.parent()


    # Check if the parent widget has the method you want to call
        if hasattr(parent_widget, 'write_to_text_overlay_output'):
            parent_widget.write_to_text_overlay_output()  # Call the function on the parent widget

        self.update()
        if parent_widget:
            #parent_widget.adjustSize()
            parent_widget.repaint()

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)
        if self.character_image_path:
            pixmap = QPixmap(self.character_image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image_rect = scaled_pixmap.rect()
                image_rect.moveCenter(self.rect().center())
                painter.drawPixmap(image_rect, scaled_pixmap)
        else:
            painter.fillRect(self.rect(), QColor(255, 255, 255))
            painter.setPen(Qt.black)
            painter.setFont(QFont('Arial', 14))
            painter.drawText(self.rect(), Qt.AlignCenter, self.text)
class LogViewer(QWidget):
    new_log_entry = pyqtSignal(str)


    def __init__(self):
        super().__init__()
        self.initUI()
        self.new_log_entry.connect(self.display_log_entry)



    def initUI(self):
        self.setWindowTitle("Omega Strikers Overlay Config")
        self.setGeometry(100, 100, 700, 450)


        #self.setWindowFlags(Qt.Window | Qt.MSWindowsFixedSizeDialogHint) # disables resizing

        main_layout = QVBoxLayout()

        # Players display area
        self.players_layout = QHBoxLayout()
        # Add label 'IGNs' to indicate that these are nicknames
        ign_label = QLabel("IGNs")  # Create the label
        ign_label.setAlignment(Qt.AlignLeft)  # Center align the text (optional)
        ign_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Fix the size policy

        self.players_layout.addWidget(ign_label)  # Add the label to the layout

        self.players_labels = []
        main_layout.addLayout(self.players_layout)

        # Characters display area
        self.characters_layout = QHBoxLayout()
        self.character_labels = []
        main_layout.addLayout(self.characters_layout)

        self.swap_button = QPushButton("Swap Teams")
        self.swap_button.clicked.connect(self.swap_team_contents)  # Connect button click to method
        self.swap_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.swap_button.setFixedHeight(30)
        main_layout.addWidget(self.swap_button, alignment=Qt.AlignCenter)  # Center the button
        # Team layout
        team_layout = QHBoxLayout()  # Changed to QHBoxLayout for side-by-side stacking

        # Blue team layout
        self.blue_team_layout = QVBoxLayout()
        self.blue_team_layout.addWidget(QLabel("Blue Team"))

        self.blue_team_slots = []
        for _ in range(3):
            # Create a horizontal layout for each player-character pair
            slot_layout = QHBoxLayout()
            # Create player and character slots
            player_slot = self.create_drop_slot("Player")
            character_slot = self.create_drop_slot("Character")
            # Add the player and character slots to the horizontal layout
            slot_layout.addWidget(player_slot)
            slot_layout.addWidget(character_slot)
            # Add the horizontal layout to the blue team layout
            self.blue_team_layout.addLayout(slot_layout)
            # Store the slots for later reference
            self.blue_team_slots.append((player_slot, character_slot))
            #self.drop_zones.extend([player_slot, character_slot])

        # Red team layout
        self.red_team_layout = QVBoxLayout()
        self.red_team_layout.addWidget(QLabel("Red Team"))

        self.red_team_slots = []
        for _ in range(3):
            # Create a horizontal layout for each player-character pair in the red team
            slot_layout = QHBoxLayout()

            # Create player and character slots
            player_slot = self.create_drop_slot("Player")
            character_slot = self.create_drop_slot("Character")
            # Add the player and character slots to the horizontal layout
            slot_layout.addWidget(player_slot)
            slot_layout.addWidget(character_slot)

            # Add the horizontal layout to the red team layout
            self.red_team_layout.addLayout(slot_layout)

            # Store the slots for later reference
            self.red_team_slots.append((player_slot, character_slot))
            #self.drop_zones.extend([player_slot, character_slot])

        # Add both team layouts to the main team layout
        team_layout.addLayout(self.blue_team_layout)  # Add blue team layout
        team_layout.addLayout(self.red_team_layout)  # Add red team layout

        # Finally, set the main_layout to the central widget of the window
        main_layout.addLayout(team_layout)  # Add team layout to main layout

        self.setLayout(main_layout)  # Ensure this is set to your main widget

    def swap_team_contents(self):
        for (blue_player_widget, blue_character_widget), (red_player_widget, red_character_widget) in zip(self.blue_team_slots, self.red_team_slots):
            # Swap player text
            blue_player_text_temp = blue_player_widget.get_text()
            red_player_text_temp = red_player_widget.get_text()
            blue_player_widget.set_text(red_player_text_temp)
            red_player_widget.set_text(blue_player_text_temp)

            # Swap character image paths



            blue_character_image_path_temp = blue_character_widget.get_character_image_path()
            red_character_image_path_temp = red_character_widget.get_character_image_path()
            blue_character_widget.set_character_image_path(red_character_image_path_temp)
            red_character_widget.set_character_image_path(blue_character_image_path_temp)

            blue_character_text_temp = blue_character_widget.get_text()
            red_character_text_temp = red_character_widget.get_text()
            blue_character_widget.set_text(red_character_text_temp)
            red_character_widget.set_text(blue_character_text_temp)



            self.update()
            # If you want to update the GUI representation (like showing images), you'll need to implement that logic as well.
            self.write_to_text_overlay_output()

    def first_drop_zone_at_pos(self, pos):
    # Convert the position to global coordinates
        global_pos = self.mapToGlobal(pos)

        #print(pos)
        # Loop through all child widgets
        for child in self.findChildren(QFrame):  # Use QFrame if drop zones are QFrames
            #print(child)
            # Check if the child is a drop zone by examining its slot_type property
            slot_type = child.property("slot_type")
            if slot_type in ["Character", "Player"]:  # Check if the slot_type is relevant
                # Convert the child's geometry to global coordinates
                child_geometry = child.geometry()
                child_global_pos = child.mapToGlobal(QPoint(0, 0))

                if QRect(child_global_pos, child_geometry.size()).contains(global_pos):
                    return child  # Return the first drop zone found

        return None  # Return None if no drop zone is found

    def create_drop_slot(self, slot_type):
        drop_slot = DropZone(slot_type)  # Use the DropZone class here
        return drop_slot

    def dragEnterEvent(self, event):
        print('line496')
        #if event.mimeData().hasText() or event.mimeData().hasImage():
        event.accept()
        #else:
        #    event.ignore()

    def dropEvent(self, event):
        # Accept the drop event
        print('line504')
        event.accept()
        # Get the drop zone that received the drop event

        mime_data = event.mimeData()
        is_character = mime_data.data("application/is-character") == b"true"
        is_player = mime_data.data("application/is-player") == b"true"

        #print('line304')
        #print(is_character)
        #print(is_player)

        if is_character or is_player:
            #print('line 259')
            # Get the slot type from the drop zone

            print(mime_data.hasImage())
            if is_character:
                #print('line 267')
                # Handle character drops
                character_image_path = mime_data.urls()[0].toLocalFile() if mime_data.urls() else None

                print(f"Dropped character image path: {character_image_path}")
                pixmap = QPixmap(character_image_path)  # Load the image as a pixmap
                self.handleDrop("Character", pixmap, event)
            elif is_player:
                # Handle player drops
                text_data = mime_data.text()  # Get the dropped text data (e.g., player name)
                print(f"Dropped player: {text_data}")
                #if(mime_data.)
                self.handleDrop("Player", text_data, event)


    def handleDrop(self, slot_type, item, event):
        #print('line 330')
        drop_zone = event.source()#self.sender()  # Get the drop zone that received the drop event
        drop_zone = self.first_drop_zone_at_pos(event.pos())
        #print(drop_zone)
        print("Object name:", drop_zone.objectName())
        print("Text:", drop_zone.text())
        print("Position:", drop_zone.pos())
        print("Size:", drop_zone.size())


        print(drop_zone)
        if slot_type == "Character" and isinstance(item, QPixmap):
            label = QLabel()  # Create a new label for the character
            label.setPixmap(item.scaled(80, 80, Qt.KeepAspectRatio))  # Scale the pixmap if needed
            drop_zone.setLayout(QVBoxLayout())  # Set layout for the drop zone if not already set
            drop_zone.layout().addWidget(label)  # Add the character label to the drop zone
        elif slot_type == "Player" and isinstance(item, str):
            label = QLabel(item)  # Create a label for the player name
            drop_zone.setLayout(QVBoxLayout())  # Set layout for the drop zone if not already set
            drop_zone.layout().addWidget(label)  # Add the player label to the drop zone



    def update_player_display(self):
        # Clear existing players
        global PLAYER_LIST
        #print('line 206')
        if(len(self.players_labels)==0):
            print('566')
            # build player display
            #print(PLAYER_LIST)
            for player in PLAYER_LIST:
                player_label = DraggableLabel(player_name=str(player),character_name=None, image_path=None)
                self.players_labels.append(player_label)
                self.players_layout.addWidget(player_label)

        else:
            for index, player_label in enumerate(self.players_labels):
                player_label.player_name = str(PLAYER_LIST[index])
                print('line577')
                print(player_label.player_name)

                player_label.player_text = str(PLAYER_LIST[index])
                player_label.text= str(PLAYER_LIST[index])
                player_label.setText(str(PLAYER_LIST[index]))
                player_label.show()  # Show the label
                self.update()
        # Debugging output
        #print(PLAYER_LIST)
        #print("Player names updated:", [label.text() for label in self.players_labels])  # Log the current player names

    def update_character_display(self):
        # Clear existing characters
        global CHARACTERS_IN_LOBBY
        if(len(self.character_labels)==0):
            print('line594')
            for character in CHARACTERS_IN_LOBBY:  # Assuming this is your list of characters
                character_image_path = os.path.join('images', f'{character}.png')  # Ensure this is the correct path
                character_pixmap = QPixmap(character_image_path)  # Load the image as QPixmap

                if not character_pixmap.isNull():  # Check if the image was loaded successfully
                    character_label = DraggableLabel(player_name=None,character_name= str(character), image_path=str(character_image_path))  # Pass both arguments
                    print(f"line 601: {character_label.character_name},{character_label.image_path},{character_label.player_name}, ")
                    #self, player_name=None, character_name=None, image_path=None, *args, **kwargs)
                    character_label.setPixmap(character_pixmap.scaled(80, 80, Qt.KeepAspectRatio))  # Example scaling
                    character_label.show()  # Show the label


                    # Add to the layout and store in the labels list
                    self.character_labels.append(character_label)
                    self.characters_layout.addWidget(character_label)
                else:
                    print(f"Failed to load image for character: {character}")
        else:
            # Update existing labels with new attributes
            for index, character_label in enumerate(self.character_labels):

                character_name = str(CHARACTERS_IN_LOBBY[index])
                character_label.text = str(character_name)
                character_label.character_name = str(character_name)
                #character_label.setText(character_name)

                character_image_path = os.path.join('images', f'{str(character_name)}.png')  # Get the updated path
                character_pixmap = QPixmap(str(character_image_path))  # Load the image as QPixmap

                if not character_pixmap.isNull():  # Check if the image was loaded successfully
                        # Update the label's pixmap and any other attributes as necessary

                    character_label.setPixmap(character_pixmap.scaled(80, 80, Qt.KeepAspectRatio))  # Update pixmap
                    character_label.image_path = str(character_image_path)  # Update image_path attribute if needed
                    print(f"line 628: {character_label.character_name},{character_label.image_path},{character_label.player_name}, ")
                    character_label.show()  # Show the label
                    self.update()
                else:
                    print(f"Failed to load updated image for character: {character_name}")

    def print_data_dropzones(self):
        player_names = []
        character_names = []

        # Iterate over blue team slots
        for player_slot, character_slot in self.blue_team_slots:
            # Access player name directly from the DropZone's text attribute
            if player_slot.slot_type == "Player" and player_slot.text:
                player_names.append(player_slot.text)

            # Access character name directly from the DropZone's text attribute
            if character_slot.slot_type == "Character" and character_slot.text:
                character_names.append(character_slot.text)

        # Repeat for red team slots
        for player_slot, character_slot in self.red_team_slots:
            if player_slot.slot_type == "Player" and player_slot.text:
                player_names.append(player_slot.text)

            if character_slot.slot_type == "Character" and character_slot.text:
                character_names.append(character_slot.text)

        # Print gathered data
        print("Going through dropzones to get Player Names and Character Names:")
        print("Player Names:", player_names)
        print("Character Names:", character_names)


        return player_names, character_names




    def write_to_text_overlay_output(self):
        #looks at the dropzones, and prints out the intented organised output file.
        #TODO only prints right now. write to a notepad!
        playerlist, characterlist = self.print_data_dropzones()
        #print('line584')
        print(f"Current Players in corresponding dropzones: {', '.join(playerlist)}")
        print(f"Current Characters in corresponding dropzones: {', '.join(characterlist)}")
        print(f"This is the unorganized dict: {DICT_IGN_TRAININGS}")


        # Initialize a list to hold the formatted strings for each player
        indexed_overlay_of_players_characters_trainings = []

        # Iterate over the playerlist and characterlist
        for i in range(len(playerlist)):
            player = playerlist[i]
            character = characterlist[i] if i < len(characterlist) else None  # Handle potential mismatches in length
            trainings = DICT_IGN_TRAININGS.get(player, [])  # Get the trainings, defaulting to an empty list if not found

            # Create the formatted string
            trainings_str = ', '.join(trainings)
            indexed_overlay_of_players_characters_trainings.append(f"{player}, {character}, {trainings_str}")


        # Join the list into a single string with line breaks between each entry
        print('here are the organized players, characters, and their trainings.')
        print("\n".join(indexed_overlay_of_players_characters_trainings))
        return "\n".join(indexed_overlay_of_players_characters_trainings)

    def display_log_entry(self, log_message): # this receives a signal from on_modified():
        #let's process the entry here.
        #self.update_signal.emit("update_player_display")
        #self.update_signal.emit("update_characters_display")
        #print(f"Log Entry: {entry}")  # For debugging
        if "Application Will Terminate" in log_message:
            self.print_data_dropzones()
            #TODO exit

        if "update_characters_display" == log_message:
            #print('found log message that apllication will terminate')
            self.update_character_display()
        elif "update_player_display" == log_message:
            #print('found log message that apllication will terminate')
            self.update_player_display()

        elif "reset_dropzone_display" == log_message:
            #we dont need this anymore?
            self.print_data_dropzones()

        elif "equipped_awakenings_has_changed" == log_message:
            self.write_to_text_overlay_output()
def main():
    if (is_omega_strikers_window_open() is False):
        return
    app = QApplication(sys.argv)
    viewer = LogViewer()

    log_file_path =os.path.join(os.getenv('LOCALAPPDATA'), 'OmegaStrikers', 'Saved', 'Logs', 'OmegaStrikers.log')

    # Start log monitoring in a separate thread
    thread = QThread()
    observer = Observer()
    event_handler = LogEventHandler(log_file_path, viewer.new_log_entry)
    observer.schedule(event_handler, os.path.dirname(log_file_path), recursive=False)
    observer.start()

    viewer.show()

    # =
    # Append a '.' to the log file
    #with open(log_file_path, 'a') as log_file:  # 'a' mode opens the file for appending
    #    log_file.write('.\n')  # Write the dot and add a newline for readability

    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
