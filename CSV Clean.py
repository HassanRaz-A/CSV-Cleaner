import os
import pandas as pd
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QTextEdit, QListWidget, QCheckBox, QInputDialog
from PyQt5.QtGui import QFont

class CSVCleanerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('CSV Cleaner')
        self.setGeometry(700, 400, 500, 600)

        self.folder_path_label = QLabel('Source Root Folder:', self)
        self.folder_path_label.setGeometry(10, 10, 2000, 30)
        self.folder_path_label.setFont(QFont('Helvetica Bold', 12))
        self.folder_path_edit = QLineEdit(self)
        self.folder_path_edit.setFixedHeight(30)
        self.source_button = QPushButton('Browse', self)
        self.source_button.setFixedHeight(30)
        self.source_button.setFont(QFont('Helvetica Bold', 12))
        self.source_button.clicked.connect(self.browse_folder)

        self.column_label = QLabel('Columns:', self)
        self.column_label.setFont(QFont('Helvetica Bold', 12))
        self.column_list = QListWidget(self)
        self.column_list.setFixedHeight(50)
        self.column_list.setSelectionMode(QListWidget.MultiSelection)
        self.column_list.addItems(['Longitude (degree)','Latitude (degree)' ])

        self.add_button = QPushButton('Add', self)
        self.add_button.clicked.connect(self.add_column)
        self.remove_button = QPushButton('Remove', self)
        self.remove_button.clicked.connect(self.remove_column)

        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.remove_button)
        self.button_layout.addSpacing(20)  # Adjust spacing as needed

        self.options_label = QLabel('Options:', self)
        self.options_label.setFont(QFont('Helvetica Bold', 12))
        self.clean_checkbox = QCheckBox('Remove rows with missing values', self)
        self.clean_checkbox.setFont(QFont('Helvetica', 10))
        self.clean_checkbox.setChecked(True)

        self.missing_value_label = QLabel('Missing Value:', self)
        self.missing_value_label.setFont(QFont('Helvetica Bold', 12))
        self.missing_value_edit = QLineEdit(self)
        self.missing_value_edit.setFixedHeight(30)

        self.folder_layout = QHBoxLayout()
        self.folder_layout.addWidget(self.folder_path_label)
        self.folder_layout.addWidget(self.folder_path_edit)
        self.folder_layout.addWidget(self.source_button)

        self.column_layout = QHBoxLayout()
        self.column_layout.addWidget(self.column_label)
        self.column_layout.addWidget(self.column_list)

        self.options_layout = QVBoxLayout()
        self.options_layout.addWidget(self.options_label)
        self.options_layout.addWidget(self.clean_checkbox)
        self.options_layout.addWidget(self.missing_value_label)
        self.options_layout.addWidget(self.missing_value_edit)

        self.process_button = QPushButton('Clean CSV Files')
        self.process_button.setFont(QFont('Helvetica Bold', 12))
        self.process_button.clicked.connect(self.clean_csv_files)
        self.process_button.setFixedHeight(50)

        self.log_label = QLabel('Log:', self)
        self.log_label.setGeometry(10, 230, 250, 30)
        self.log_label.setFont(QFont('Helvetica Bold', 12))
        self.log_text = QTextEdit(self)
        self.log_text.setGeometry(420, 275, 500, 420)

        main_layout = QVBoxLayout()
        main_layout.addLayout(self.folder_layout)
        main_layout.addLayout(self.column_layout)
        main_layout.addLayout(self.button_layout)
        main_layout.addLayout(self.options_layout)
        main_layout.addWidget(self.process_button)
        main_layout.addWidget(self.log_label)
        main_layout.addWidget(self.log_text)

        self.setLayout(main_layout)

    def browse_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Source Root Folder')
        if folder_path:
            self.folder_path_edit.setText(folder_path)

    def add_column(self):
        column, ok = QInputDialog.getText(self, 'Add Column', 'Enter Column Name:')
        if ok:
            self.column_list.addItem(column)

    def remove_column(self):
        for item in self.column_list.selectedItems():
            self.column_list.takeItem(self.column_list.row(item))

    def clean_csv_files(self):
        folder_path = self.folder_path_edit.text()
        if not folder_path:
            QMessageBox.warning(self, 'Warning', 'Please select a folder.')
            return

        columns_to_clean = [self.column_list.item(i).text() for i in range(self.column_list.count())]
        remove_missing_values = self.clean_checkbox.isChecked()
        missing_value = self.missing_value_edit.text()

        try:
            count = 0
            for root, dirs, files in os.walk(folder_path):
                for filename in files:
                    if filename.endswith('.csv'):
                        file_path = os.path.join(root, filename)
                        try:
                            df = pd.read_csv(file_path)
                            if remove_missing_values:
                                df_cleaned = df.dropna(subset=columns_to_clean)
                            else:
                                if missing_value:
                                    for col in columns_to_clean:
                                        df[col] = df[col].replace(missing_value, pd.NA)
                                df_cleaned = df
                            df_cleaned.to_csv(file_path, index=False)
                            count += 1
                        except Exception as e:
                            print(f"Failed to process file: {file_path} due to {e}")
            self.log_text.append(f'{count} CSV files cleaned successfully.')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {str(e)}')

if __name__ == '__main__':
    app = QApplication([])
    window = CSVCleanerGUI()
    window.show()
    app.exec_()
