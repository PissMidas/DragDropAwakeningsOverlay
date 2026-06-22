from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy, QPushButton
from PyQt5.QtCore import pyqtSignal, Qt, QObject, QThread, QMimeData, QPoint, QRect, QUrl,QCoreApplication, QTimer
from PyQt5.QtGui import QPixmap, QDrag, QPainter, QFont, QColor, QIcon
import os
import sys
import pygetwindow
import re
import ast
import time
import asyncio
import json
import threading
from aiohttp import web
from collections import Counter
import tkinter as tk
from tkinter import messagebox, ttk

#pyinstaller --onefile --noconsole --icon=images/nao_thumbnail.ico --add-data "images;images" --name "DragnDropAwakeningsOverlay" main.py
#use this to compile this program in a single file executable.

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

'''
dict_internal_to_external.update({"CD_AngelicSupport": "Atlas", "CD_ChaoticRocketeer": "Luna", "CD_CleverSummoner": "Juno",
"CD_EDMOni": "Octavia", "CD_EmpoweringEnchanter": "Era", "CD_FlashySwordsman": "Zentaro",
"CD_FlexibleBrawler": "Juliette", "CD_GravityMage": "Finii", "CD_HulkingBeast": "X",
"CD_MagicalPlaymaker": "Ai.Mi", "CD_ManipulatingMastermind": "Rune", "CD_NimbleBlaster": "Drek'ar",
"CD_RockOni": "Vyce", "CD_ShieldUser": "Asher", "CD_SpeedySkirmisher": "Kai",
"CD_StalwartProtector": "Dubu", "CD_TempoSniper": "Estelle", "CD_UmbrellaUser": "Kazan",
"CD_WhipFighter": "Rasmus", "CD_Healer": "Nao", "CD_DrumOni": "Mako",})
'''


dict_internal_to_external_CD={"CD_AngelicSupport": "Atlas", "CD_ChaoticRocketeer": "Luna", "CD_CleverSummoner": "Juno",
"CD_EDMOni": "Octavia", "CD_EmpoweringEnchanter": "Era", "CD_FlashySwordsman": "Zentaro",
"CD_FlexibleBrawler": "Juliette", "CD_GravityMage": "Finii", "CD_HulkingBeast": "X",
"CD_MagicalPlaymaker": "Ai.Mi", "CD_ManipulatingMastermind": "Rune", "CD_NimbleBlaster": "Drek'ar",
"CD_RockOni": "Vyce", "CD_ShieldUser": "Asher", "CD_SpeedySkirmisher": "Kai",
"CD_StalwartProtector": "Dubu", "CD_TempoSniper": "Estelle", "CD_UmbrellaUser": "Kazan",
"CD_WhipFighter": "Rasmus", "CD_Healer": "Nao", "CD_DrumOni": "Mako"
} #used only when building a json to send to a websocket.


DICT_INTERNAL_TO_EXTERNAL_AWAKENINGS = {"TD_AvoidDamageHitHarder": "Glass Cannon", "TD_BarrierBuff": "Demolitionist", "TD_BaseStaggerAndRegen": "Reptile Remedy", "TD_BlessingCooldownRate": "Spark of Focus", "TD_BlessingMaxStagger": "Spark of Resilience", "TD_BlessingPower": "Spark of Strength", "TD_BlessingShare": "Spark of Leadership", "TD_BlessingSpeed": "Spark of Agility", "TD_BuffAndDebuffDuration": "Cast to Last", "TD_ComboATarget": "One-Two Punch", "TD_CreationSize": "Monumentalist", "TD_CreationSizeLifeTime": "Timeless Creator", "TD_DistancePower": "Deadeye", "TD_EdgePower": "Knife's Edge", "TD_EmpoweredHitsBuff": "Specialized Training", "TD_EnergyCatalyst": "Catalyst", "TD_EnergyConversion": "Egoist", "TD_EnergyDischarge": "Fire Up!", "TD_EnhancedOrbsCooldown": "Orb Ponderer" , "TD_EnhancedOrbsSpeed": "Orb Dancer", "TD_FasterDashes": "Super Surge", "TD_FasterDashes2": "Chronoboost", "TD_FasterDashes3": "Explosive Entrance", "TD_FasterProjectiles": "Missile Propulsion", "TD_FasterProjectiles2": "Aerials", "TD_FasterProjectiles3":"Siege Machine", "TD_HitAnythingRestoreStagger": "Tempo Swing", "TD_HitEnemyBurnThem": "Stinger", "TD_HitRockCooldown": "Hotshot", "TD_HitsIncreaseSpeedAndPower": "Stacks On Stacks", "TD_HitSpeed": "Fight Or Flight", "TD_HitsReduceCooldowns": "Perfect Form", "TD_IncreasedPowerWithMaxStagger": "OLD Unstoppable", "TD_IncreasedSpeedWithStagger": "Stagger Swagger", "TD_KOKing": "Prize Fighter", "TD_MovementAbilityCharges": "Twin Drive", "TD_MultiHitsReduceCooldowns": "Heavy Impact", "TD_OrbShare": "Orb Replicator", "TD_PrimaryAbilityCooldownReduction": "Rapid Fire", "TD_PrimaryEcho": "Primetime", "TD_ResistFirstHit": "Unstoppable", "TD_Revive":"Recovery Drone", "TD_ShrinkSelfGrowAllies": "Among Titans", "TD_SizeIncrease": "Built Different", "TD_SizeIncrease2": "Big Fish", "TD_SizePowerConversion": "Might of the Colossus", "TD_SpecialCooldownAfterRounds": "Extra Special", "TD_StackingSize": "Rampage", "TD_StaggerCooldownRateConversion": "Reverberation", "TD_StaggerPowerConversion": "Bulk Up", "TD_StaggerSpeedConversion": "Peak Performance", "TD_StrikeCooldownReduction": "Quick Strike", "TD_StrikeRockTowardsAllies": "Team Player", "TD_TakeDownReduceCooldowns": "Adrenaline Rush", "TD_AvoidKnockoutGainSpeed": "Omega Infused Accelerator", "TD_IncreasedStatsWhileStaggered": "Berserker", "TD_HitCoreGainCDR": "Inner Focus" }

DICT_INTERNAL_TO_EXTERNAL_AWAKENINGS.update({"TD_MovementAbilitiesTeleport": "Eject Button", "TD_IncreasedSpeedCrossingMidfield": "Magnetized Soles", "TD_GainRampingSpeed": "Momentum Boots", "TD_HitEnemyDrainThem": "Siphoning Wand", "TD_GoalArcPower": "Powerhouse Pauldrons", "TD_HitStaggerEnemyCooldownReduction": "Pummelers", "TD_StrikeRockSpeedUp": "Slick Kicks", "TD_RangedStrike": "Strike Shot", "TD_KnockAnythingRecoverStagger": "Vicious Vambraces" })


# Cache to hold the most recent live JSON structure for newly connecting clients
LAST_VALID_PAYLOAD = {"blue": [], "red": []}


# Global set to track active OBS browser connections across threads

CONNECTED_CLIENTS = set()

async def handle_blue_page(request):
    return web.FileResponse('website/blue.html')

async def handle_red_page(request):
    return web.FileResponse('website/red.html')

async def handle_websocket(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # 1. Add the client to the connected set
    CONNECTED_CLIENTS.add(ws)
    print("Connected to overlay server as blue/red team.")

    # 2. IMMEDIATELY send the last known live layout state right after connection
    try:
        # Pushes the cached live data (or the empty template if no broadcast has happened yet)
        await ws.send_str(json.dumps(LAST_VALID_PAYLOAD))
        print("Initial live state payload pushed to connected browser tab.")
    except Exception as e:
        print(f"Failed to send initial payload: {e}")

    # 3. Keep the connection alive
    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT and msg.data == 'close':
                await ws.close()
    finally:
        CONNECTED_CLIENTS.remove(ws)

    return ws
def start_asyncio_server(viewer):
    # Standard threads do not have an active asyncio loop by default; one must be created manually
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app = web.Application()

    # Map the URL endpoints to their respective handler functions
    app.router.add_get('/blue', handle_blue_page)
    app.router.add_get('/red', handle_red_page)
    app.router.add_get('/', handle_websocket)

    # Route to allow blue.html and red.html to fetch local files like overlay.js or styles.css
    app.router.add_static('/', path='website', name='website')

    # Bind the application to the network port
    runner = web.AppRunner(app)
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, 'localhost', 8765)
    loop.run_until_complete(site.start())

    # Keep the thread loop alive indefinitely to process network traffic
    loop.run_forever()

def broadcast_to_overlay(payload_dict):
    """Serializes the data dictionary and safely dispatches it to the async server thread."""
    global LAST_VALID_PAYLOAD

    # Early exit if the new state matches the previously broadcasted state
    if payload_dict == LAST_VALID_PAYLOAD:
        return

    LAST_VALID_PAYLOAD = payload_dict  # Save the new live data to the cache

    json_string = json.dumps(payload_dict)

    active_clients = list(CONNECTED_CLIENTS)
    print(f"Attempting broadcast to {len(active_clients)} active clients...")

    for ws in active_clients:
        try:
            loop = ws._req.app.loop if hasattr(ws, '_req') else asyncio.get_event_loop()
            if loop and loop.is_running():
                asyncio.run_coroutine_threadsafe(ws.send_str(json_string), loop)
                print("Packet thread-bridge execution scheduled successfully.")
        except Exception as e:
            print(f"Failed to send data packet to client: {e}")
# Check if Omega Strikers window is open
def is_omega_strikers_window_open():
    game_title = "OmegaStrikers"
    windows = pygetwindow.getAllWindows()
    for window in windows:
        if game_title in window.title:
            return True
    print("Omega strikers is not running. closing app.")
    return False  # Set to True for testing; change to False for actual use

def resourcePath(relativePath):
    #Get absolute path to resource, works for dev and for PyInstaller
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        basePath = sys._MEIPASS
    except Exception:
        basePath = os.path.abspath(".")

    return os.path.join(basePath, relativePath)
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

                        time.sleep(0.01)
                        self.reset_global_lists()
                        self.update_signal.emit("reset_dropzone_display")
                    # Avoid duplicate log entries
                    if cleaned_line not in CURRENT_GAME_LOGS:
                        if("LogPMSkinDataManager: UPMSkinDataManagerComponent::DetermineLobbyAnimation" in cleaned_line):
                            #then we need to check if EMatchPhase::VersusScreen is a substring in an element of CURRENT_GAME_LOGS which is a list of strings.
                            if(any("EMatchPhase::VersusScreen" in log_line for log_line in CURRENT_GAME_LOGS)== False): #check
                                continue #if EmatchPhase::VersusScreen is not in the logs, then we should not append the current line.

                        CURRENT_GAME_LOGS.append(cleaned_line)
                        time.sleep(0.01)
                        #self.update_signal.emit(cleaned_line)  # Emit signal for new log entry

                        # Extract character tags and convert to external names

                        if "LogPMSkinDataManager: UPMSkinDataManagerComponent::DetermineLobbyAnimation" in cleaned_line:

                            if(len(CHARACTERS_IN_LOBBY)<6):
                                #print(f"line 109 Characters in the lobby so far {CHARACTERS_IN_LOBBY}")
                                match = re.search(r"SD_([^_]+)", cleaned_line)
                                converted_value = None
                                if match:
                                    extracted_value = match.group(1)
                                    converted_value = dict_internal_to_external.get(extracted_value)

                                # Optionally, handle the case where the key might not exist
                                if converted_value is None:
                                    continue
                                else:
                                    print("Converted value:", converted_value)
                                    if (converted_value not in CHARACTERS_IN_LOBBY):
                                        time.sleep(0.01)
                                        CHARACTERS_IN_LOBBY.append(converted_value)
                                        print(f"line 239, all  characters in the lobby: {CHARACTERS_IN_LOBBY}")

                                    if(len(CHARACTERS_IN_LOBBY)>5):
                                        time.sleep(0.01)
                                        print(f"line 112, all 6 characters in the lobby: {CHARACTERS_IN_LOBBY}")
                                        self.update_signal.emit("update_characters_display")  # Emit signal to update characters
                        # Update player trainings with external names
                        if "equipping trainings" in cleaned_line:
                            match = re.search(r"Player '(.+?)' equipping trainings (.*)", cleaned_line)
                            if match:
                                player = match.group(1)
                                if player not in PLAYER_LIST:
                                    time.sleep(0.01)
                                    PLAYER_LIST.append(player)  # Add player to PLAYER_LIST
                                    #time.sleep(0.1)
                                    #print(f"line 98 printing player_list {PLAYER_LIST}")
                                    if(len(PLAYER_LIST)==6):
                                        print(f"line 99 printing player_list {PLAYER_LIST}")
                                        self.update_signal.emit("update_player_display")  # Emit signal to update players

                                trainings = [dict_internal_to_external.get(t, t) for t in re.findall(r"TD_\w+", match.group(2)) if t.startswith("TD_")]
                                trainings = [DICT_INTERNAL_TO_EXTERNAL_AWAKENINGS.get(t, t) for t in trainings]

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

                            self.update_signal.emit(cleaned_line)
                            print(f"Application will terminate line found. we should end this program.")




    def reset_global_lists(self):
        time.sleep(0.01)
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
        self.setFrameStyle(QFrame.Sunken)

        self.setStyleSheet("background-color: dark grey;")

        if (slot_type == "Player"):
            self.setMinimumSize(160, 80)
            self.setFixedSize(160, 80)

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
            painter.fillRect(self.rect(), QColor(169, 169, 169))
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
        self.setWindowTitle("Drag'n'Drop Awakenings Overlay v1.0.1")
        self.setGeometry(100, 100, 700, 450)
        self.setWindowIcon(QIcon(resourcePath("images/nao_thumbnail.ico")))
        self.setStyleSheet("QMainWindow {background-color: darkgray;}")

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

        ''''
        self.swap_button = QPushButton("Swap Teams")
        self.swap_button.clicked.connect(self.swap_team_contents)  # Connect button click to method
        self.swap_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.swap_button.setFixedHeight(30)
        main_layout.addWidget(self.swap_button, alignment=Qt.AlignCenter)  # Center the button
        '''
        self.clear_button = QPushButton("Clear All")
        self.clear_button.clicked.connect(self.clear_all_dropzones)  # Connect to the new clearing method
        self.clear_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.clear_button.setFixedHeight(30)
        main_layout.addWidget(self.clear_button, alignment=Qt.AlignCenter)


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

            self.write_to_text_overlay_output()
    def clear_all_dropzones(self):
        """Clears the textual data, stored assets, and visual layouts of all team slots, restoring the dark grey background."""
        # Combine both team slot lists to iterate through them cleanly
        all_slots = self.blue_team_slots + self.red_team_slots


        default_grey_style = "background-color: #a9a9a9"

        for player_slot, character_slot in all_slots:
            # 1. Reset the Player DropZone
            player_slot.set_text("")
            player_slot.setStyleSheet(default_grey_style)  # Restore grey look
            if player_slot.layout() is not None:
                while player_slot.layout().count():
                    item = player_slot.layout().takeAt(0)
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()

            # 2. Reset the Character DropZone
            character_slot.set_text("")
            character_slot.set_character_image_path(None)
            character_slot.setStyleSheet(default_grey_style)  # Restore grey look
            if character_slot.layout() is not None:
                while character_slot.layout().count():
                    item = character_slot.layout().takeAt(0)
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()

        # Force a visual update across the interface canvas
        self.update()
        self.repaint()

        # Sync the cleared status out to your network overlay instantly
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
        #if event.mimeData().hasText() or event.mimeData().hasImage():
        event.accept()
        #else:
        #    event.ignore()

    def dropEvent(self, event):
        # Accept the drop event
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
        time.sleep(0.02)
        # Clear existing players
        global PLAYER_LIST

        # Check if there are no labels to update
        if len(self.players_labels) == 0:
            # Build player display
            for player in PLAYER_LIST:
                player_label = DraggableLabel(player_name=str(player), character_name=None, image_path=None)
                self.players_labels.append(player_label)
                self.players_layout.addWidget(player_label)
        else:
            # Iterate over the existing player labels and update them
            for index, player_label in enumerate(self.players_labels):
                if index < len(PLAYER_LIST):  # Ensure that the index does not go out of range
                    try:
                        # Safely update player label with the player's name
                        player_label.player_name = str(PLAYER_LIST[index])
                        player_label.player_text = str(PLAYER_LIST[index])
                        player_label.text = str(PLAYER_LIST[index])
                        print(player_label.player_name)
                        player_label.setText(str(PLAYER_LIST[index]))  # Update the text on the label
                        player_label.show()  # Show the label
                    except Exception as e:
                        print(f"Error updating player label at index {index}: {e}")
                else:
                    print(f"Index {index} is out of range for PLAYER_LIST (length: {len(PLAYER_LIST)})")

            self.update()


    def update_character_display(self):
            # Clear existing characters
            time.sleep(0.001)
            global CHARACTERS_IN_LOBBY
            print('the top of update_character_display')

            if len(self.character_labels) == 0:
                for character in CHARACTERS_IN_LOBBY:  # Assuming this is your list of characters
                    # Use forward slashes inside the string and normalize the entire path
                    character_image_path = os.path.normpath(resourcePath(f"images/{character}.png"))
                    character_pixmap = QPixmap(character_image_path)  # Load the image as QPixmap

                    if not character_pixmap.isNull():  # Check if the image was loaded successfully
                        character_label = DraggableLabel(player_name=None, character_name=str(character), image_path=str(character_image_path))
                        print(f"line 601: {character_label.character_name},{character_label.image_path},{character_label.player_name}, ")
                        character_label.setPixmap(character_pixmap.scaled(80, 80, Qt.KeepAspectRatio))
                        character_label.show()  # Show the label

                        # Add to the layout and store in the labels list
                        self.character_labels.append(character_label)
                        self.characters_layout.addWidget(character_label)
                    else:
                        print(f"Failed to load image for character: {character}")
            else:
                # Update existing labels with new attributes
                for index, character_label in enumerate(self.character_labels):
                    # Safety Check: Prevent IndexError if the lobby list is smaller than the labels pool
                    if index < len(CHARACTERS_IN_LOBBY):
                        character_name = str(CHARACTERS_IN_LOBBY[index])
                        character_label.text = str(character_name)
                        character_label.character_name = str(character_name)

                        # Use forward slashes and normalize the path here as well
                        character_image_path = os.path.normpath(resourcePath(f"images/{character_name}.png"))
                        character_pixmap = QPixmap(character_image_path)  # Load the image as QPixmap

                        if not character_pixmap.isNull():  # Check if the image was loaded successfully
                            character_label.setPixmap(character_pixmap.scaled(80, 80, Qt.KeepAspectRatio))  # Update pixmap
                            character_label.image_path = str(character_image_path)  # Update image_path attribute
                            print(f"line 628: {character_label.character_name},{character_label.image_path},{character_label.player_name}, ")
                            character_label.show()  # Show the label
                        else:
                            print(f"Failed to load updated image for character: {character_name}")
                    else:
                        # Hide excess labels if fewer characters are currently in the lobby
                        character_label.hide()

                self.update()

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



        #write to text, but it instead sends a json to websocket.
    def write_to_text_overlay_output(self):
        """
        Extracts team layouts from the PyQt5 UI slots, structures them into a
        unified 3v3 layout format, and broadcasts the frame over the WebSocket.

        file_path = "website/dummy_overlay.json"
        with open(file_path, "r", encoding="utf-8") as file:
            dummy = json.load(file)
        print("Successfully loaded dummy_overlay.json from disk!")

    # You can now pass it right into your broadcaster
        print(dummy)
        time.sleep(0.05)
        broadcast_to_overlay(dummy)

        print('line827')
        return
        """
        time.sleep(0.01)


        player_count = 0
        character_count = 0

        all_slots = self.blue_team_slots + self.red_team_slots
        for player_slot, character_slot in all_slots:
            p_text = player_slot.get_text().strip() if player_slot.get_text() else ""
            c_text = character_slot.get_text().strip() if character_slot.get_text() else ""

            if p_text:
                player_count += 1
            if c_text and c_text != "No character assigned":
                character_count += 1

        # Early exit if the numbers of players and characters are unequal
        if player_count != character_count:
            print(f"Broadcast skipped: Player count ({player_count}) != Character count ({character_count}).")
            return



        payload = {
            "blue": [],
            "red": []
        }

        # 1. Process Blue Team Slots
        for i in range(3):
            if i < len(self.blue_team_slots):
                player_slot, character_slot = self.blue_team_slots[i]
                player_name = player_slot.get_text().strip() if player_slot.get_text() else ""
                character_name = character_slot.get_text().strip() if character_slot.get_text() else "No character assigned"
            else:
                player_name = ""
                character_name = "No character assigned"

            # Revert character name by looking up the key for the matching value
            internal_character_name = next(
                (k for k, v in dict_internal_to_external_CD.items() if v == character_name),
                character_name  # Fallback if no matching value is found (e.g., "No character assigned")
            )

            # Retrieve external trainings array
            external_trainings = DICT_IGN_TRAININGS.get(player_name, []) if player_name else []

            # Revert each training back to its internal name using your existing dictionary
            internal_trainings = [
                next((k for k, v in DICT_INTERNAL_TO_EXTERNAL_AWAKENINGS.items() if v == t), t)
                for t in external_trainings
            ]

            payload["blue"].append({
                "player": player_name,
                "character": internal_character_name,
                "trainings": internal_trainings
            })

        # 2. Process Red Team Slots
        for i in range(3):
            if i < len(self.red_team_slots):
                player_slot, character_slot = self.red_team_slots[i]
                player_name = player_slot.get_text().strip() if player_slot.get_text() else ""
                character_name = character_slot.get_text().strip() if character_slot.get_text() else "No character assigned"
            else:
                player_name = ""
                character_name = "No character assigned"

            # Revert character name by looking up the key for the matching value
            internal_character_name = next(
                (k for k, v in dict_internal_to_external_CD.items() if v == character_name),
                character_name
            )

            # Retrieve external trainings array
            external_trainings = DICT_IGN_TRAININGS.get(player_name, []) if player_name else []

            # Revert each training back to its internal name using your existing dictionary
            internal_trainings = [
                next((k for k, v in DICT_INTERNAL_TO_EXTERNAL_AWAKENINGS.items() if v == t), t)
                for t in external_trainings
            ]

            payload["red"].append({
                "player": player_name,
                "character": internal_character_name,
                "trainings": internal_trainings
            })
        # 3. Transmit the complete layout frame out to the server
        print(payload)
        broadcast_to_overlay(payload)

    def display_log_entry(self, log_message): # this receives a signal from on_modified():
        #let's process the entry here.
        #self.update_signal.emit("update_player_display")
        #self.update_signal.emit("update_characters_display")
        #print(f"Log Entry: {entry}")  # For debugging

        if "Application Will Terminate" in log_message:
            self.print_data_dropzones()
            #TODO exit
            print("Application will terminate log line found, closing app.")

            QTimer.singleShot(2000, self.close)
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








def main(): #TODO remove return true in is_omega_strikers_window_open() function

    if not is_omega_strikers_window_open():
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        # Show a message box dialog
        messagebox.showinfo("Message", "Omega strikers not found. Exiting app.")
        sys.exit()

    app = QApplication(sys.argv)
    viewer = LogViewer()

    server_thread = threading.Thread(
        target=start_asyncio_server,
        args=(viewer,),
        daemon=True
    )
    server_thread.start() #hosts website


    log_file_path = os.path.join(os.getenv('LOCALAPPDATA'), 'OmegaStrikers', 'Saved', 'Logs', 'OmegaStrikers.log')

    #log_file_path = os.path.normpath("C:/Users/wasdf/Downloads/OmegaStrikers.log")

    # Start log monitoring in a separate thread
    thread = QThread()
    observer = Observer()
    event_handler = LogEventHandler(log_file_path, viewer.new_log_entry)
    observer.schedule(event_handler, os.path.dirname(log_file_path), recursive=False)
    observer.start()

    viewer.show()

    # Append a '.' to the log file. this is for testing: changing the .log file forces the observer to pay attention.

    # with open(log_file_path, 'a') as log_file:  # 'a' mode opens the file for appending
    #     time.sleep(1)
    #     log_file.write('.\n')  # Write the dot and add a newline for readability

    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
