from PySide2 import QtCore, QtGui, QtWidgets


APP_STYLE = """
QWidget#Form {
    background: #f5f7fb;
    color: #172033;
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
}

QLabel {
    color: #23324d;
    background: transparent;
}

QLabel#label_3 {
    color: #13213c;
    font-size: 30px;
    font-weight: 800;
    letter-spacing: 0.5px;
}

QLabel#label_4 {
    color: #5d6f92;
    font-size: 14px;
    font-weight: 600;
}

QLabel#label_2,
QLabel#running_info {
    color: #5d6f92;
    padding: 4px 10px;
    border-radius: 10px;
    background: rgba(255, 255, 255, 180);
}

QLabel#title_label {
    color: #13213c;
    font-size: 18px;
    font-weight: 800;
}

QFrame#loginCard,
QFrame#menuCard,
QFrame#toolbarCard {
    background: #ffffff;
    border: 1px solid #e2e8f4;
    border-radius: 18px;
}

QLabel#captcha_pic {
    background: #f7faff;
    border: 1px solid #d8e0ef;
    border-radius: 10px;
    color: #7a89a6;
}

QLineEdit,
QComboBox {
    min-height: 34px;
    color: #172033;
    background: #ffffff;
    border: 1px solid #d8e0ef;
    border-radius: 10px;
    padding: 4px 10px;
    selection-background-color: #3268d9;
}

QLineEdit:focus,
QComboBox:focus {
    border: 1px solid #3268d9;
    background: #ffffff;
}

QComboBox::drop-down {
    width: 28px;
    border: 0;
}

QPushButton {
    min-height: 34px;
    color: #ffffff;
    background: #3268d9;
    border: 0;
    border-radius: 12px;
    padding: 7px 18px;
    font-weight: 700;
}

QPushButton:hover {
    background: #275bc5;
}

QPushButton:pressed {
    background: #1f4ba7;
}

QPushButton:disabled {
    color: #edf2fb;
    background: #aab8d3;
}

QPushButton#delete_btn {
    background: #d84e55;
}

QPushButton#delete_btn:hover {
    background: #c34249;
}

QRadioButton {
    color: #40516f;
    spacing: 8px;
}

QRadioButton::indicator {
    width: 17px;
    height: 17px;
}

QTableWidget {
    background: #ffffff;
    alternate-background-color: #f7faff;
    border: 1px solid #d8e0ef;
    border-radius: 14px;
    gridline-color: #e7edf7;
    color: #1d2a44;
    selection-background-color: #dbe7ff;
    selection-color: #10213f;
}

QTableWidget::item {
    padding: 6px;
    border: 0;
}

QTableWidget::item:selected {
    background: #dbe7ff;
    color: #10213f;
}

QHeaderView::section {
    color: #2d3c59;
    background: #edf3ff;
    border: 0;
    border-right: 1px solid #d8e0ef;
    border-bottom: 1px solid #d8e0ef;
    padding: 8px 6px;
    font-weight: 700;
}

QScrollBar:vertical,
QScrollBar:horizontal {
    background: transparent;
    width: 10px;
    height: 10px;
    margin: 2px;
}

QScrollBar::handle:vertical,
QScrollBar::handle:horizontal {
    background: #b9c6dc;
    border-radius: 5px;
}

QScrollBar::add-line,
QScrollBar::sub-line {
    width: 0;
    height: 0;
}

QMessageBox {
    background: #f5f7fb;
}
"""


def set_app_theme(app):
    app.setApplicationName("SCU URP Helper")
    app.setFont(QtGui.QFont("Microsoft YaHei", 10))
    app.setStyleSheet(APP_STYLE)


def polish_window(ui, title):
    ui.setWindowTitle(title)
    ui.setAttribute(QtCore.Qt.WA_StyledBackground, True)


def polish_table(table):
    table.setAlternatingRowColors(True)
    table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
    table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
    table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
    table.setShowGrid(False)
    table.setWordWrap(False)
    table.verticalHeader().setVisible(False)
    table.verticalHeader().setDefaultSectionSize(38)
    table.horizontalHeader().setStretchLastSection(True)
    table.horizontalHeader().setHighlightSections(False)


def add_card_shadow(widget):
    shadow = QtWidgets.QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(24)
    shadow.setColor(QtGui.QColor(39, 65, 116, 35))
    shadow.setOffset(0, 8)
    widget.setGraphicsEffect(shadow)
