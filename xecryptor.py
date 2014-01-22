#!/usr/bin/python

'''

xecryptor.py - Application for Encrypting and Decrypting plain text using the (weak) XECryption algorithm.

Features:
- Compatible with Unicode characters.
- GUI!

Notes:
- Very little sanity checking.
- User is uninformed of serious errors.

Will M. Temple 08/28/13 22:22
wt@wpi.edu

Built for Python 3.3.2 with PyGObject 3.8.3-1

'''

from gi.repository import Gtk
from random import randint
from math import floor

#Mode function for integer list - batteries included.
#Saves importing another library.
def mode(int_list):
    current_leader = 0
    score_to_beat = 0
    for value in int_list:
        ocurrences = int_list.count(value)
        if ocurrences > score_to_beat:
            current_leader = value
            score_to_beat = ocurrences

    return current_leader

#Class that does all mathematical operations on text to en/decrypt.
class XECrypt:

    #Utility method: Finds numerical value for password.
    def resolve_pwd(self, pwd):

        pwd_value = 0        
        for pwd_char in list(pwd):
            pwd_value += ord(pwd_char)
        
        return pwd_value
    
    #Utility method: Returns usable integer array from array representing triplet code.
    #Adds each triplet together to produce one integer representing the encoded character plus the value of the password.
    def resolve_enc_array(self, enc_array):

        return_list = []
        counter = 0
        running_total = 0

        for value in enc_array:

            #The leading '.' at the beginning  of XECrypted text causes int() to throw a ValueError.
            #Since the leading '.' is insignificant to the encryption, we may safely pass that case.
            try:
                running_total += int(value)
            except ValueError:
                counter -= 1

            counter += 1

            if counter == 3:
                counter = 0
                return_list.append(running_total)
                running_total = 0

        return return_list

    #Encodes plain text into xecrypted text.
    def encode(self, plain_text, pwd):

        final_text = ''
        unenc_char_array = list(plain_text)

        for char in unenc_char_array:
            base_value = ord(char) + self.resolve_pwd(pwd)
            numbers = [ 0, 0, 0 ]
            numbers[0] = floor(base_value / 3) + randint(-10, 10)
            numbers[1] = floor(base_value / 3) + randint(-10, 10)
            numbers[2] = base_value - (numbers[0] + numbers[1])
            final_text += ('.' + '.'.join(str(x) for x in numbers))

        return final_text

    #Decodes xecrypted text given the encryption password.
    def decode(self, crypto_text, pwd):
        
        final_text = ''
        pwd_value = self.resolve_pwd(pwd)
        enc_value_array = self.resolve_enc_array(crypto_text.split('.'))

        for value in enc_value_array:
            final_text += chr( value - pwd_value )

        return final_text

    #Very, very simple bruteforcing algorithm that may be thwarted by smart encryptors.
    #This algorithm assumes that the most common ASCII character in the plain text is ' '.
    def bruteforce(self, crypto_text):

        final_text = ''
        enc_value_array = self.resolve_enc_array(crypto_text.split('.'))
        pwd_value = mode(enc_value_array) - ord(' ')

        for value in enc_value_array:
            final_text += chr(value - pwd_value)

        return final_text

# Application class that binds UI events to XECryption algorithms.
class XECryptor:

    xecrypt = XECrypt()
    gladefile = 'xecryptor.glade'
    builder = Gtk.Builder()

    def __init__(self):

        #Load Glade XML and retrieve window-main.
        self.builder.add_from_file(self.gladefile)
        self.builder.connect_signals(self)
        window = self.builder.get_object('window-main')
        window.show_all()

        #Workaround for an odd glade bug.
        combobox = self.builder.get_object('mode-dropdown')
        combobox.set_active(0)

        # Begin GTK loop
        Gtk.main()
        
    def onApplyButton(self, button):

        mode = self.builder.get_object('mode-dropdown').get_active()
        text_entry_buffer = self.builder.get_object('text-entry').get_buffer()
        text = text_entry_buffer.get_text(text_entry_buffer.get_start_iter(), text_entry_buffer.get_end_iter(), True)

        if mode == 2:
            text_entry_buffer.set_text(self.xecrypt.bruteforce(text))
        else:
            pwd = self.builder.get_object('pwd-entry').get_text()
            if mode == 1:
                text_entry_buffer.set_text(self.xecrypt.encode(text, pwd))
            if mode == 0:
                text_entry_buffer.set_text(self.xecrypt.decode(text, pwd))

    def onModeChange(self, combobox):

        pwd_box = self.builder.get_object('pwd-entry') 
      
        if combobox.get_active() == 2:
            pwd_box.set_text('')
            pwd_box.set_sensitive(False)
        else:
            pwd_box.set_sensitive(True)

    def onWindowDestroy(self, *args):
        Gtk.main_quit()

xecryptor = XECryptor()
