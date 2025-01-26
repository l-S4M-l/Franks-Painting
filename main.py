from mainui import Ui_CFSS as main_ui_form
from popupui import Ui_Form as popup_ui_form
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QBuffer, QByteArray
from QtTitleBarManager import windowmanager
from PIL import Image as PImage
import sys
import os
import json
import logging
import subprocess
import math
import io
import subprocess
import shutil

os.environ['MAGICK_HOME'] = f"{os.getcwd().replace("\\","/")}/assets/imageMagik"  # Path to your portable ImageMagick
os.environ['PATH'] = os.environ['MAGICK_HOME'] + r'\bin;' + os.environ['PATH']

from wand.image import Image as Wimage


logger = logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s-%(levelname)s:: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="log.log"
)

logger = logging.getLogger(__name__)

class DragDropLabel(QtWidgets.QLabel):
    file_dropped = QtCore.pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("Drag a file here")
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QtGui.QDropEvent):
        if event.mimeData().hasUrls():
            file_paths = [url.toLocalFile() for url in event.mimeData().urls()]
            self.file_dropped.emit(file_paths)
        else:
            self.setText("Invalid file")
            event.ignore()

class ui_class(main_ui_form, QtWidgets.QWidget):
    def setupUi(self, Form):
        super().setupUi(Form)
        self.cwd = os.getcwd().replace("\\","/")
        self.current_card_index = 0
        self.out_res = 512

        stylesheet = """background-color:rgba(0,0,0,0);"""
        self.paint_bucket.setStyleSheet(stylesheet)
        self.paint_bucket.setText("")
        self.paint_bucket_label.setStyleSheet(stylesheet)
        self.coverter.setStyleSheet(stylesheet)
        self.coverter.setText("")
        self.converter_label.setStyleSheet(stylesheet)

        self.converter_label.setPixmap(QtGui.QPixmap(f"{self.cwd}/assets/exchange-svgrepo-com.png"))
        self.paint_bucket_label.setPixmap(QtGui.QPixmap(f"{self.cwd}/assets/paint-bucket-svgrepo-com.png"))

        self.app_icon.setPixmap(QtGui.QPixmap(f"{self.cwd}/assets/icon.png"))

        windowmanager.title_bar_handler(Form,self.titlebar,self.close,self.mini_but)

        self.images_bg_textures = DragDropLabel(self.paint_editor_tab)
        self.images_bg_textures.setGeometry(QtCore.QRect(800, 10, 291, 101))
        self.images_bg_textures.setStyleSheet("background-color: rgb(39, 13, 32); border-radius:10px; border:2px solid rgb(229, 130, 202); font: 15pt \"Hawkeye\"; color:white;")
        self.images_bg_textures.setAlignment(QtCore.Qt.AlignCenter)
        self.images_bg_textures.setObjectName("images_bg_textures")

        self.events()

    def events(self):
        self.paint_bucket.clicked.connect(lambda : self.popup("uwu"))
        self.images_bg_textures.file_dropped.connect(self.file_dragged_in)
        self.ConvertImages.clicked.connect(self.convert_images)
        self.up_res.clicked.connect(self.up_res_clicked)
        self.down_res.clicked.connect(self.down_res_clicked)

    def file_dragged_in(self,paths:list):
        for value, i in enumerate(paths):
            extension = i.split("/")[-1].split(".")[-1]
            accepted_formats = [
                "bmp",       # Bitmap
                "ico",       # Icon
                "jpg", "jpeg",  # JPEG
                "png",       # PNG
                "pbm",       # Portable Bitmap
                "pgm",       # Portable Graymap
                "ppm",       # Portable Pixmap
                "tiff", "tif",  # TIFF
                "xbm",       # X Bitmap
                "xpm"        # X Pixmap
            ]


            if extension in accepted_formats: 
                self.add_texture_frame(i)
            

        self.scroll_images_area.setMinimumSize(0,self.current_card_index*131)
        
        self.repaint()

    def tab_handler(self,index):
        tab_lists = [
            self.paint_editor_tab,
        ]

    def add_texture_frame(self,texture_path):
        setattr(self, f"item_frame_{self.current_card_index}", QtWidgets.QFrame(self.scroll_images_area))
        item_frame = getattr(self, f"item_frame_{self.current_card_index}")

        offset = 131*( self.current_card_index)

        item_frame.setGeometry(QtCore.QRect(0, offset, 751, 131))
        item_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        item_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        item_frame.setObjectName(f"{self.current_card_index}_item_frame")


        setattr(self, f"main_item_bg_{ self.current_card_index}", QtWidgets.QLabel(item_frame))
        main_item_bg = getattr(self,f"main_item_bg_{ self.current_card_index}")

        main_item_bg.setGeometry(QtCore.QRect(26, 14, 691, 101))
        main_item_bg.setStyleSheet("background-color: rgb(52, 18, 43); border-radius:10px;")
        main_item_bg.setText("")
        main_item_bg.setObjectName(f"{self.current_card_index}_main_item_bg")


        setattr(self, f"main_item_bg_shadow_{ self.current_card_index}", QtWidgets.QLabel(item_frame))
        main_item_bg_shadow = getattr(self, f"main_item_bg_shadow_{ self.current_card_index}")

        main_item_bg_shadow.setGeometry(QtCore.QRect(33, 21, 691, 101))
        main_item_bg_shadow.setStyleSheet("background-color: rgba(0, 0, 0, 250); border-radius:10px;")
        main_item_bg_shadow.setText("")
        main_item_bg_shadow.setObjectName(f"{self.current_card_index}_main_item_bg_shadow")


        setattr(self, f"alias_input_{ self.current_card_index}", QtWidgets.QLineEdit(item_frame))
        alias_input:QtWidgets.QLineEdit = getattr(self, f"alias_input_{ self.current_card_index}")
        alias_input.setGeometry(QtCore.QRect(140, 75, 221, 30))
        alias_input.setStyleSheet("border-radius:6px; background-color: rgb(109, 37, 91); border-bottom:1px solid rgb(229, 130, 202); font: 10pt \"Hawkeye\"; color:rgb(200, 114, 177);")
        alias_input.setObjectName("alias_input")
        alias_input.setText("0x0000000000000000")
        
        setattr(self, f"Alias_title_{self.current_card_index}", QtWidgets.QLabel(item_frame))
        Alias_title = getattr(self, f"Alias_title_{self.current_card_index}")
        Alias_title.setGeometry(QtCore.QRect(147, 55, 111, 20))
        Alias_title.setStyleSheet("font: 10pt \"Hawkeye\"; color:rgb(117, 40, 98);")
        Alias_title.setObjectName("Alias_title")
        Alias_title.setText("Alias")

        setattr(self, f"image_text_{self.current_card_index}", QtWidgets.QLabel(item_frame))
        image_text:QtWidgets.QLabel = getattr(self, f"image_text_{ self.current_card_index}")

        image_text.setGeometry(QtCore.QRect(30, 18, 93, 93))
        image_text.setStyleSheet("")
        image_text.setText("")
        print(f"{texture_path}")
        pixmap = QtGui.QPixmap(texture_path)
        image_text.setPixmap(pixmap)
        image_text.setScaledContents(True)
        image_text.setObjectName(f"{self.current_card_index}_image_text")


        setattr(self, f"image_title_{ self.current_card_index}", QtWidgets.QLabel(item_frame))
        image_title = getattr(self, f"image_title_{ self.current_card_index}", QtWidgets.QLabel(item_frame))

        image_title.setGeometry(QtCore.QRect(140, 24, 191, 31))
        image_title.setStyleSheet("font: 15pt \"Hawkeye\"; color:white;")
        image_title.setObjectName(f"{self.current_card_index}_image_title")
        image_title.setText(texture_path.split("/")[-1].split(".")[0])


        setattr(self, f"opacity_slider{ self.current_card_index}", QtWidgets.QSlider(item_frame))
        opacity_slider:QtWidgets.QSlider = getattr(self, f"opacity_slider{ self.current_card_index}")
        opacity_slider.setGeometry(QtCore.QRect(550, 50, 160, 22))
        opacity_slider.setStyleSheet("""
                        QSlider::groove:horizontal {
                                border-radius: 9px;
                                height: 15px;
                                margin: 0px;
                                background-color: rgba(84, 193, 255, 0);
                                border: 3px solid rgb(229, 130, 202);
                                }
                        QSlider::handle:horizontal {
                                background-color:rgb(229, 130, 202);
                                height: 10px;
                                width: 23px;
                                margin: 2px;
                                border-radius:5px;
                                }""")
        opacity_slider.setProperty("value", 10)
        opacity_slider.setOrientation(QtCore.Qt.Horizontal)
        opacity_slider.setObjectName(f"{self.current_card_index}_opacity_slider")
        
        opacity_slider.valueChanged.connect(lambda:opacity_val.setText(f"{opacity_slider.value()}%"))


        setattr(self, f"opacity_title_val", QtWidgets.QLabel(item_frame))
        opacity_title = getattr(self, f"opacity_title_val")

        opacity_title.setGeometry(QtCore.QRect(552, 31, 111, 21))
        opacity_title.setStyleSheet("font: 10pt \"Hawkeye\"; color:rgb(117, 40, 98);")
        opacity_title.setObjectName(f"{self.current_card_index}_opacity_title_val")
        opacity_title.setText("opacity")


        setattr(self, f"opacity_val_{ self.current_card_index}", QtWidgets.QLabel(item_frame))
        opacity_val:QtWidgets.QLabel = getattr(self, f"opacity_val_{ self.current_card_index}")
        opacity_val.setGeometry(QtCore.QRect(550, 80, 160, 31))
        opacity_val.setStyleSheet("font: 15pt \"Hawkeye\"; color:white;")
        opacity_val.setAlignment(QtCore.Qt.AlignCenter)
        opacity_val.setObjectName(f"{self.current_card_index}_opacity_val")
        opacity_val.setText("10%")

        setattr(self, f"close_page_{self.current_card_index}", QtWidgets.QPushButton(item_frame))
        close_page:QtWidgets.QPushButton = getattr(self, f"close_page_{self.current_card_index}", QtWidgets.QPushButton(item_frame))
        close_page.setGeometry(QtCore.QRect(688, 10, 30, 31))
        close_page.setStyleSheet("font: 87 14pt \"Arial Black\"; background-color: rgba(255, 0, 4, 0); border-radius:10px; color:rgb(229, 130, 202);")
        close_page.setObjectName(f"{self.current_card_index}_close_page")
        close_page.setText("X")
        close_page.clicked.connect(self.texture_delete)

        main_item_bg_shadow.raise_()
        main_item_bg.raise_()
        image_title.raise_()
        opacity_slider.raise_()
        opacity_title.raise_()
        opacity_val.raise_()
        image_text.raise_()
        close_page.raise_()
        alias_input.raise_()
        Alias_title.raise_()

        item_frame.show()
        self.current_card_index = self.current_card_index + 1
    
    def texture_delete(self):
        pressed_button:QtWidgets.QPushButton = self.sender()
        parent:QtWidgets.QFrame = pressed_button.parentWidget()
        index = int(parent.objectName().split("_")[0])
        
        print(parent.parentWidget().objectName())
        parent.deleteLater()
        
        for i in range(index+1,self.current_card_index):
            frame:QtWidgets.QFrame = self.scroll_images_area.findChild(QtWidgets.QFrame, f"{i}_item_frame")
            try:
                y_val = frame.geometry().y()

                frame.setGeometry(QtCore.QRect(0, y_val-131, 751, 131))

                frame_value = int(frame.objectName().split("_")[0])
                frame.setObjectName(f"{frame_value-1}_item_frame")

            
            except AttributeError:
                print("ehhhhh")

        self.current_card_index = self.current_card_index - 1
        self.scroll_images_area.setMinimumSize(0,self.current_card_index*131)

        print(self.current_card_index)

    def image_to_dds(self,texture_path):
        subprocess.run(f'assets/texconv.exe -y -f DXT5 -o "{texture_path}" "M:/Skate 3 Modding and saves/xbox modding/coding/FP/code/temp.png"')

    def dds_to_psg(self,dds_path,alias):
        os.chdir(f"{self.cwd}/assets/PsgCliTool")
        subprocess.run(f'PsgCliTool.exe "{dds_path}" {alias}.psg')
        os.chdir(f"{self.cwd}")

    def convert_images(self):
        def scale_opacity(img, scale_factor):
            # Ensure scale_factor is between 0 and 1
            if scale_factor < 0:
                scale_factor = 0
            elif scale_factor > 1:
                scale_factor = 1

            # Get the data of the image
            datas = img.getdata()

            # Create a new list to store modified pixel data
            new_data = []
            for item in datas:
                # Scale the alpha value
                new_alpha = int(item[3] * scale_factor)
                new_data.append((item[0], item[1], item[2], new_alpha))

            # Update image data
            img.putdata(new_data)
            return img

        label_list = self.scroll_images_area.findChildren(QtWidgets.QLabel)
        
        image_list = []
        image_title = []
        for i in label_list:
            if "image_text" in i.objectName():
                image_list.append(i)
                print(len(i.parentWidget().findChild(QtWidgets.QLineEdit).text()))

                if len(i.parentWidget().findChild(QtWidgets.QLineEdit).text()) != 18:
                    self.popup("please make sure your alias are in the format 0x0000000000000000 and are 18 characters")
                    return

            if "image_title" in i.objectName():
                image_title.append(i.text())

        for index_val , i in enumerate(image_list):
            i:QtWidgets.QLabel = i

            alias = i.parentWidget().findChild(QtWidgets.QLineEdit).text()
            opacity = i.parentWidget().findChild(QtWidgets.QSlider).value()

            qimage = i.pixmap().toImage()
            byte_array = QByteArray()
            buffer = QBuffer(byte_array)
            buffer.open(QBuffer.WriteOnly)
            qimage.save(buffer, "PNG")
            raw_bytes = io.BytesIO(byte_array.data())
            pil_img = PImage.open(raw_bytes).convert("RGBA")

            pil_img = pil_img.resize((self.out_res, self.out_res))
            pil_img = scale_opacity(pil_img,opacity/100)

            img_byte_arr = io.BytesIO()
            pil_img.save("temp.png", format='PNG')  # Save as JPEG in memory
        

            if not os.path.exists(f"{self.cwd}/exported psgs"):
                os.makedirs(f"{self.cwd}/exported psgs")
            if not os.path.exists(f"{self.cwd}/exported psgs/{image_title[index_val]}"):
                os.makedirs(f"{self.cwd}/exported psgs/{image_title[index_val]}")

            
            self.image_to_dds(f"{self.cwd}/exported psgs/{image_title[index_val]}/")
            
            try:
                os.remove(f"{self.cwd}/exported psgs/{image_title[index_val]}/{alias}.dds")
            except FileNotFoundError:
                pass
            os.rename(f"{self.cwd}/exported psgs/{image_title[index_val]}/temp.dds",f"{self.cwd}/exported psgs/{image_title[index_val]}/{alias}.dds")

            self.dds_to_psg(f"{self.cwd}/exported psgs/{image_title[index_val]}/{alias}.dds",alias)

            with open(f"{self.cwd}/assets/PsgCliTool/{alias}.psg", "rb") as file:
                out_psg = open(f"{self.cwd}/exported psgs/{image_title[index_val]}/{alias}.psg","wb")
                out_psg.write(file.read())
                file.close()
                out_psg.close()
            
            os.remove(f"{self.cwd}/exported psgs/{image_title[index_val]}/{alias}.dds")
            os.remove(f"{self.cwd}/assets/PsgCliTool/{alias}.psg")
            os.remove(f"{self.cwd}/temp.png")

        self.popup("All Images Converted \n they can be found in the folder called exported psgs")

    def up_res_clicked(self):
        if self.out_res != 4096:
            self.out_res = self.out_res * 2
        
        self.out_put_res_display.setText(f"{self.out_res} x {self.out_res}")
    
    def down_res_clicked(self):
        if self.out_res != 128:
            self.out_res = int(self.out_res / 2)
        
        self.out_put_res_display.setText(f"{self.out_res} x {self.out_res}")
    
    def popup(self, message,error_with_log=False):
        self.popup_ui = popup_ui()
        self.popup_ui.setupUi(self.popup_ui,message,error_with_log)
        self.popup_ui.show()

class popup_ui(popup_ui_form, QtWidgets.QWidget):
    def setupUi(self, Form, Message,error_but:bool):
        super().setupUi(Form)
        self.open_log.setHidden(not error_but)
        self.cwd = os.getcwd().replace("\\","/")
        self.message.setText(Message)
        windowmanager.title_bar_handler(Form,self.titlebar,self.close_but,self.mini_but)
        self.okbutton.clicked.connect(lambda : self.close())
        self.open_log.clicked.connect(self.open_log_clicked)
    
    def open_log_clicked(self):
        try:
            subprocess.Popen(f"notepad.exe {self.cwd}/log.log")
            self.close()
        except:
            print("this shouldnt happen")
            self.close()
        



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = ui_class()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())