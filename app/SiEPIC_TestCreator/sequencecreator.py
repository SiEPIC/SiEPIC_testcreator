# %%
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication,
    QTextEdit,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QCheckBox,
    QComboBox,
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtWidgets import QLabel, QLineEdit, QVBoxLayout, QWidget, QFormLayout
import os
from os.path import dirname, abspath
import sys
import ast
import yaml
import importlib
import importlib.util
import inspect
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
from SiEPIC_TestCreator.yamlcheck import yaml_check

def launch():
    app = QApplication([])
    ex = GUI()
    ex.show()
    app.exec_()
class GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SiEPIC TestCreator")
        self.custom_sequences_store = dict()
        self.branch = 'IDA'
        self.runtime_max = 100000

        self.yamldict = dict()
        self.yamldict = {"Devices": {}, "Sequences": {}}
        self.runtime_journal = dict()

        # Set up the layout
        self.layout = QVBoxLayout()
        self.hlayout = QHBoxLayout()
        self.setLayout(self.layout)

        # Set up the file selection area
        #self.setup_yaml_selection()
        self.setup_file_selection()

        # Set up the sequence selection area
        self.setup_sequence_selection()

        # Set up the group and devices area
        self.setup_devices()

        self.layout.addLayout(self.hlayout)
        #self.setup_save_folder()

        self.setup_outputlog()
        self.removed_items = self.remove_non_ida_entries(self.sequences_checklist)

    def setup_outputlog(self):
        # Set up the output log
        self.outputtitle = QLabel("Output Log")
        self.layout.addWidget(self.outputtitle)

        # Log Viewer

        self.logTextBox = QTextEditLogger(self)
        self.layout.addWidget(self.logTextBox.widget)

        # Set up logging
        logging.basicConfig(
            format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
        )
        log = logging.getLogger()
        log.addHandler(self.logTextBox)

        # Test logging
        # logging.info("This is an informational message.")

        # Redirect standard output to logging
        std_out_logger = logging.getLogger("STDOUT")
        sl = StreamToLogger(std_out_logger, logging.INFO)
        sys.stdout = sl

        # self.outputtitle = QLabel("Output Log")
        # self.layout.addWidget(self.outputtitle)

        # self.textEdit = QTextEdit()
        # self.textEdit.setReadOnly(True)

        # # Redirect stdout and stderr
        # sys.stdout = StreamRedirector(self.textEdit)
        # sys.stderr = StreamRedirector(self.textEdit)

        # self.layout.addWidget(self.textEdit)

    def setup_file_selection(self):
        self.file_title = QLabel("Upload coordinates file or Yaml file")
        self.file_label = QLineEdit("No file selected")
        self.file_button = QPushButton("Choose File")
        self.file_button.clicked.connect(self.choose_file)

        file_layoutv = QVBoxLayout()
        file_layout = QHBoxLayout()
        file_layoutv.addWidget(self.file_title)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.file_button)
        file_layoutv.addLayout(file_layout)
        self.layout.addLayout(file_layoutv)

    def setup_yaml_selection(self):
        self.yfile_title = QLabel("Upload yaml file")
        self.yfile_label = QLineEdit("No file selected")
        self.yfile_button = QPushButton("Choose File")
        self.yfile_button.clicked.connect(self.choose_yaml_file)

        file_layoutv = QVBoxLayout()
        file_layout = QHBoxLayout()
        file_layoutv.addWidget(self.yfile_title)
        file_layout.addWidget(self.yfile_label)
        file_layout.addWidget(self.yfile_button)
        file_layoutv.addLayout(file_layout)
        self.layout.addLayout(file_layoutv)

    def get_sequences_path(self, branch=None):
    # Determine if running from executable or regular script
        if getattr(sys, 'frozen', False):  
            # Running from executable
            data_dir = Path(sys._MEIPASS)  # Temporary extraction directory
        else:
            # Running as a regular script
            data_dir = Path(__file__).parent.resolve() 

        if branch:
            sequences_path = data_dir / "sequences" / branch
        else:
            sequences_path = data_dir / "sequences"
        return str(sequences_path.resolve())

    def place_sequence_options(self):
        #if self.branch:
        #p = dirname(abspath(__file__))

        p = self.get_sequences_path(self.branch)

        #print(p)

        sequences_dict = DirectoryDict(p)

        self.sequences_checklist = self.create_checklist(sequences_dict.dir_dict)
        self.sequence_versions_checklist = self.create_checklist(
            sequences_dict.dir_dict
        )
        custom_sequences_dict = self.yamldict["Sequences"]
        self.customsequences_checklist = self.create_checklist(
            custom_sequences_dict, customflag=True
        )

    def setup_sequence_selection(self, branch='IDA'):

        self.place_sequence_options()
        
        sequence_hlayout = QHBoxLayout()
        self.sequence_layout = QVBoxLayout()
        edxchoicelayout = QHBoxLayout()


        self.create_checkboxes(edxchoicelayout)

        # self.checkBox1 = QCheckBox("IDA")
        # self.checkBox1.setChecked(True)
        # self.IDAcheck = True
        # self.checkBox2 = QCheckBox("DREAM")
        # self.checkbox3 = QCheckBox("BIO")

        #edxchoicelayout.addWidget(self.checkBox1)
        #edxchoicelayout.addWidget(self.checkBox2)
        #self.checkBox1.stateChanged.connect(self.update_checkboxes)
        #self.checkBox2.stateChanged.connect(self.update_checkboxes)
        self.sequence_layout.addLayout(edxchoicelayout)

        self.sequence_layout.addWidget(QLabel("Sequences"))
        self.sequence_layout.addWidget(self.sequences_checklist)
        self.sequence_layout.addWidget(QLabel("Custom Sequences"))
        self.sequence_layout.addWidget(self.customsequences_checklist)

        self.parameters_area = QWidget()

        sequence_variables_layout = QVBoxLayout()
        sequence_variables_layout.addWidget(QLabel("Sequence Variables"))
        sequence_variables_layout.addWidget(self.parameters_area)

        buttonhlayout = QHBoxLayout()
        self.sequence_namer = QLineEdit()
        self.SetButton = QPushButton("Set Sequence")
        self.SetButton.clicked.connect(self.set_sequence)
        buttonhlayout.addWidget(self.sequence_namer)
        buttonhlayout.addWidget(self.SetButton)

        sequence_variables_layout.addLayout(buttonhlayout)
        sequence_hlayout.addLayout(self.sequence_layout)
        sequence_hlayout.addLayout(sequence_variables_layout)

        self.hlayout.addLayout(sequence_hlayout)

    def replace_widget(self, layout, widget_to_replace, custom_widget_to_replace, custom=False):
        #self.custom_sequences_store[self.branch] = widget_to_replace
        index = layout.indexOf(widget_to_replace)
        custom_index = layout.indexOf(custom_widget_to_replace)
        widget_to_replace.hide()       
        custom_widget_to_replace.hide()  
        # if not custom: 
        widget_to_replace.deleteLater()
        custom_widget_to_replace.deleteLater()
        self.place_sequence_options() 
        # if custom:
        #     layout.insertWidget(self.custom_sequences_store[self.old_branch], self.customsequences_checklist)
        # else:
        
        layout.insertWidget(index, self.sequences_checklist)
        layout.insertWidget(custom_index, self.customsequences_checklist)
        

        #self.replace_custom_widget(layout)

    def create_checkboxes(self, layout):
        """Finds the names of folders in the current working directory.

        Returns:
            A list of folder names.
        """

        folder_names = []

        script_dir = Path(__file__).parent.resolve()  # Ensure absolute path
        # Define the relative path *within your project*
        rel_path = Path("sequences")
        # Combine the script directory with the relative path to get the full path
        mypath = script_dir / rel_path
        # Resolve the full path on the system
        dir_path = str(mypath.resolve())

        dir_path = self.get_sequences_path()
        self.checkboxes = []

        #print(dir_path)

        for entry in os.listdir(dir_path):  # Iterate over entries in the directory
            
            if entry != 'core' and entry != '__pycache__' and entry != 'template' and entry != '__init__.py':
                self.checkBox = QCheckBox(entry)
                self.checkBox.setObjectName(entry)
                self.checkboxes.append(self.checkBox)
                self.checkBox.clicked.connect(self.update_checkboxes)
                if entry == 'IDA':
                    self.checkBox.setChecked(True)
                layout.addWidget(self.checkBox)

    def remove_non_ida_entries(self, checklist: QListWidget):
        """Removes checklist entries not ending with '_ida' and returns the removed items.

        Args:
            checklist: The PyQt5 QListWidget object to modify.

        Returns:
            A list of the text labels of the removed items.
        """

        removed_items = []
        for i in reversed(range(checklist.count())):
            item = checklist.item(i)
            if not item.text().endswith("_ida"):
                removed_items.append(item.text())  # Store before removing
                checklist.takeItem(i)

        return removed_items

    def add_removed_entries(self, checklist: QListWidget, removed_items):
        """Adds previously removed entries back to the checklist with checkboxes.

        Args:
            checklist: The PyQt5 QListWidget object to modify.
            removed_items: A list of the text labels of the removed items.
        """
        for item_text in removed_items:
            item = QListWidgetItem(item_text)  # Create a new QListWidgetItem
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)  # Make it checkable
            item.setCheckState(Qt.Unchecked)  # Set initial state to unchecked
            checklist.addItem(item)

        self.removed_items = []

    def remove_ida_entries(self, checklist: QListWidget):
        """Removes checklist entries containing '_ida' and returns the removed items.

        Args:
            checklist: The PyQt5 QListWidget object to modify.

        Returns:
            A list of the text labels of the removed items.
        """
        removed_items = []
        for i in reversed(range(checklist.count())):
            item = checklist.item(i)
            if "_ida" in item.text():
                removed_items.append(item.text())  # Store before removing
                checklist.takeItem(i)

        return removed_items

    def update_checkboxes(self, item):
        sender = self.sender()
        name = sender.objectName()
        checkbox = self.findChild(QCheckBox, name)

        check = self.warning_popup()

        if check:
            if checkbox:
                for box in self.checkboxes:
                    if box.objectName() != checkbox.objectName():
                        if box.isChecked():
                            box.setChecked(False)

            #self.custom_sequences_store[self.branch] = self.customsequences_checklist
            self.old_branch = self.branch
            self.branch = name
            #if checkbox:
            # self.replace_widget(self.sequence_layout, self.customsequences_checklist, custom=True)
            self.yamldict['Sequences'] = {}
            #self.place_sequence_options()

            if checkbox:
                self.replace_widget(self.sequence_layout, self.sequences_checklist, self.customsequences_checklist)
        else:
            checkbox.setChecked(False)

        # checkbox.setChecked(True)

        # if sender.isChecked():
        #     if sender == self.checkBox1:
        #         self.IDAcheck = True
        #         self.checkBox2.setChecked(False)
        #         self.add_removed_entries(self.sequences_checklist, self.removed_items)
        #         self.removed_items = self.remove_non_ida_entries(
        #             self.sequences_checklist
        #         )
        #     elif sender == self.checkBox2:
        #         self.IDAcheck = False
        #         self.checkBox1.setChecked(False)
        #         self.add_removed_entries(self.sequences_checklist, self.removed_items)
        #         self.removed_items = self.remove_ida_entries(self.sequences_checklist)

    def warning_popup(self):
        popup = QMessageBox()
        popup.setWindowTitle("Warning")
        popup.setText('Warning: if you change stage all custom sequences will be erased')
        popup.addButton('Continue', QMessageBox.AcceptRole)
        popup.addButton('Cancel', QMessageBox.RejectRole)

        result = popup.exec()

        if result == QMessageBox.AcceptRole:
            return True
        else:
            return False

    def button1_clicked(self, item):
        selected_devices = []
        selected_sequence = []

        # check which devices is selected
        for i in range(self.listbox2.count()):
            if self.listbox2.item(i).checkState() == Qt.Checked:
                selected_devices.append(self.listbox2.item(i))

        # selected_devices = self.listbox2.selectedItems()

        for i in range(self.customsequences_checklist.count()):
            if self.customsequences_checklist.item(i).checkState() == Qt.Checked:
                selected_sequence.append(self.customsequences_checklist.item(i))

        # check which sequence is selected

        # selected_sequence = self.customsequences_checklist.selectedItems()


        if selected_sequence != [] and selected_devices != []:
            for device in selected_devices:
                self.yamldict["Devices"][device.text()]["sequences"].append(
                    selected_sequence[0].text().split(' ')[0]
                )
                seq = selected_sequence[0].text().split(' ')[0]
                self.runtime_journal[seq][1] = self.runtime_journal[seq][1] + 1
                print(
                    "Linked sequence: "
                    + selected_sequence[0].text()
                    + " and device: "
                    + device.text()
                )

            sequence_item = QListWidgetItem(selected_sequence[0].text().split(' ')[0])
            sequence_item.setFlags(sequence_item.flags() | Qt.ItemIsUserCheckable)
            sequence_item.setCheckState(Qt.Unchecked) 
            self.listbox4.addItem(sequence_item)
        else:
            print('Please make sure a sequence and device(s) are selected before linking.')

    def button2_clicked(self, item):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(
            None,
            "Save as YAML",
            "",
            "YAML Files (*.yaml);;All Files (*)",
            options=options,
        )
        self.runtime_max = 10000
        runtime = self.total_runtime_check(self.yamldict)
        if runtime >= self.runtime_max:
            print(f"Total runtime {runtime} exceeds set threshold of {self.runtime_max}, aborting save.")
        else:
            print(f"Total runtime {runtime} is within set threshold of {self.runtime_max}, proceeding with save.")
            if filename:
                if not filename.endswith(".yaml"):
                    filename += ".yaml"
                with open(filename, "w") as file:
                    yaml.dump(self.yamldict, file)
                print("Saved to " + filename)
            else:
                print("Please choose save location to export YAML file.")

    def object_to_dict(self, obj):
        """
        Convert an object's attributes to a dictionary.

        Args:
        - obj: The object to be converted

        Returns:
        - dict: A dictionary representation of the object's attributes
        """
        return {
            attr: getattr(obj, attr)
            for attr in dir(obj)
            if not callable(getattr(obj, attr)) and not attr.startswith("__")
        }

    def update_custom_sequences(self, checklist, data_dict):
        """
        Refresh the given checklist based on the updated dictionary.

        Args:
            checklist (QListWidget): The checklist to refresh.
            data_dict (dict): Dictionary containing data for the checklist.
        """
        checklist.clear()  # Clear existing items

        for key in data_dict:
            if 'Runtime' in data_dict[key]:
                item = QListWidgetItem(key + ' [' + str(data_dict[key]['Runtime']) + ' secs' ']')
                self.runtime_journal[key] = [data_dict[key]['Runtime'], 0]
            else:
                self.sequence_runtime_check(self.extract_text_in_brackets(key), data_dict[key], key)
                item = QListWidgetItem(key + ' [' + str(data_dict[key]['Runtime']) + ' secs' ']')
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)  # Allow user to check/uncheck the item
            item.setCheckState(Qt.Unchecked)  # Initially set the item to unchecked
            checklist.addItem(item)

    def setup_buttons(self):
        button1 = QPushButton("Link Sequence")
        button2 = QPushButton("Button 2")
        button3 = QPushButton("Button 3")

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(button1)
        buttons_layout.addWidget(button2)
        buttons_layout.addWidget(button3)

        button1.isClicked.connect(self.button1_clicked)

        self.layout.addLayout(buttons_layout)

    def setup_devices(self):
        layoutv = QVBoxLayout()

        button1 = QPushButton("Link Sequence")
        button2 = QPushButton("Export Yaml")
        #button3 = QPushButton("Adjust coord file")

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(button1)
        buttons_layout.addWidget(button2)
        #buttons_layout.addWidget(button3)

        button1.clicked.connect(self.button1_clicked)
        button2.clicked.connect(self.button2_clicked)
        #button3.clicked.connect(self.fix_coord_file)

        layoutv.addLayout(buttons_layout)

        layouth = QHBoxLayout()
        self.listbox1 = QListWidget()
        self.listbox1_2 = QListWidget()
        self.listbox1_3 = QListWidget()
        self.listbox2 = QListWidget()
        self.listbox2.setSelectionMode(QListWidget.ExtendedSelection)

        devices_group_layout = QVBoxLayout()
        self.device_search = QLineEdit()
        self.device_search.setPlaceholderText("Search for devices here...")
        self.device_search.textChanged.connect(self.search_devices)

        devices_group_layout.addWidget(self.device_search)
        devices_group_layout.addWidget(QLabel("Devices"))
        devices_group_layout.addWidget(self.listbox2)

        button_h_layout = QHBoxLayout()

        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.select_all)

        button_h_layout.addWidget(select_all_btn)

        unselect_all_btn = QPushButton("Unselect All")
        unselect_all_btn.clicked.connect(self.unselect_all)

        button_h_layout.addWidget(unselect_all_btn)

        selectkw_btn = QPushButton("Select Keyword")
        selectkw_btn.clicked.connect(self.select_keyword)

        button_h_layout.addWidget(selectkw_btn)

        select_highlighted_btn = QPushButton("Select Highlighted")
        select_highlighted_btn.clicked.connect(self.select_highlighted)

        button_h_layout.addWidget(select_highlighted_btn)

        devices_group_layout.addLayout(button_h_layout)



        choice_menu = QHBoxLayout()

        grouplayout = QVBoxLayout()
        grouplayout.addWidget(QLabel("Group"))
        grouplayout.addWidget(self.listbox1)
        self.listbox1.setFixedWidth(75)
        choice_menu.addLayout(grouplayout)

        pollayout = QVBoxLayout()
        pollayout.addWidget(QLabel("Polarization"))
        pollayout.addWidget(self.listbox1_2)
        self.listbox1_2.setFixedWidth(75)
        choice_menu.addLayout(pollayout)

        wllayout = QVBoxLayout()
        wllayout.addWidget(QLabel("Wavelength"))
        wllayout.addWidget(self.listbox1_3)
        self.listbox1_3.setFixedWidth(75)
        choice_menu.addLayout(wllayout)

        devices_group_layout.addLayout(choice_menu)

        layouth.addLayout(devices_group_layout)
        # layouth.addLayout(devices_layout)

        self.listbox3 = QListWidget()
        self.listbox4 = QListWidget()

        device_data_sequences_layout = QVBoxLayout()
        device_data_sequences_layout.addWidget(QLabel("Device Data"))
        device_data_sequences_layout.addWidget(self.listbox3)
        device_data_sequences_layout.addWidget(QLabel("Associated Sequences"))
        device_data_sequences_layout.addWidget(self.listbox4)
        self.listbox4.itemChanged.connect(self.on_itembox4_checked)

        remove_sequence_btn = QPushButton("Remove Sequence")
        remove_sequence_btn.clicked.connect(self.remove_sequence)
        device_data_sequences_layout.addWidget(remove_sequence_btn)

        layoutv.addLayout(device_data_sequences_layout)
        layouth.addLayout(layoutv)

        self.hlayout.addLayout(layouth)

    def select_items(self, sequence_name):
        for i in range(self.listbox2.count()):
            item = self.listbox2.item(i)
            try:
                if sequence_name in self.devicedict[item.text()]['sequences']:
                    item.setSelected(True)
            except:
                for x in self.deviceobjects:
                    a = item.text()
                    b = x.device_id
                    if item.text() == x.device_id:
                        deviceobject = x
                if sequence_name in deviceobject.sequences:
                    item.setSelected(True)

    def unselect_items(self):
        for i in range(self.listbox2.count()):
            item = self.listbox2.item(i)
            item.setSelected(False)

    def on_itembox4_checked(self):
        checked_items = self.find_checked_items(self.listbox4)
        if len(checked_items) == 1:

            self.select_items(checked_items[0].text())

            for i in range(self.customsequences_checklist.count()):
                if self.customsequences_checklist.item(i).text() != checked_items[0].text():
                    self.customsequences_checklist.item(i).setCheckState(Qt.Unchecked)
                else:
                    self.customsequences_checklist.item(i).setCheckState(Qt.Checked)


            
            self.custom_reset_parameters(checked_items[0].text().split(' ')[0])
            self.sequence_namer.setText(self.extract_text_before_brackets(checked_items[0].text()))
        else:
            self.unselect_items()
            self.remove_layout_from_widget(self.parameters_area)
            
    def find_checked_items(self, box):
        checked_items = []
        for i in range(box.count()):
            item = box.item(i)
            if item.checkState() == Qt.Checked:
                checked_items.append(item)
        return checked_items

    def remove_sequence(self):
        selected_sequences = self.find_checked_items(self.listbox4)
        selected_devices = self.find_checked_items(self.listbox2)
        # selected_sequences = self.listbox4.selectedItems()
        # selected_devices = self.listbox2.selectedItems()
        for item in selected_sequences:
            row = self.listbox4.row(item)  # Get the row of the item
            self.listbox4.takeItem(row)

        count = 0
        for device in selected_devices:
            for sequence in selected_sequences:
                try:
                    self.yamldict['Devices'][device.text()]['sequences'].remove(sequence.text())
                    print('Removed sequence '+sequence.text()+' from device '+device.text())
                    count = count + 1
                except: 
                    for x in self.deviceobjects:
                        if x.device_id == device.text():
                            try:
                                x.sequences.remove(sequence.text())
                                count = count + 1
                            except:
                                pass
                    print('Removed sequence '+sequence.text()+' from device '+device.text())

        for seq in selected_sequences:
            a = seq.text()
            self.runtime_journal[seq.text()][1] = self.runtime_journal[seq.text()][1] - count

    def select_keyword(self, item):
        keyword = self.device_search.text()
        for i in range(self.listbox2.count()):
            if keyword in self.listbox2.item(i).text() and keyword != '':
                self.listbox2.item(i).setCheckState(Qt.Checked)

    def select_highlighted(self, item):

        for i in range(self.listbox2.count()):
            if self.listbox2.item(i).isSelected():
                self.listbox2.item(i).setCheckState(Qt.Checked)

    def select_all(self, item):
        for i in range(self.listbox2.count()):
            self.listbox2.item(i).setCheckState(Qt.Checked)

    def unselect_all(self, item):
        for i in range(self.listbox2.count()):
            self.listbox2.item(i).setCheckState(Qt.Unchecked)

    def setup_device_data_sequences(self):
        listbox3 = QListWidget()
        listbox4 = QListWidget()

        device_data_sequences_layout = QVBoxLayout()
        device_data_sequences_layout.addWidget(QLabel("Device Data"))
        device_data_sequences_layout.addWidget(listbox3)
        device_data_sequences_layout.addWidget(QLabel("Associated Sequences"))
        device_data_sequences_layout.addWidget(listbox4)

        self.hlayout.addLayout(device_data_sequences_layout)

    def setup_save_folder(self):
        # self.save_label = QLineEdit("No Save Folder Selected")
        # self.savefile_button = QPushButton("Choose File")
        self.checkyaml_button = QPushButton("Check YAML")
        # self.savefile_button.clicked.connect(self.choose_save_file)
        self.checkyaml_button.clicked.connect(self.yaml_check_open)

        file_layout = QHBoxLayout()
        # file_layout.addWidget(self.save_label)
        # file_layout.addWidget(self.savefile_button)
        file_layout.addWidget(self.checkyaml_button)
        self.layout.addLayout(file_layout)

    def yaml_check_open(self):
        fname = QFileDialog.getOpenFileName(self, "Open file")

        yaml_check(fname[0])

    def create_checklist(self, dict, customflag=False):
        checklist = QListWidget()
        for x in dict:
            item = QListWidgetItem(x)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            checklist.addItem(item)
        # Connect the itemChanged signal to the update_text_editor slot
        if customflag == True:
            checklist.itemClicked.connect(self.custom_sequence_selected)
        else:
            checklist.itemClicked.connect(self.sequence_selected)
        return checklist

    def custom_sequence_selected(self, item):
        # Uncheck all items except the current one
        for i in range(self.sequences_checklist.count()):
            if self.sequences_checklist.item(i) != item:
                self.sequences_checklist.item(i).setCheckState(Qt.Unchecked)

        for i in range(self.customsequences_checklist.count()):
            if self.customsequences_checklist.item(i) != item:
                self.customsequences_checklist.item(i).setCheckState(Qt.Unchecked)

        self.select_items(item.text().split(' ')[0])

        if item.checkState() == Qt.Checked:
            # Get the sequence name
            self.sequence_name0 = item.text()

            self.sequence_name0 = self.sequence_name0.split(' ')[0]

            self.custom_reset_parameters(self.sequence_name0)
            # Get the path to the sequences directory
            # cwd = os.getcwd()
            # d = dirname(abspath(__file__))
            # # print(d)
            # d = str(d)

            # attributes = self.yamldict["Sequences"][self.sequence_name0]

            # # class_name = self.find_class_names_in_file(sequence_file)

            # # attributes = self.find_instance_attributes_in_init(sequence_file, class_name[0])
            # # print(attributes)

            # # Clear the existing layout
            # self.clear_layout(self.parameters_area.layout())

            # # Delete the existing layout
            # old_layout = self.parameters_area.layout()
            # if old_layout is not None:
            #     del old_layout

            # layout, self.widget_list = self.set_parameters(attributes)
            # # self.populate_sequence_variables(sequence_file, class_name[0])

            # new_layout = self.parameters_area.layout()
            # if new_layout is None:  # Only set the new layout if there isn't one already
            #     self.parameters_area.setLayout(layout)

            # # Set the new layout
            # self.parameters_area.setLayout(layout)

        else:
            # Clear the text editor
            self.unselect_items()
            self.remove_layout_from_widget(self.parameters_area)

    def custom_reset_parameters(self, sequenceName):
        # Get the sequence name
            if 'ida' in sequenceName:
                showresults = False
            else:
                showresults = True
            self.sequence_name0 = sequenceName
            # Get the path to the sequences directory
            cwd = os.getcwd()
            d = dirname(abspath(__file__))
            # print(d)
            d = str(d)

            attributes = self.yamldict["Sequences"][self.sequence_name0]

            sequence_name_og = self.extract_text_in_brackets(sequenceName)[0] + ".py"

            script_dir = Path(__file__).parent.resolve()  # Ensure absolute path
            # Define the relative path *within your project*
            rel_path = Path("sequences", self.branch, sequence_name_og)
            # Combine the script directory with the relative path to get the full path
            mypath = script_dir / rel_path
            # Resolve the full path on the system
            sequence_file = str(mypath.resolve())

            class_name = self.find_class_names_in_file(sequence_file)

            attributes2 = self.find_instance_attributes_in_init(sequence_file, class_name[0])

            for entry in attributes:
                if entry != 'Runtime':
                    for entry2 in attributes[entry]:
                        attributes2[entry][entry2] = attributes[entry][entry2]

            self.attributes = attributes2

            # class_name = self.find_class_names_in_file(sequence_file)

            # attributes = self.find_instance_attributes_in_init(sequence_file, class_name[0])
            # print(attributes)

            # Clear the existing layout
            self.clear_layout(self.parameters_area.layout())

            # Delete the existing layout
            old_layout = self.parameters_area.layout()
            if old_layout is not None:
                del old_layout

            layout, self.widget_list = self.set_parameters(attributes2, showresults=showresults)
            # self.populate_sequence_variables(sequence_file, class_name[0])

            new_layout = self.parameters_area.layout()
            if new_layout is None:  # Only set the new layout if there isn't one already
                self.parameters_area.setLayout(layout)

            # Set the new layout
            self.parameters_area.setLayout(layout)

    def reset_parameters(self, sequenceName):

        if 'ida' in sequenceName:
            showresults = False
        else:
            showresults = True
        cwd = os.getcwd()
        d = str(dirname(abspath(__file__)))

        sequence_name = sequenceName + ".py"

        script_dir = Path(__file__).parent.resolve()  # Ensure absolute path
        # Define the relative path *within your project*
        rel_path = Path("sequences", self.branch, sequence_name)
        # Combine the script directory with the relative path to get the full path
        mypath = script_dir / rel_path
        # Resolve the full path on the system
        sequence_file = str(mypath.resolve())

        #sequence_file = os.path.join(d, "sequences", self.branch, sequence_name)

        class_name = self.find_class_names_in_file(sequence_file)

        self.attributes = self.find_instance_attributes_in_init(
            sequence_file, class_name[0]
        )

        # Clear the existing layout
        self.clear_layout(self.parameters_area.layout())

        # Delete the existing layout
        old_layout = self.parameters_area.layout()
        if old_layout is not None:
            del old_layout

        layout, self.widget_list = self.set_parameters(self.attributes, showresults=showresults)
        self.results_info = self.attributes["results_info"]
        # self.populate_sequence_variables(sequence_file, class_name[0])

        new_layout = self.parameters_area.layout()
        if new_layout is None:  # Only set the new layout if there isn't one already
            self.parameters_area.setLayout(layout)

        # Set the new layout
        self.parameters_area.setLayout(layout)

    def extract_text_in_brackets(self, text):
        results = []
        start_index = None
        for i, char in enumerate(text):
            if char == '(':
                start_index = i + 1  # Record the index after the opening bracket
            elif char == ')':
                if start_index is not None:  
                    results.append(text[start_index:i])
                    start_index = None
        return results
    
    def extract_text_before_brackets(self, text):
        current_word = ""
        in_brackets = False
        for char in text:
            if not in_brackets:
                if char == '(':
                    in_brackets = True
                else:
                    current_word += char
        return current_word 

    def set_sequence(self, item):
        if self.check_for_multiple_sequence_types(self.sequence_name0):
            print('Please do not choose sequence types from different stages')
            return
        
        parameters = self.get_parameters(self.widget_list)

        if self.check_bounds(parameters):
            return

        if '(' in self.sequence_namer.text() or ')' in self.sequence_namer.text():
            print('Please remove brackets from sequence name and try again')
            return

        a = self.extract_text_in_brackets(self.sequence_name0)
        if a != []:
            self.sequence_name0 = a[0]

        name = self.sequence_namer.text() + "(" + self.sequence_name0 + ")"
        # if self.branch == 'IDA':
        #     parametersdict = {
        #         "variables": parameters["variables"],
        #         "results_info": self.results_info,
        #     }

        #     self.yamldict["Sequences"][
        #         self.sequence_namer.text() + "(" + self.sequence_name0 + ")"
        #     ] = parametersdict
        # else:
        self.yamldict["Sequences"][
                self.sequence_namer.text() + "(" + self.sequence_name0 + ")"
            ] = parameters

        runtime = self.sequence_runtime_check(self.sequence_name0, parameters, name)
        self.update_custom_sequences(self.customsequences_checklist, self.yamldict["Sequences"])
        print("Added Sequence")
        print(f'This sequence will take approximately {runtime} seconds to run')

    def check_bounds(self, parameters):
        variables = parameters['variables']
        check = False

        for variable in variables:
            if variable + '_bounds' in self.attributes['variables']:
                try:
                    a = variables[variable]
                    b = self.attributes['variables'][variable + '_bounds'][1]
                    subcheck = 0

                    if ',' in variables[variable]:
                        readings = variables[variable].split(',')
                        for i in range(len(readings)):
                            subcheck = 0
                            if isinstance(self.attributes['variables'][variable + '_bounds'][0], list):
                                for j in range(len(self.attributes['variables'][variable + '_bounds'][0])):
                                    if float(readings[i]) > float(self.attributes['variables'][variable + '_bounds'][1][j]) or float(readings[i]) < float(self.attributes['variables'][variable + '_bounds'][0][j]):
                                        subcheck += 1
                                if subcheck == len(self.attributes['variables'][variable + '_bounds'][0]):
                                    print('Variable {} entry {} is out of bounds'.format(variable, readings[i]))
                                    print('Ensure variable is within {} and {} or {} and {}'.format(self.attributes['variables'][variable + '_bounds'][0][0], self.attributes['variables'][variable + '_bounds'][1][0], self.attributes['variables'][variable + '_bounds'][0][1], self.attributes['variables'][variable + '_bounds'][1][1] ))

                                    check = True
                                    subcheck = 0
                            else:
                                if float(readings[i]) > float(self.attributes['variables'][variable + '_bounds'][1]) or float(readings[i]) < float(self.attributes['variables'][variable + '_bounds'][0]):
                                    print('Variable {} entry {} is out of bounds'.format(variable, readings[i]))
                                    print('Ensure variable is within {} and {}'.format(self.attributes['variables'][variable + '_bounds'][0], self.attributes['variables'][variable + '_bounds'][1]))
                                    check = True
                    else:
                        if isinstance(self.attributes['variables'][variable + '_bounds'][0], list):
                            for i in range(len(self.attributes['variables'][variable + '_bounds'][0])):
                                if float(variables[variable]) > float(self.attributes['variables'][variable + '_bounds'][1][i]) or float(variables[variable]) < float(self.attributes['variables'][variable + '_bounds'][0][i]):
                                    subcheck += 1
                            if subcheck == len(self.attributes['variables'][variable + '_bounds'][0]):
                                print('Variable {} is out of bounds'.format(variable))
                                print('Ensure variable is within {} and {}'.format(self.attributes['variables'][variable + '_bounds'][0], self.attributes['variables'][variable + '_bounds'][1]))

                                check = True
                                subcheck = 0
                        else:
                            if float(variables[variable]) > float(self.attributes['variables'][variable + '_bounds'][1]) or float(variables[variable]) < float(self.attributes['variables'][variable + '_bounds'][0]):
                                print('Variable {} is out of bounds'.format(variable))
                                print('Ensure variable is within {} and {}'.format(self.attributes['variables'][variable + '_bounds'][0], self.attributes['variables'][variable + '_bounds'][1]))

                                check = True
                except:
                    print('Bounds check failed for variable {}'.format(variable))
                    check = True
        return check

    def sequence_runtime_check(self, sequenceName, parameters, name):
        wavelength_constant = 0.25
        smu_constant = 0.5

        sequencetypes = [
            "wavelength_sweep",
            "current_sweep",
            "voltage_sweep",
            "set_current_wavelength_sweep",
            "set_voltage_wavelength_sweep",
            "set_wavelength_current_sweep",
            "set_wavelength_voltage_sweep",
            "wavelength_sweep_ida",
            "current_sweep_ida",
            "voltage_sweep_ida",
            "set_current_wavelength_sweep_ida",
            "set_voltage_wavelength_sweep_ida",
            "set_wavelength_current_sweep_ida",
            "set_wavelength_voltage_sweep_ida",
        ]

        sequence = sequenceName
        variables = parameters['variables']
        # print(variables)
        if sequencetypes[6] in sequence or sequencetypes[13] in sequence:

            runtime = (
                (
                    (float(variables["Stop"]) - float(variables["Start"]))
                )
                * smu_constant
                * (variables["Wavelengths"].count(",") + 1)
            )
        elif sequencetypes[5] in sequence or sequencetypes[12] in sequence:
            runtime = (
                (
                    (float(variables["Stop"]) - float(variables["Start"]))
                 / float(variables["Step"])
                )
                * smu_constant
                * (variables["Wavelengths"].count(",") + 1)
            )
        elif sequencetypes[4] in sequence or sequencetypes[11] in sequence:
            runtime = (
                (float(variables["Stop"]) - float(variables["Start"]))
                * wavelength_constant
                * (variables["Voltages"].count(",") + 1)
            )
        elif sequencetypes[3] in sequence or sequencetypes[10] in sequence:
            runtime = (
                (float(variables["Stop"]) - float(variables["Start"]))
                * wavelength_constant
                * (variables["Currents"].count(",") + 1)
            )
        elif sequencetypes[2] in sequence or sequencetypes[9] in sequence:
            runtime = (
                (float(variables["Stop"]) - float(variables["Start"]))
                / float(variables["Step"])
            ) * smu_constant
        elif sequencetypes[1] in sequence or sequencetypes[8] in sequence:
            runtime = (
                (float(variables["Stop"]) - float(variables["Start"]))
                / float(variables["Step"])
            ) * smu_constant
        elif sequencetypes[0] in sequence or sequencetypes[7] in sequence:
            runtime = (
                (float(variables["Stop"]) - float(variables["Start"]))
                * wavelength_constant
            )
        else:
            print("Error in predicting runtime. Please check sequence type and parameters.")
            return None
        self.runtime_journal[name] = [runtime, 0]
        self.yamldict["Sequences"][name]['Runtime'] = runtime
        return runtime

    def total_runtime_check(self, yamldict):
        """
        Checks the runtime of all the sequences on all specified devices.
        """

        sequences = yamldict["Sequences"]
        devices = yamldict['Devices']

        # for device in devices:
        #     for sequence in devices[device]['sequences']:
        #         self.runtime_journal[sequence][1] = self.runtime_journal[sequence][1] + 1

        move_time_constant = 1
        total_runtime = 0

        for seq in self.runtime_journal:
            total_runtime = total_runtime + self.runtime_journal[seq][0] * self.runtime_journal[seq][1]

        return total_runtime

    def to_title_case(self, s):
        return "".join(word.capitalize() for word in s.split("_"))

        self.update_custom_sequences(
            self.customsequences_checklist, self.yamldict["Sequences"]
        )
        print("Added Sequence")

    def choose_file(self):
        fname = QFileDialog.getOpenFileName(self, "Open file")
        if fname[0]:
            self.file_label.setText(fname[0])
            #self.file_label.setText("No file selected")

        if fname[0] != "" and fname[0].endswith(".yaml") == True:
            with open(fname[0], "r") as file:
                inputfile = yaml.safe_load(file)


            self.yamldict = inputfile
            self.devicedict = inputfile["Devices"]
            self.routinedict = inputfile["Sequences"]
            self.update_custom_sequences(self.customsequences_checklist, inputfile["Sequences"])


            self.deviceobjects = self.create_device_list(self.devicedict)

            self.populate_device_list()
            self.populate_group_list()
            self.populate_polar_list()
            self.populate_wavelength_list()
        elif fname[0] != "" and fname[0].endswith(".txt") == True:
            with open(fname[0], "r") as file:
                lines = file.readlines()
            if lines[0] != '% X-coord, Y-coord, Polarization, wavelength, type, deviceID, params \n' and lines[0] != '% X-coord, Y-coord, Polarization, wavelength, type, deviceID, params\n':
                print("Incorrect format for coordinate file, please reupload with correct format")
                print('First line should be "% X-coord, Y-coord, Polarization, wavelength, type, deviceID, params"')
                print('First line is ' + lines[0])
                self.file_label.setText('No file selected')
                return
            try:
                self.deviceobjects = self.create_devices_from_file(fname[0])
                self.populate_device_list()
                self.populate_group_list()
                self.populate_polar_list()
                self.populate_wavelength_list()
            except:
                print(
                    "Errors found in coordinate file, please remove or edit and upload again"
                )
        else:
            print("Please select either a valid yaml file or coordinate text file")

    def populateCustomSequences(self, inputfile):
        self.customsequences_checklist = []
        if "CustomSequences" in inputfile:
            custom_sequences = inputfile["CustomSequences"]
            for sequence in custom_sequences:
                self.customsequences_checklist.append(sequence["Name"])

    # Redefining the function create_devices_from_file with handling blank lines in electrical coordinates data
    def create_devices_from_file(self, file_path):
        """
        This function creates a list of ElectroOpticDevice objects from the input text file.
        Each line in the first part of the text file corresponds to a device.
        The second part of the text file contains the electrical coordinates for the devices.

        Args:
            file_path (str): Path to the text file.

        Returns:
            list: A list of ElectroOpticDevice objects.
        """
        # Dictionary to store the created ElectroOpticDevice objects
        devices_dict = {}
        home_dir = Path.home()

        # Create a directory in the user's home directory (e.g., 'my_package_data')
        data_dir = home_dir / "my_package_data"
        os.makedirs(data_dir, exist_ok=True)

        # Save the file within this directory
        save_location = data_dir / "coordinate_file_edits.txt"
        # save_location = os.path.dirname(os.path.abspath(__file__))
        # save_location = (
        #     str(save_location)
        #     + "\\"
        #     + "File_edits"
        #     + "\\"
        #     + "coordinate_file_edits.txt"
        # )

        optLines, ElecLines = self.countLines(file_path)

        file = self.remove_comments_from_lines(file_path, save_location)
        file = self.account_for_underscores(file, save_location)
        file = self.append_number_to_duplicate_device_ids(file, save_location)
        file = self.check_coordfile_titles(file, save_location)
        errors = self.check_number_of_columns_optical(file)
        file = self.elec_pad_underscore_issue(file, save_location)

        # if errors != []:
        #     print("Issues found in the following lines:")
        #     for x in errors:
        #         print(x)

        with open(file, "r") as f:
            data = f.readlines()

        # Remove the first line since it is the header and remove newline char
        data = [line.strip() for line in data[1:]]

        # Device data and electrical coordinates are separated by a blank line in the file
        # Find the index of the blank line
        blank_line_index = data.index("")

        # Device data is before the blank line
        device_data = data[:blank_line_index]

        # Electrical coordinates data is after the blank line and also has a header line
        elec_coords_data = data[blank_line_index + 2 :]

        # Create ElectroOpticDevice objects from device data
        for count, line in enumerate(device_data):
            try:
                x, y, polarization, wavelength, device_type, device_id = line.split(
                    ", "
                )
                optical_coords = [float(x), float(y)]
                device = ElectroOpticDevice(
                    device_id, wavelength, polarization, optical_coords, device_type
                )
                devices_dict[device_id] = device
            except:
                print("Error in optical coordinate line: " + str(count + 2) + ": " + line)

        # Add electrical coordinates to devices
        for count, line in enumerate(elec_coords_data):
            # Skip blank lines
            if line:
                # try:
                #     x, y, device_id = line.split(", ")
                #     elec_coords = ['G', float(x), float(y)]
                #     devices_dict[device_id].add_electrical_coordinates(elec_coords)
                # except:
                #     print(
                #         "Error in electrical coordinate line: "
                #         + str(count + optLines + 3)
                #         + ": "
                #         + line
                #     )

        #device ID may have an _G or _G1, _G2, _S1, _S2, modify it to accept _G or _G1 
                try:    
                    x, y, device_id = line.split(", ")


                    #print("device ID is")
                    #print(device_id)
                    # #"If its clean with no underscores, add pad to device dictonary"
                    # if("_" not in device_id):
                    #     elec_coords = ['G', float(x), float(y)]
                    #     print("we did not find an underscore in the device ID, the device ID we found is")
                    #     print(device_id)
                    #     devices_dict[device_id].add_electrical_coordinates(elec_coords)
                    
                    # #"If an older convention was used and an underscore was included"
                    # elif("_" in device_id):

                    #     # #only include pad as a device if it ends with a _G label or _G1 label
                    #     # if(device_id.endswith("G" ,"G1") ):
                    #     #     print("we know that it ends with G1")

                    #     #     #first strip away the _G or _G1
                    #     #     device_id=device_id.split("_")[0]

                    #     #     print(device_id)

                    #     #     elec_coords = ['G', float(x), float(y)]
                    #     #     devices_dict[device_id].add_electrical_coordinates(elec_coords)
                    #     #we should reject the other pads 
                    #     if( ("G2" in device_id) or ("S1" in device_id) or ("S2" in device_id) ):
                    #         pass
                    #     elif( ("G" in device_id) or ("G1" in device_id)):
                    #         print("we did find an underscore in the device ID, the device ID we found is")
                    #         print(device_id)
                    #         #first strip away the _G or _G1
                    #         device_id=device_id.split("_")[0]
                    #         elec_coords = ['G', float(x), float(y)]
                    #         print("after stripping away G labels our device id is")
                    #         print(device_id)

                    #         devices_dict[device_id].add_electrical_coordinates(elec_coords)

                    #The first thing to do is outright reject any devices that have G2S1 or S2 at the end
                    #If by some horrible coincidence the user decided to actually name their device with S2 or G2 or anything like that at the end of their name 
                    #hen they will not be able to get their device tested with this method
                    if(device_id.endswith("_G2") or device_id.endswith("_S1") or device_id.endswith("_S2")):
                        #We will simply not add pads that end with G2S1 or S2 because those will create multiple electrical coordinates for one device which is wrong
                        pass
                    elif(device_id.endswith("_G1")):
                        #These labels would correspond to the top pad if the user's labeled their device is correctly according to the old convention

                        #We need to strip away the ground label at the end though
                        device_id = device_id.replace("_G1", "")

                        #print("new device ID is")
                        #print(device_id)
                        #Now we should be fine to add the electrical coordinates To our device dictionary
                        #print("attempting to append device")
                        elec_coords = ['G', float(x), float(y)]
                        devices_dict[device_id].add_electrical_coordinates(elec_coords)
                        #print("appended successfully")

                    elif(device_id.endswith("_G")):
                        device_id = device_id.replace("_G", "")


                        #print("new device ID is")
                        #print(device_id)

                        #print("attempting to append device")
                        elec_coords = ['G', float(x), float(y)]
                        devices_dict[device_id].add_electrical_coordinates(elec_coords)
                        #print("appended successfully")


                    else: #If there is none of these ground labels then we can just try to add the coordinates and Throw exceptions if there are any other errors
                        
                        #print("attempting to append device")
                        elec_coords = ['G', float(x), float(y)]
                        devices_dict[device_id].add_electrical_coordinates(elec_coords)
                        #print("appended successfully")

                except:
                    print(
                        "Error in electrical coordinate line: "
                        + str(count + optLines + 3)
                        + ": "
                        + line
                    )


        for devicename in devices_dict:
            self.yamldict["Devices"][devices_dict[devicename].device_id] = (
                self.object_to_dict(devices_dict[devicename])
            )

        return list(devices_dict.values())
    
    def countLines(self, file_path):
        """
        This function counts the number of lines in the optical and electrical coordinate files.
        It also counts the number of optical coordinate lines and the number of electrical coordinate lines.
        """

        optLines = 0
        ElecLines = 0
        optcheck = True

        with open(file_path, "r") as file:
            lines = file.readlines()

        for line in lines:
            if line == "\n":  # Check for the line with just '\n'
                optcheck = False
            if optcheck == True:
                optLines += 1
            else:
                ElecLines += 1
    
        return optLines, ElecLines

    def create_device_list(self, devicedict):
        device_list = []
        for device_info in devicedict.values():
            device = ElectroOpticDevice(
                device_id=device_info["device_id"],
                opticalCoords=device_info["opticalCoordinates"],
                polarization=device_info["polarization"],
                device_type=device_info["device_type"],
                wavelength=device_info["wavelength"],
            )
            if device_info["electricalCoordinates"] != []:
                device.add_electrical_coordinates(device_info["electricalCoordinates"])
            device.add_sequences(device_info["sequences"])
            device_list.append(device)
            self.yamldict["Devices"][device.device_id] = self.object_to_dict(device)
        return device_list

    def fix_coord_file(self, item):
        fname = QFileDialog.getOpenFileName(self, "Open file")
        if fname[0]:
            self.file_label.setText(fname[0])
            self.yfile_label.setText("No file selected")

        if fname[0].endswith(".yaml") == True:
            print("Please select a coordinate file not a yaml file")

        if fname[0] != "" and fname[0].endswith(".yaml") == False:
            save_location = fname[0].replace(".txt", "_adjusted.txt")

            file = self.remove_comments_from_lines(fname[0], save_location)
            file = self.account_for_underscores(file, save_location)
            file = self.append_number_to_duplicate_device_ids(file, save_location)
            file = self.check_coordfile_titles(file, save_location)
            errors = self.check_number_of_columns_optical(file)
            file = self.elec_pad_underscore_issue(file, save_location)

            # if errors != []:
            #     print("Issues found in the following lines:")
            #     for x in errors:
            #         print(x)

    def elec_pad_underscore_issue(self, input_file_path, output_file_path):
        modified_lines = []
        process_line = False  # Flag to indicate if the line should be processed

        with open(input_file_path, "r") as file:
            lines = file.readlines()

        for line in lines:
            if line == "\n":  # Check for the line with just '\n'
                process_line = True

            if process_line:
                if line.strip().startswith("%"):
                    modified_lines.append(line)
                    continue
                elements = line.strip().split(", ")
                if len(elements) > 4:
                    # Keep the first, second, and last elements as they are
                    # Combine the middle elements with underscores
                    combined_middle = "_".join(elements[2:-1])
                    elements = elements[:2] + [combined_middle] + elements[-1:]
                line = ", ".join(elements) + "\n"
                modified_lines.append(line)
            else:
                # Simply append the line as is, without modification
                modified_lines.append(line)

        with open(output_file_path, "w") as file:
            file.writelines(modified_lines)

        return output_file_path

    def account_for_underscores(self, input_file_path, output_file_path):
        modified_lines = []
        process_line_optical = True  # Flag to indicate if the line should be processed

        with open(input_file_path, "r") as file:
            lines = file.readlines()

        for line in lines:
            if line == "\n":  # Check for the line with just '\n'
                process_line_optical = False

            if process_line_optical:
                if line.strip().startswith("%"):
                    modified_lines.append(line)
                    continue
                elements = line.strip().split(", ")
                if len(elements) > 6:
                    elements[5:] = ["_".join(elements[5:])]
                line = ", ".join(elements) + "\n"
                modified_lines.append(line)
            else:
                # Simply append the line as is, without modification
                if line.strip().startswith("%"):
                    modified_lines.append(line)
                    continue
                elements = line.strip().split(", ")
                if len(elements) > 3:
                    elements[2:] = ["_".join(elements[2:])]
                line = ", ".join(elements) + "\n"
                modified_lines.append(line)

        with open(output_file_path, "w") as file:
            file.writelines(modified_lines)

        return output_file_path

    def check_number_of_columns_optical(
        self, input_file_path, delimiter=", ", expected_columns=6, comment_char="%"
    ):
        alerts = (
            []
        )  # List to hold the alerts if any rows have a different number of columns
        process_line = True  # Flag to indicate if the line should be processed

        with open(input_file_path, "r") as file:
            for line_number, line in enumerate(file, start=1):
                if line == "\n":  # Check for the line with just '\n'
                    process_line = False
                # Skip empty lines and commented lines
                if process_line:
                    if not line.strip() or line.strip().startswith(comment_char):
                        continue

                    columns = line.strip().split(delimiter)
                    if len(columns) != expected_columns:
                        alerts.append((line_number, line.strip()))

        return alerts

    def check_coordfile_titles(self, input_file_path, output_file_path):
        # Define the required title lines
        title_line_1 = (
            "% X-coord, Y-coord, Polarization, wavelength, type, deviceID, params \n"
        )
        title_line_2 = "% X-coord, Y-coord, deviceID, padName, params \n"

        with open(input_file_path, "r") as file:
            lines = file.readlines()

        # Check if the first line matches the required title line 1
        if lines[0].strip() != title_line_1.strip():
            lines.insert(0, title_line_1)

        # Check if the title line 2 exists anywhere in the file
        if title_line_2 not in lines:
            lines.append(
                "\n"
            )  # Ensure there is a newline before appending the title line 2
            lines.append(title_line_2)

        # Write the modified lines to the output file
        with open(output_file_path, "w") as file:
            file.writelines(lines)

        return output_file_path

    def remove_comments_from_lines(self, input_file_path, output_file_path):
        # This function will remove the word "comment" from the end of each line
        modified_lines = []

        with open(input_file_path, "r") as file:
            lines = file.readlines()

        for line in lines:
            # Check if 'comment' is at the end of the line (considering possible trailing spaces)
            if "comment" in line:
                # Remove the word 'comment' (and surrounding whitespace)
                line = line.replace(", comment", "").rstrip() + "\n"
            modified_lines.append(line)

        try:
        # Write the modified lines to the output file
            with open(output_file_path, "w") as file:
                file.writelines(modified_lines)
        except PermissionError:
            print("Error: Permission denied. Please check write access to the directory.")
        except Exception as e:  # Catch other potential errors
            print("An error occurred while writing to the file:", e)

        return output_file_path

    def append_number_to_duplicate_device_ids(self, input_file_path, output_file_path):
        device_id_counter = {}
        modified_lines = []
        optical_lines = True
        change_record = []
        errorcheck = 0

        with open(input_file_path, "r") as file:
            lines = file.readlines()

        for line in lines:
            
            if line == "\n":  # Check for the line with just '\n'
                optical_lines = False 
            if optical_lines:
                if not line.startswith("%"):  # ignore comment lines
                    parts = line.split(", ")

                    device_id = parts[-1].strip()  #
                    # Check if the device_id has already been encountered
                    if device_id in device_id_counter:
                        # Increment the count and append it to the device_id
                        device_id_counter[device_id] += 1
                        new_device_id = f"{device_id}_{device_id_counter[device_id]}"
                        parts[-1] = new_device_id + "\n"  # replace with the new_device_id
                        change_record.append([device_id, new_device_id, [parts[0], parts[1]]])
                    else:
                        # Initialize the count for this device_id
                        device_id_counter[device_id] = 0
                    # Reconstruct the line
                    line = ", ".join(parts)
                # Add the (possibly modified) line to the list of modified lines
                modified_lines.append(line)
            else:
                if not line.startswith("%") and not line == '\n':  # ignore comment lines
                    parts = line.split(", ")
                    device_id = parts[-1].strip()
                    errorcheck = 0
                    for x in range(len(change_record)):
                        if change_record[x][0] == device_id:
                            if abs(float(parts[0]) - float(change_record[x][2][0])) <= 600 and abs(float(parts[1]) - float(change_record[x][2][1])) <= 600:
                                new_device_id = change_record[x][1]
                                parts[-1] = new_device_id + "\n"
                                error_check = errorcheck + 1
                    if errorcheck >= 2:
                        print('Possible error with electrical pad and optical device renaming, please check to make sure pads associated with and devices labelled {device_id} are correct')


                    line = ", ".join(parts)
                modified_lines.append(line)

        # Write the modified lines to the output file
        with open(output_file_path, "w") as file:
            file.writelines(modified_lines)

        return output_file_path

    def update_device_list(self, item):
        # Clear the device listbox before populating
        self.listbox2.clear()

        # Create a set to store the checked device types
        checked_device_types = set()
        checked_device_polarization = set()
        checked_device_nm = set()

        # Iterate over all items in the group listbox and add the checked ones to the set
        for i in range(self.listbox1.count()):
            if self.listbox1.item(i).checkState() == Qt.Checked:
                checked_device_types.add(self.listbox1.item(i).text())


        for i in range(self.listbox1_2.count()):
            if self.listbox1_2.item(i).checkState() == Qt.Checked:
                checked_device_polarization.add(self.listbox1_2.item(i).text())


        for i in range(self.listbox1_3.count()):
            if self.listbox1_3.item(i).checkState() == Qt.Checked:
                checked_device_nm.add(self.listbox1_3.item(i).text())

        # Iterate over all devices and add those of the checked types to the device listbox
        for device in self.deviceobjects:
            check = True
                
            if checked_device_types and device.device_type not in checked_device_types:
                check = False 

            if checked_device_polarization and device.polarization not in checked_device_polarization:
                check = False

            if checked_device_nm and device.wavelength not in checked_device_nm:
                check = False

            if check == True:
                device_item = QListWidgetItem(device.device_id)
                device_item.setFlags(device_item.flags() | Qt.ItemIsUserCheckable)
                device_item.setCheckState(Qt.Unchecked)
                self.listbox2.addItem(device_item) 

        # Connect the itemChanged signal to the update_device_data slot
        self.listbox2.itemChanged.connect(self.update_device_data)

    def populate_device_list(self):
        # Clear listbox2 before populating
        self.listbox2.clear()

        # Assuming each object in devicedict has a property deviceID
        for device in self.deviceobjects:
            item = QListWidgetItem(device.device_id)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.listbox2.addItem(item)
        self.listbox2.itemChanged.connect(self.update_device_data)

    def populate_group_list(self):
        # Clear the group listbox before populating
        self.listbox1.clear()

        # Create a set to store unique device types
        device_types = set()

        # Iterate over all devices and add their types to the set
        for device in self.deviceobjects:
            device_types.add(device.device_type)

        # Iterate over the unique device types and add them to the group listbox
        for device_type in device_types:
            item = QListWidgetItem(device_type)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.listbox1.addItem(item)

        # Connect the itemChanged signal to the update_device_list slot
        self.listbox1.itemChanged.connect(self.update_device_list)

    def populate_polar_list(self):
        # Clear the group listbox before populating
        self.listbox1_2.clear()

        # Create a set to store unique device types
        device_polarization = set()

        # Iterate over all devices and add their types to the set
        for device in self.deviceobjects:
            device_polarization.add(device.polarization)

        # Iterate over the unique device types and add them to the group listbox
        for device_pol in device_polarization:
            item = QListWidgetItem(device_pol)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.listbox1_2.addItem(item)

        # Connect the itemChanged signal to the update_device_list slot
        self.listbox1_2.itemChanged.connect(self.update_device_list)

    def populate_wavelength_list(self):
        # Clear the group listbox before populating
        self.listbox1_3.clear()

        # Create a set to store unique device types
        device_wavelengths = set()

        # Iterate over all devices and add their types to the set
        for device in self.deviceobjects:
            device_wavelengths.add(device.wavelength)

        # Iterate over the unique device types and add them to the group listbox
        for device_wav in device_wavelengths:
            item = QListWidgetItem(device_wav)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.listbox1_3.addItem(item)

        # Connect the itemChanged signal to the update_device_list slot
        self.listbox1_3.itemChanged.connect(self.update_device_list)

    def search_devices(self, search_string):
        self.rearrange_list_items(self.listbox2, search_string)

    def rearrange_list_items(self, list_widget: QListWidget, search_string: str):
        matching_items = []
        non_matching_items = []

        # Temporarily store items and detach them from the list
        for index in range(list_widget.count()):
            item = list_widget.takeItem(
                0
            )  # Take the first item (since the list is being shortened each time)
            if search_string.lower() in item.text().lower():
                matching_items.append(item)
            else:
                non_matching_items.append(item)

        # Add the items back to the list in the new order
        for item in matching_items + non_matching_items:
            list_widget.addItem(item)

    def update_device_data(self, item):
        # Clear the device data listbox and associated sequences listbox before populating
        self.listbox3.clear()
        self.listbox4.clear()

        # Uncheck all items except the current one
        # for i in range(self.listbox2.count()):
        #     if self.listbox2.item(i) != item:
        #         # Disconnect the signal to avoid recursive calls
        #         self.listbox2.itemChanged.disconnect()
        #         self.listbox2.item(i).setCheckState(Qt.Unchecked)
        #         # Reconnect the signal
        #         self.listbox2.itemChanged.connect(self.update_device_data)

        # Check if the item is checked
        if item.checkState() == Qt.Checked:
            # Get the device id
            device_id = item.text()

            # Find the corresponding device object
            for device in self.deviceobjects:
                if device.device_id == device_id:
                    # Format the device data as a string
                    device_data_str = (
                        f"Device ID: {device.device_id}\n"
                        f"Type: {device.device_type}\n"
                        f"Wavelength: {device.wavelength}\n"
                        f"Polarization: {device.polarization}\n"
                        f"Optical Coordinates: {device.opticalCoordinates}\n"
                        f"Electrical Coordinates: {device.electricalCoordinates}"
                    )

                    # Populate the device data listbox with the formatted device data
                    device_data_item = QListWidgetItem(device_data_str)
                    self.listbox3.addItem(device_data_item)

                    # Populate the associated sequences listbox with the sequences associated with the device
                    for i, sequence in enumerate(device.sequences):
                        sequence_item = QListWidgetItem(sequence)
                        self.listbox4.addItem(sequence_item)
                        self.listbox4.item(i).setCheckState(Qt.Unchecked)

    def choose_save_file(self):
        fname = QFileDialog.getOpenFileName(self, "Open file")
        if fname[0]:
            self.file_label.setText(fname[0])

        with open(fname[0], "r") as file:
            inputfile = yaml.safe_load(file)

        self.devicedict = inputfile["Devices"]
        self.routinedict = inputfile["Routines"]

    def update_text_editor(self, item):
        # Uncheck all items except the current one
        for i in range(self.sequences_checklist.count()):
            if self.sequences_checklist.item(i) != item:
                self.sequences_checklist.item(i).setCheckState(Qt.Unchecked)
        # Check if the item is checked
        if item.checkState() == Qt.Checked:
            # Get the sequence name
            sequence_name = item.text()
            # Get the path to the sequences directory
            cwd = os.getcwd()
            d = dirname(abspath(__file__))
            print(d)
            d = str(d)
            d = d + "\sequences\\" + sequence_name + "\__init__.py"
            # Read the contents of the __init__.py file
            with open(d, "r") as f:
                text = f.read()
            # Set the text in the text editor
            self.parameters_area.setText(text)
        else:
            # Clear the text editor
            self.parameters_area.clear()

    def sequence_selected(self, item):
        # Uncheck all items except the current one
        for i in range(self.sequences_checklist.count()):
            if self.sequences_checklist.item(i) != item:
                self.sequences_checklist.item(i).setCheckState(Qt.Unchecked)
        for i in range(self.customsequences_checklist.count()):
            if self.customsequences_checklist.item(i) != item:
                self.customsequences_checklist.item(i).setCheckState(Qt.Unchecked)
        # Check if the item is checked
        if item.checkState() == Qt.Checked:
            # Get the sequence name
            self.sequence_name0 = item.text()
            # Get the path to the sequences directory
            self.reset_parameters(self.sequence_name0)
            
        else:
            # Clear the text editor
            self.remove_layout_from_widget(self.parameters_area)

    def remove_layout_from_widget(self, widget):
        old_layout = widget.layout()
        if old_layout is not None:
            self.clear_layout(old_layout)

    def clear_layout(self, layout):
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

    def get_parameters(self, widgets_list):
        result_dict = {}
        current_main_key = None
        current_sub_dict = {}

        for widget in widgets_list:
            if isinstance(widget, QLabel):
                # This is a main dictionary key
                if current_main_key:
                    # Save the previous sub-dictionary and start a new one
                    result_dict[current_main_key] = current_sub_dict
                    current_sub_dict = {}
                current_main_key = widget.text()

            elif isinstance(widget, tuple) and len(widget) == 3:
                # This is a sub-dictionary key-value pair
                key_widget, value_widget, buttton_widget = widget
                key = key_widget.text()
                if isinstance(value_widget, QLineEdit):
                    value = value_widget.text()
                elif isinstance(value_widget, QComboBox):
                    value = value_widget.currentText()
                current_sub_dict[key] = value

        # Add the last sub-dictionary
        if current_main_key:
            result_dict[current_main_key] = current_sub_dict

        return result_dict

    def check_for_multiple_sequence_types(self, name):

        for i in range(self.customsequences_checklist.count()):
            if 'ida' in self.customsequences_checklist.item(i).text() and 'ida' not in name:
                return True
            else:
                return False
        return False

    def set_parameters(self, main_dict, showresults=True):
        # Initialize a list to hold the created QLabel and QLineEdit widgets
        widgets_list = []

        # Initialize a layout to organize the widgets
        layout = QFormLayout()
        variables_layout = QFormLayout()
        results_info_layout = QFormLayout()

        # Loop through the keys of the main dictionary
        for name in main_dict.keys():
            # Create a QLabel with the given name
            dict_label = QLabel(name)

            # Add the QLabel to the layout and widget list
            if showresults:# and dict_label.text() != "results_info":
                layout.addRow(dict_label)
            widgets_list.append(dict_label)

            # Loop through the keys of the sub-dictionary
            for key in main_dict[name].keys():
                # Create QLabel and QLineEdit for each key
                if "_info" not in key and "_bounds" not in key and "_options" not in key:
                    key_label = QLabel(str(key))
                    if key + "_info" in main_dict[name].keys():
                        key_info = PopupButton("?", main_dict[name][key + "_info"])
                    else:
                        key_info = None

                    if key + "_options" in main_dict[name].keys():
                        key_edit = QComboBox()
                        key_edit.addItems(main_dict[name][key + "_options"])
                        key_edit.setCurrentText(main_dict[name][key]) 
                    else:
                        key_edit = QLineEdit(str(main_dict[name][key]))

                    # Create a horizontal layout for the row
                    row_layout = QHBoxLayout()

                    if (
                        name == "results_info" and self.branch != 'IDA'
                    ) or name == "variables":
                        # Add the label and line edit to the row layout
                        row_layout.addWidget(key_label)
                        row_layout.addWidget(key_edit)

                        # Add the button to the row layout if it exists
                        if key_info is not None:
                            row_layout.addWidget(key_info)

                        # Add the row layout to the main form layout
                        layout.addRow(row_layout)

                    # Add the QLabel and QLineEdit to the layout and widget list

                    # if key_info is not None:
                    #     layout.addRow(key_label, key_edit, key_info)
                    # else:
                    #     layout.addRow(key_label, key_edit)
                    widgets_list.append((key_label, key_edit, key_info))

        return layout, widgets_list

    def populate_sequence_variables(self, sequence_file_path, class_name):
        # Load the module dynamically
        spec = importlib.util.spec_from_file_location(
            "sequence_module", sequence_file_path
        )
        sequence_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sequence_module)

        # Assuming the class name in the sequence file is 'SequenceClass'

        sequence_class = getattr(sequence_module, class_name)
        sequence_class1 = sequence_module.VoltageSweep()

        # Accessing the variables and results_Info dictionaries
        variables = (
            sequence_class.variables if hasattr(sequence_class, "variables") else {}
        )
        results_Info = (
            sequence_class.results_Info if hasattr(sequence_class, "results_Info") else {}
        )

        # Updating the QTextEdit area for sequence variables
        self.sequence_variables_textedit.clear()
        self.sequence_variables_textedit.append("Variables:")
        for key, value in variables.items():
            self.sequence_variables_textedit.append(f"{key}: {value}")
        self.sequence_variables_textedit.append("\\nResults Info:")
        for key, value in results_Info.items():
            self.sequence_variables_textedit.append(f"{key}: {value}")

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())
            # Remove layout from parent (if it has one)
            parent = layout.parent()
            if parent is not None:
                parent.layout().removeItem(layout)
            del layout

    def find_class_names_in_file(self, file_path):
        with open(file_path, "r") as f:
            tree = ast.parse(f.read())

        class_names = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_names.append(node.name)

        return class_names

    def find_instance_attributes_in_init(self, file_path, class_name):
        with open(file_path, "r") as f:
            tree = ast.parse(f.read())

        instance_attributes = {}

        def handle_expression(expr):
            if isinstance(expr, ast.Str):  # String value
                return expr.s
            elif isinstance(expr, ast.Constant):  # Use ast.Constant for numbers
                if isinstance(expr.value, int) or isinstance(expr.value, float):  # Check for numbers
                    return expr.value 
            elif isinstance(expr, ast.Name):  # Variable or other reference
                return expr.id
            elif isinstance(expr, ast.NameConstant):  # Boolean or None value
                return expr.value
            elif isinstance(expr, ast.Dict):  # Dictionary
                keys = [handle_expression(k) for k in expr.keys]
                values = [handle_expression(v) for v in expr.values]
                return {key: value for key, value in zip(keys, values)}
            elif isinstance(expr, ast.List): # List
                return [handle_expression(element) for element in expr.elts]
            elif isinstance(expr, ast.UnaryOp) and isinstance(expr.op, ast.USub):  # Negative sign
                if isinstance(expr.operand, ast.Constant):  # Check if operand is a number
                    return -expr.operand.value     # Return negative of the constant
            else:
                return "complex_expression"  # Placeholder for more complex expressions

        # def handle_expression(expr):
        #     if isinstance(expr, ast.Str):  # String value
        #         return expr.s
        #     elif isinstance(expr, ast.Num):  # Numeric value
        #         return expr.n
        #     elif isinstance(expr, ast.Name):  # Variable or other reference
        #         return expr.id
        #     elif isinstance(expr, ast.NameConstant):  # Boolean or None value
        #         return expr.value
        #     elif isinstance(expr, ast.Dict):  # Dictionary
        #         keys = [handle_expression(k) for k in expr.keys]
        #         values = [handle_expression(v) for v in expr.values]
        #         return {key: value for key, value in zip(keys, values)}
        #     else:
        #         return "complex_expression"  # Placeholder for more complex expressions

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for class_node in ast.walk(node):
                    if (
                        isinstance(class_node, ast.FunctionDef)
                        and class_node.name == "__init__"
                    ):
                        for init_node in ast.walk(class_node):
                            if isinstance(init_node, ast.Assign):
                                for target in init_node.targets:
                                    if (
                                        isinstance(target, ast.Attribute)
                                        and isinstance(target.value, ast.Name)
                                        and target.value.id == "self"
                                    ):
                                        attribute_name = target.attr
                                        attribute_value = handle_expression(
                                            init_node.value
                                        )
                                        instance_attributes[attribute_name] = (
                                            attribute_value
                                        )

        return instance_attributes


class StreamRedirector(object):
    def __init__(self, widget, file=None):
        self.widget = widget
        self.file = file

    def write(self, text):
        self.widget.append(text)  # Append text to the QTextEdit widget
        if self.file:
            self.file.write(text)  # Optionally write to a file

    def flush(self):
        pass


class PopupButton(QPushButton):
    def __init__(self, title, popup_message):
        super().__init__(title)
        self.popup_message = popup_message
        self.clicked.connect(self.showPopup)
        size = 20
        self.setFixedSize(size, size)

    def showPopup(self):
        msg = QMessageBox()
        msg.setWindowTitle("Info")
        msg.setText(self.popup_message)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()


class LogEmitter(QObject):
    """Custom signal emitter for log messages."""

    emitLog = pyqtSignal(str)


class StreamToLogger:
    """
    Custom stream object that redirects writes to a logger instance.
    """

    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, message):
        # Avoid writing newline characters
        if message != "\n":
            self.logger.log(self.level, message)

    def flush(self):
        pass


class QTextEditLogger(logging.Handler, QObject):
    """Custom logging handler sending log messages to a QTextEdit."""

    def __init__(self, parent):
        super().__init__()
        QObject.__init__(self)
        self.widget = QTextEdit(parent)
        self.widget.setReadOnly(True)
        self.logEmitter = LogEmitter()
        self.logEmitter.emitLog.connect(self.appendLogMessage)

    def emit(self, record):
        msg = self.format(record)
        self.logEmitter.emitLog.emit(msg)

    def appendLogMessage(self, message):
        self.widget.append(message)


class ElectroOpticDevice:
    """Object used to store all information associated with an electro-optic device

    Args:
        device_id (str): name of the device
        wavelength(int): wavelength for measuring the device
        polarization(str): 'TE' or 'TM'
        opticalCoords(list): list of x and y gds coordinates
        device_type: the type of the device ie. 'test'
    """

    def __init__(self, device_id, wavelength, polarization, opticalCoords, device_type):
        self.device_id = device_id
        self.wavelength = wavelength
        self.polarization = polarization
        self.opticalCoordinates = opticalCoords
        self.device_type = device_type
        self.electricalCoordinates = []
        self.sequences = []
        # self.results = Results()

    def add_electrical_coordinates(self, elecCoords):
        """Associates a bondpad with the device"""
        self.electricalCoordinates = elecCoords

    def get_optical_coordinates(self):
        """Returns the coordinates of the optical input for the device as [x coordinate, y coordinate]"""
        if self.opticalCoordinates:
            return self.opticalCoordinates

    def get_electrical_coordinates(self):
        """Return a list of electrical bondpads. Bondpads are stored as lists in the form [pad name,
        x coordinate, y coordinate]"""
        return self.electricalCoordinates

    def get_device_id(self):
        """Returns the device id of the device. IDs should be unique for each device within a chip"""
        return self.device_id

    def get_device_wavelength(self):
        """
        Fetches the device's wavelength.

        Returns:
            float: The wavelength of the device.
        """
        return self.wavelength

    def get_device_polarization(self):
        """
        Fetches the device's polarization.

        Returns:
            float: The polarization of the device.
        """
        return self.polarization

    def get_device_type(self):
        """
        Fetches the device's type.

        Returns:
            str: The type of the device.
        """
        x = self.type  # .split(',')
        return x

    def add_sequences(self, sequences):
        """Adds the names of routines to be performed on this device to a list."""
        self.sequences.extend(sequences)

    def get_reference_bond_pad(self):
        """Returns the name and coordinates of the left-most bond pad within
        an electro-optic device in the form of a list [bond pad name, x coordinates, y coordinates]
        """
        if self.electricalCoordinates:
            reference = self.electricalCoordinates[0]
            for bondPad in self.electricalCoordinates:
                if bondPad[1] < reference[1]:
                    reference = bondPad
            return reference

    def has_routines(self):
        """
        Checks if the device has any routines.

        Returns:
            bool: True if the device has routines, False if not.
        """
        if self.routines:
            return True
        else:
            return False


class DirectoryDict:
    def __init__(self, directory):
        self.directory = directory
        self.dir_dict = self.create_dict_from_dir()
        self.observer = Observer()
        self.handler = self.DirectoryHandler(self)
        self.observer.schedule(self.handler, self.directory, recursive=True)
        self.observer.start()

    def create_dict_from_dir(self):
        """
        Walks through provided directory and creates a dictionary. Each Python file is treated as a Python
        module, and each Python class in the file is included in the dictionary. The file names (without the .py extension)
        are used as dictionary keys and the value for each key is a list of class names.

        Files named '__init__.py' and directories named '__pycache__' and 'core' are explicitly excluded from the walking process.
        Directory walk is performed using os.walk().

        Each module's classes are gathered using the inspect module.

        Returns:
            dict: A dictionary where keys are file names (without .py extension) and values are lists of class
                names present in their respective files.

        Raises:
            ImportError: If the module doesn't exist or can't be imported for some reason.
            Other exceptions may be propagated depending on the content of the Python files.
        """
        dir_dict = {}
        for root, dirs, files in os.walk(self.directory):
            if "__pycache__" in dirs:
                dirs.remove("__pycache__")  # don't visit __pycache__ directories
            if "core" in dirs:
                dirs.remove("core")  # don't visit core directories
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    file_name_without_extension = os.path.splitext(file)[0]
                    module_name = file_name_without_extension
                    module_path = os.path.join(root, file)
                    spec = importlib.util.spec_from_file_location(
                        module_name, module_path
                    )
                    module = importlib.util.module_from_spec(spec)
                    classes = [
                        m[1]
                        for m in inspect.getmembers(
                            module,
                            lambda m: inspect.isclass(m)
                            and m.__module__ == module.__name__,
                        )
                    ]
                    dir_dict[file_name_without_extension] = classes
        return dir_dict

    class DirectoryHandler(FileSystemEventHandler):
        def __init__(self, dir_dict):
            self.dir_dict = dir_dict

        def on_modified(self, event):
            self.dir_dict.dir_dict = self.dir_dict.create_dict_from_dir()


if __name__ == "__main__":
    app = QApplication([])
    ex = GUI()
    ex.show()
    app.exec_()

# %%
