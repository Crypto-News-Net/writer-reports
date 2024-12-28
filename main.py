import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from functools import partial
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTableWidget, 
                             QTableWidgetItem, QDialog, QFormLayout, QLineEdit,
                             QSpinBox, QHeaderView, QFrame, QDateEdit)
from PySide6.QtCore import Qt, QDate, QRect, QDateTime
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont, QPen, QIcon, QLinearGradient, QBrush

class WriterStats:
    def __init__(self):
        self.data_file = Path("writer_stats.json")
        self.writers = self.load_data()

    def load_data(self):
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                # Fix any duplicate IDs
                used_ids = set()
                next_id = 1
                fixed_writers = []
                fixed_stats = {}
                
                for writer in data["writers"]:
                    old_id = writer["id"]
                    # If ID is already used, assign a new one
                    while str(next_id) in used_ids:
                        next_id += 1
                    new_id = str(next_id)
                    used_ids.add(new_id)
                    
                    # Update writer with new ID
                    writer["id"] = new_id
                    fixed_writers.append(writer)
                    
                    # Transfer stats to new ID if they exist
                    if old_id in data["stats"]:
                        fixed_stats[new_id] = data["stats"][old_id]
                    else:
                        fixed_stats[new_id] = {"articles": 0, "views": 0}
                    
                    next_id += 1
                
                data["writers"] = fixed_writers
                data["stats"] = fixed_stats
                
                # Save the fixed data
                with open(self.data_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                return data
        return {
            "writers": [],
            "stats": {}
        }

    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.writers, f, indent=2)

    def add_writer(self, name):
        # Get all existing IDs
        existing_ids = {w["id"] for w in self.writers["writers"]}
        next_id = 1
        
        # Find the next available ID
        while str(next_id) in existing_ids:
            next_id += 1
        
        new_id = str(next_id)
        
        # Add writer with unique ID
        self.writers["writers"].append({
            "id": new_id,
            "name": name
        })
        
        # Initialize stats
        if "stats" not in self.writers:
            self.writers["stats"] = {}
        self.writers["stats"][new_id] = {
            "articles": 0,
            "views": 0
        }
        
        self.save_data()
        return new_id

    def update_stats(self, writer_id, articles, views):
        if "stats" not in self.writers:
            self.writers["stats"] = {}
        
        self.writers["stats"][writer_id] = {
            "articles": articles,
            "views": views
        }
        self.save_data()

    def remove_writer(self, writer_id):
        # Remove writer from writers list
        self.writers["writers"] = [w for w in self.writers["writers"] if w["id"] != writer_id]
        # Remove writer's stats
        if writer_id in self.writers["stats"]:
            del self.writers["stats"][writer_id]
        self.save_data()

    def get_writer_stats(self):
        stats = []
        for writer in self.writers["writers"]:
            writer_id = writer["id"]
            writer_stats = self.writers["stats"].get(writer_id, {"articles": 0, "views": 0})
            stats.append({
                "id": writer_id,  # Include the writer ID
                "name": writer["name"],
                "articles": writer_stats["articles"],
                "views": writer_stats["views"],
                "avg_views": round(writer_stats["views"] / writer_stats["articles"]) if writer_stats["articles"] > 0 else 0
            })
        return sorted(stats, key=lambda x: (x["articles"], x["views"]), reverse=True)

class ConfirmDialog(QDialog):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm Action")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        # Buttons
        buttons = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        confirm_btn = QPushButton("Delete")
        confirm_btn.clicked.connect(self.accept)
        confirm_btn.setDefault(True)
        confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        
        buttons.addWidget(cancel_btn)
        buttons.addWidget(confirm_btn)
        layout.addLayout(buttons)

class AddWriterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Writer")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        
        self.name_input = QLineEdit()
        layout.addRow("Name:", self.name_input)
        
        buttons = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.accept)
        add_btn.setDefault(True)
        
        buttons.addWidget(cancel_btn)
        buttons.addWidget(add_btn)
        layout.addRow(buttons)

class UpdateStatsDialog(QDialog):
    def __init__(self, writer_name, current_stats=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Update Stats for {writer_name}")
        self.setModal(True)
        self.current_stats = current_stats or {"articles": 0, "views": 0}
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        
        self.articles_input = QSpinBox()
        self.articles_input.setRange(0, 999999)
        self.articles_input.setValue(self.current_stats["articles"])
        layout.addRow("Articles:", self.articles_input)
        
        self.views_input = QSpinBox()
        self.views_input.setRange(0, 999999999)
        self.views_input.setValue(self.current_stats["views"])
        layout.addRow("Views:", self.views_input)
        
        buttons = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        update_btn = QPushButton("Update")
        update_btn.clicked.connect(self.accept)
        update_btn.setDefault(True)
        
        buttons.addWidget(cancel_btn)
        buttons.addWidget(update_btn)
        layout.addRow(buttons)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stats = WriterStats()
        self.setup_ui()
        self.update_table()

    def setup_ui(self):
        self.setWindowTitle("Writer Reports")
        self.setMinimumSize(800, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton.delete-btn {
                background-color: #dc3545;
            }
            QPushButton.delete-btn:hover {
                background-color: #c82333;
            }
            QTableWidget {
                background-color: white;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #dee2e6;
            }
            QDateEdit {
                padding: 4px 8px;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background: white;
                min-width: 120px;
            }
            QDateEdit::drop-down {
                border: none;
                width: 20px;
                padding-right: 4px;
            }
            QDateEdit::down-arrow {
                image: url(none);
                border-style: solid;
                border-width: 4px;
                border-color: #666 transparent transparent transparent;
            }
            QCalendarWidget {
                background-color: white;
                min-width: 300px;
            }
            QCalendarWidget QToolButton {
                color: #333333;
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                margin: 2px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #e9ecef;
            }
            QCalendarWidget QMenu {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
            QCalendarWidget QSpinBox {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 2px 4px;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: #333333;
                background-color: white;
                selection-background-color: #4a90e2;
                selection-color: white;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: #999999;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
                padding: 4px;
            }
        """)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QHBoxLayout()
        title = QLabel("Writer Reports")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header.addWidget(title)
        
        # Date range
        date_range = QHBoxLayout()
        date_range.addWidget(QLabel("Date Range:"))
        
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        date_range.addWidget(self.start_date)
        
        date_range.addWidget(QLabel("to"))
        
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        date_range.addWidget(self.end_date)
        
        header.addLayout(date_range)
        header.addStretch()

        # Buttons
        add_writer_btn = QPushButton("Add Writer")
        add_writer_btn.clicked.connect(self.add_writer)
        export_btn = QPushButton("Export Report")
        export_btn.clicked.connect(self.export_report)
        
        header.addWidget(add_writer_btn)
        header.addWidget(export_btn)
        layout.addLayout(header)

        # Stats summary
        stats_layout = QHBoxLayout()
        
        # Writers count
        writers_frame = QFrame()
        writers_frame.setFrameStyle(QFrame.StyledPanel)
        writers_layout = QVBoxLayout(writers_frame)
        self.writers_count = QLabel("0")
        self.writers_count.setStyleSheet("font-size: 24px; font-weight: bold;")
        writers_layout.addWidget(self.writers_count, alignment=Qt.AlignCenter)
        writers_layout.addWidget(QLabel("Total Writers"), alignment=Qt.AlignCenter)
        stats_layout.addWidget(writers_frame)
        
        # Articles count
        articles_frame = QFrame()
        articles_frame.setFrameStyle(QFrame.StyledPanel)
        articles_layout = QVBoxLayout(articles_frame)
        self.articles_count = QLabel("0")
        self.articles_count.setStyleSheet("font-size: 24px; font-weight: bold;")
        articles_layout.addWidget(self.articles_count, alignment=Qt.AlignCenter)
        articles_layout.addWidget(QLabel("Total Articles"), alignment=Qt.AlignCenter)
        stats_layout.addWidget(articles_frame)
        
        # Views count
        views_frame = QFrame()
        views_frame.setFrameStyle(QFrame.StyledPanel)
        views_layout = QVBoxLayout(views_frame)
        self.views_count = QLabel("0")
        self.views_count.setStyleSheet("font-size: 24px; font-weight: bold;")
        views_layout.addWidget(self.views_count, alignment=Qt.AlignCenter)
        views_layout.addWidget(QLabel("Total Views"), alignment=Qt.AlignCenter)
        stats_layout.addWidget(views_frame)
        
        layout.addLayout(stats_layout)

        # Writer Leaderboard
        leaderboard_frame = QFrame()
        leaderboard_frame.setFrameStyle(QFrame.StyledPanel)
        leaderboard_layout = QVBoxLayout(leaderboard_frame)
        
        leaderboard_header = QHBoxLayout()
        leaderboard_title = QLabel("Writer Leaderboard")
        leaderboard_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        leaderboard_header.addWidget(leaderboard_title)
        leaderboard_layout.addLayout(leaderboard_header)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Writer", "Articles", "Views", "Actions", ""])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        leaderboard_layout.addWidget(self.table)
        
        layout.addWidget(leaderboard_frame)

    def add_writer(self):
        dialog = AddWriterDialog(self)
        if dialog.exec():
            name = dialog.name_input.text().strip()
            if name:
                self.stats.add_writer(name)
                self.update_table()

    def update_writer_stats(self, writer_id, writer_name):
        current_stats = self.stats.writers["stats"].get(writer_id, {"articles": 0, "views": 0})
        dialog = UpdateStatsDialog(writer_name, current_stats, self)
        if dialog.exec():
            articles = dialog.articles_input.value()
            views = dialog.views_input.value()
            self.stats.update_stats(writer_id, articles, views)
            self.update_table()

    def remove_writer(self, writer_id, writer_name):
        dialog = ConfirmDialog(f"Are you sure you want to delete writer '{writer_name}'?", self)
        if dialog.exec():
            self.stats.remove_writer(writer_id)
            self.update_table()

    def update_table(self):
        writer_stats = self.stats.get_writer_stats()
        self.table.setRowCount(len(writer_stats))
        
        total_articles = 0
        total_views = 0
        
        medals = ["🥇", "🥈", "🥉"]
        
        for row, stats in enumerate(writer_stats):
            # Medal or rank
            name_item = QTableWidgetItem()
            if row < 3:
                name_item.setText(f"{medals[row]} {stats['name']}")
            else:
                name_item.setText(f"{row + 1}. {stats['name']}")
            self.table.setItem(row, 0, name_item)
            
            # Stats
            self.table.setItem(row, 1, QTableWidgetItem(str(stats["articles"])))
            views_item = QTableWidgetItem()
            views_item.setText(f"{stats['views']} ({stats['avg_views']}/article)")
            self.table.setItem(row, 2, views_item)
            
            # Action buttons
            buttons_widget = QWidget()
            buttons_layout = QHBoxLayout(buttons_widget)
            buttons_layout.setContentsMargins(0, 0, 0, 0)
            buttons_layout.setSpacing(8)
            
            # Create buttons
            update_btn = self.create_update_button(stats["id"], stats["name"])
            delete_btn = self.create_delete_button(stats["id"], stats["name"])
            
            buttons_layout.addWidget(update_btn)
            buttons_layout.addWidget(delete_btn)
            
            self.table.setCellWidget(row, 3, buttons_widget)
            
            total_articles += stats["articles"]
            total_views += stats["views"]
        
        self.writers_count.setText(str(len(writer_stats)))
        self.articles_count.setText(str(total_articles))
        self.views_count.setText(str(total_views))

    def create_button(self, text, callback, writer_id, writer_name, is_delete=False):
        btn = QPushButton(text)
        if is_delete:
            btn.setProperty("class", "delete-btn")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
        # Use partial to bind the parameters directly to the callback
        bound_callback = partial(callback, writer_id, writer_name)
        btn.clicked.connect(bound_callback)
        return btn

    def create_update_button(self, writer_id, writer_name):
        return self.create_button("Update Stats", self.update_writer_stats, writer_id, writer_name)
    
    def create_delete_button(self, writer_id, writer_name):
        return self.create_button("Delete", self.remove_writer, writer_id, writer_name, is_delete=True)

    def export_report(self):
        writer_stats = self.stats.get_writer_stats()
        # Calculate required height based on content
        # Calculate height with more generous spacing
        header_height = 120
        stats_cards_height = 140
        table_header_height = 80
        row_height = 60
        padding = 80  # Additional padding for bottom margin
        
        height = (
            header_height +                    # Header section
            stats_cards_height +               # Stats cards
            table_header_height +              # Table header
            (len(writer_stats) * row_height) + # Table rows
            padding                            # Bottom padding
        )
        
        # Create a QPixmap to render the report
        pixmap = QPixmap(1000, height)
        pixmap.fill(Qt.white)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw background
        painter.fillRect(0, 0, 1000, height, QColor("#ffffff"))
        
        # Draw header background
        header_height = 120
        header_gradient = QLinearGradient(0, 0, 1000, header_height)
        header_gradient.setColorAt(0, QColor("#4a90e2"))
        header_gradient.setColorAt(1, QColor("#357abd"))
        painter.fillRect(0, 0, 1000, header_height, QBrush(header_gradient))
        
        # Draw title and date
        font = QFont()
        font.setPointSize(28)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor("#ffffff"))
        painter.drawText(40, 50, "Writer Reports")
        
        font.setPointSize(14)
        font.setBold(False)
        painter.setFont(font)
        date_range_text = f"{self.start_date.date().toString('MMMM d, yyyy')} - {self.end_date.date().toString('MMMM d, yyyy')}"
        painter.drawText(40, 80, date_range_text)
        
        # Draw summary statistics cards
        card_width = 220
        card_height = 100
        card_spacing = 20
        cards_y = header_height - 30
        
        total_articles = sum(w["articles"] for w in writer_stats)
        total_views = sum(w["views"] for w in writer_stats)
        avg_views = round(total_views / total_articles) if total_articles > 0 else 0
        
        stats = [
            ("Total Writers", str(len(writer_stats))),
            ("Total Articles", str(total_articles)),
            ("Total Views", f"{total_views:,}"),
            ("Avg Views/Article", str(avg_views))
        ]
        
        for i, (label, value) in enumerate(stats):
            x = 40 + i * (card_width + card_spacing)
            
            # Draw card background
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor("#ffffff"))
            painter.drawRoundedRect(x, cards_y, card_width, card_height, 8, 8)
            
            # Draw card content
            painter.setPen(QColor("#333333"))
            font.setPointSize(24)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(x + 20, cards_y + 45, value)
            
            font.setPointSize(12)
            font.setBold(False)
            painter.setFont(font)
            painter.drawText(x + 20, cards_y + 70, label)
        
        # Draw leaderboard section with adjusted spacing
        y = cards_y + card_height + 80
        font.setPointSize(20)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(40, y, "Writer Leaderboard")
        
        # Draw table background
        table_y = y + 20
        table_height = height - table_y - padding
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#f8f9fa"))
        painter.drawRoundedRect(40, table_y, 920, table_height, 8, 8)
        
        # Draw column headers
        y = table_y + 40
        font.setPointSize(14)
        painter.setPen(QColor("#666666"))
        columns = [
            (60, "Writer"),
            (400, "Articles"),
            (550, "Views"),
            (700, "Avg Views/Article")
        ]
        
        for x, label in columns:
            painter.drawText(x, y, label)
        
        # Draw horizontal separator
        painter.setPen(QPen(QColor("#dee2e6"), 1))
        painter.drawLine(60, y + 10, 900, y + 10)
        
        # Draw writer stats
        y += 50
        medals = ["🥇", "🥈", "🥉"]
        
        font.setPointSize(14)
        font.setBold(False)
        painter.setFont(font)
        
        for i, writer in enumerate(writer_stats):
            if i < 3:
                prefix = f"{medals[i]} "
                painter.setPen(QColor("#333333"))
            else:
                prefix = f"{i+1}. "
                painter.setPen(QColor("#666666"))
            
            # Draw alternating row background
            if i % 2 == 0:
                painter.fillRect(60, y - 25, 840, 40, QColor("#ffffff"))
            
            text = f"{prefix}{writer['name']}"
            painter.drawText(60, y, text)
            
            # Draw detailed stats
            painter.drawText(400, y, str(writer['articles']))
            painter.drawText(550, y, f"{writer['views']:,}")
            painter.drawText(700, y, str(writer['avg_views']))
            
            y += row_height
        
        painter.end()
        
        # Save the image with date range in filename
        start_date = self.start_date.date().toString('yyyyMMdd')
        end_date = self.end_date.date().toString('yyyyMMdd')
        filename = f"writer_report_{start_date}_to_{end_date}.png"
        pixmap.save(filename)
        
        # Open the saved image with default viewer
        import os
        os.system(f'start "" "{filename}"')

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
