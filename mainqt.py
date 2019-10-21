from item import items
from combination import combinations
from setting import settings
import random
import spacy
import en_core_web_lg
import gpt_2_simple as gpt2

# pyqt5
from PyQt5 import QtCore, QtGui, QtWidgets
import sys

# initialization
inventory = []
known_places = []
known_people = []
nlp = spacy.load("en_core_web_lg")
name = ""
paragraphs = 0
setting = ""
introduction = ""
items_in_paragraph = []
places_in_paragraph = []
people_in_paragraph = []
events_in_paragraph = []
text = ""

# initialize gpt-2
from google.colab import files
!wget -O checkpoint_run1.tar https://northwestern.box.com/shared/static/8k34b5sfq1ib5e4kmwjehxtpjotfdszl.tar
!tar -xvf checkpoint_run1.tar
session = gpt2.start_tf_sess()
gpt2.load_gpt2(session)

# QT window
class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(794, 600)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(Dialog)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.comboBox = QtWidgets.QComboBox(self.frame)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.gridLayout.addWidget(self.comboBox, 0, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.frame)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 2, 1, 1)
        self.lineEdit = QtWidgets.QLineEdit(self.frame)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 0, 3, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(self.frame)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 0, 4, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.spinBox = QtWidgets.QSpinBox(self.frame)
        self.spinBox.setMinimum(1)
        self.spinBox.setMaximum(2000)
        self.spinBox.setObjectName("spinBox")
        self.gridLayout.addWidget(self.spinBox, 1, 1, 1, 1)
        self.pushButton = QtWidgets.QPushButton(self.frame)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 1, 4, 1, 1)
        self.verticalLayout.addWidget(self.frame)
        self.textEdit = QtWidgets.QTextEdit(Dialog)
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout.addWidget(self.textEdit)
        self.frame_2 = QtWidgets.QFrame(Dialog)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.frame_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.groupBox = QtWidgets.QGroupBox(self.frame_2)
        self.groupBox.setMinimumSize(QtCore.QSize(500, 100))
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(self.frame_2)
        self.groupBox_2.setMinimumSize(QtCore.QSize(250, 100))
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_2.addWidget(self.groupBox_2, 0, 1, 1, 1)
        self.verticalLayout.addWidget(self.frame_2)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Interactive Storytelling"))
        self.label.setText(_translate("Dialog", "Setting:"))
        self.comboBox.setItemText(0, _translate("Dialog", "Fantasy"))
        self.comboBox.setItemText(1, _translate("Dialog", "Sci-Fi"))
        self.label_3.setText(_translate("Dialog", "Player name:"))
        self.pushButton_2.setText(_translate("Dialog", "Start game"))
        self.label_2.setText(_translate("Dialog", "Paragraphs:"))
        self.pushButton.setText(_translate("Dialog", "Quit"))
        self.textEdit.setHtml(_translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.groupBox.setTitle(_translate("Dialog", "Actions"))
        self.groupBox_2.setTitle(_translate("Dialog", "Inventory"))

if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	Dialog = QtWidgets.QDialog()
	ui = Ui_Dialog()
	ui.setupUi(Dialog)
	Dialog.show()
	sys.exit(app.exec_())



	print("Welcome to PCG adventures!")

	# 1. Enter name and story length [# of paragraphs]
	name = input("Please enter your name: ")
	paragraphs = int(input("Welcome %s. How long should your journey be (# of paragraphs)? " % name))

	# 2. Select setting [middle age, fantasy, horror]
	# -> Load individual checkpoints and items
	while True:
		setting = input("So %d paragraphs. And what setting do you prefer? [fantasy, sci-fy] " % paragraphs)
		if setting in settings.keys():
			break
		else:
			print("Please enter a setting name.")
	print("So our story takes place in a %s world." % setting)

	# 3. Load/generate introduction [Place, Time, Crew, Items]
	# -> place items in first place.
	paragraph = random.choice(settings[setting].introductions)

	paragraph_count = 0

	while paragraph_count < paragraphs:

		# Replace [name]
		paragraph = paragraph.replace("[name]", name)
		print(paragraph)

		# append paragraph
		text = text + paragraph

		# 4. NLP on paragraph [Extract People, Places, Items]
		doc = nlp(paragraph)

		# 4.1 clear entities before extraction
		people_in_paragraph.clear()
		places_in_paragraph.clear()
		events_in_paragraph.clear()
		items_in_paragraph.clear()

		# 4.2 extract each entity
		for ent in doc.ents:
			print(ent.text, ent.start_char, ent.end_char, ent.label_)
			if ent.label_ == "PERSON" and ent.text != name:
				people_in_paragraph.append(ent.text)
			elif ent.label_ == "GPE" or ent.label_ == "LOC":
				places_in_paragraph.append(ent.text)
			elif ent.label_ == "EVENT": # talk about event
				events_in_paragraph.append(ent.text)
			elif ent.label_ == "PRODUCT":
				items_in_paragraph.append(ent.text)
		
		# 5. Check if none or only the main character is named as ent
		if (people_in_paragraph.count() > 0 or places_in_paragraph.count() > 0 or events_in_paragraph.count() > 0 or items_in_paragraph.count() > 0):

			# 6. Generate actions [Talk to, Take [item] {based on nlp}, go to [Place], Inspect [Item, Place, Person, Item in inventory], Push, Pull {fun?},
			# insult/compliment [Person], use [item], combine [item, item]]
			for person in people_in_paragraph:
				print("[talk to %s]"%person)
				print("[look to %s]"%person)
				print("[insult to %s]"%person)
				print("[compliment to %s]"%person)
				print("[%s who are you?]"%person)
			for place in places_in_paragraph:
				print("[go to %s]"%place)
				print("[inspect %s]"%place)
			for event in events_in_paragraph:
				print("[Think about %s]"%event)
			for item in items_in_paragraph:
				print("[take %s]"%item)
				print("[use %s]"%item)
				print("[push %s]"%item)

		else:
			# 6.2 Just generate another paragraph
			print("[continue]")

		#text = gpt2.generate(session, temperature=0.1,prefix=text,run_name='run1',length=100,return_as_list=True,nsamples=3,batch_size=3,top_p=0.99)
				
		# 7. Write twine paragraph including actions

		# 8. Wait for player input

		# 9. React to input and update meta data [add [place] to [known places], add [items], set [location], remove [item]]

		# 10. Truncate text

		# 11. Increase paragraph counter
		paragraph_count +=1

		# -> If end reached add text "So this is the end of our story."

		# 12. Generate following paragraph
		# If end is not reached -> Goto 4