from telebot import types
import sqlite3
import time
import os

from todolist_secret_info import bot


class Text:
    num: int = 0
    name: str = 'text'

    def add_data(self, text_mes: object, imp: str, note: object) -> None:
        """Adding text note to the DB"""
        Text.num += 1
        n = Text.num
        conn = sqlite3.connect(f'ToDoList_text.sql')
        cur = conn.cursor()
        cur.execute(f"INSERT INTO text (importance, date, data, id, user_id) VALUES (?, ?, ?, ?, ?)",
                    (imp, time.ctime(), text_mes.text, n, text_mes.chat.id))
        conn.commit()
        cur.close()
        conn.close()

    def del_data(self, id: str, note: object) -> bool:
        """Removal some note from DB"""
        conn = sqlite3.connect(f'ToDoList_{note.name}.sql')
        cur = conn.cursor()
        cur.execute(f'SELECT * FROM {note.name}')
        note_dates = cur.fetchall()
        for i in note_dates:
            if id in i and i[4] == t.user_id:
                cur.execute(f'DELETE FROM {note.name} WHERE id=(?)', (id,))
                conn.commit()
                cur.execute(f'SELECT * FROM {note.name}')
                note_dates = cur.fetchall()
                note_dates.sort()
                for j, el in enumerate(note_dates):
                    cur.execute(f'Update {note.name} set id = ? where id = ?', (j + 1, el[3]))
                    conn.commit()
                cur.close()
                conn.close()
                return True
        return False

    def show_data(self, for_del: bool = False) -> bool or str:
        """Showing text notes"""
        try:
            conn = sqlite3.connect('ToDoList_text.sql')
            cur = conn.cursor()
            cur.execute('SELECT * FROM text')
            text_notes = cur.fetchall()
            text_notes.sort(reverse=True)
            self.info = ''
            if for_del:
                for k, el in enumerate(text_notes):
                    if self.user_id == el[4]:
                        self.info += f'{el[3]}: {el[2]}\n\n'
            else:
                k = 0
                for el in text_notes:
                    if self.user_id == el[4]:
                        k += 1
                        self.info += f'заметка №{k}: {el[2]}\n\n'
            cur.close()
            conn.close()
            return self.info
        except:
            return False


t = Text()


class Image(Text):
    info: list = []
    name: str = 'image'

    def add_data(self, img: object, imp: str, note: object) -> None:
        """Creating a new directory to save images and documents.
        Adding image and document notes to theirs DB."""
        conn = sqlite3.connect(f'ToDoList_{note.name}.sql')
        cur = conn.cursor()
        Image.num += 1
        n = Image.num
        code_path = os.getcwd()
        if note is i:
            file_info = bot.get_file(img.photo[len(img.photo) - 1].file_id)
            p = n
        else:
            file_info = bot.get_file(img.document.file_id)
            p = img.document.file_name
        downloaded_file = bot.download_file(file_info.file_path)

        if not os.path.exists('tdl_bot_files'):
            os.mkdir('tdl_bot_files')
        os.chdir('tdl_bot_files')
        if not os.path.exists(f'{note.name}s'):
            os.mkdir(f'{note.name}s')
            os.chdir(f'{note.name}s')
        os.chdir(code_path)
        with open(fr'tdl_bot_files/{note.name}s/{p}', 'wb') as file:
            file.write(downloaded_file)
            file_path = code_path + fr'/tdl_bot_files/{note.name}s/{p}'
        file_path = file_path.replace('\\', '/')
        cur.execute(f'INSERT INTO {note.name} (importance, date, data, id, user_id) VALUES (?, ?, ?, ?, ?)',
                    (imp, time.ctime(), file_path, n, img.chat.id))
        conn.commit()
        cur.close()
        conn.close()

    def show_data(self, note: object) -> bool or list:
        """Adding to 'info' paths to files (documents or images)"""
        try:
            conn = sqlite3.connect(f'ToDoList_{note.name}.sql')
            cur = conn.cursor()
            cur.execute(f'SELECT * FROM {note.name}')
            text_notes = cur.fetchall()
            text_notes.sort(reverse=True)
            self.info = []
            for note in text_notes:
                if note[4] == t.user_id:
                    self.info.append(note)
            cur.close()
            conn.close()
            return self.info
        except:
            return False


i = Image()


class Document(Image):
    name: str = 'document'


d = Document()


def restart_func() -> object:
    """Return user to start menu"""
    mk = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton('назад в меню', callback_data='back')
    mk.add(btn)
    return mk


def show_doc_and_img(message: object, data: list, note_class: object, for_del: bool = False) -> None:
    """Showing image and document notes"""
    for k, el in enumerate(data):
        if not for_del:
            text = f'заметка №{k+1}'
        else:
            text = f'{el[3]}:'
        with open(el[2], 'rb') as file:
            if note_class is i:
                bot.send_photo(message.chat.id, file, caption=text)
            elif note_class is d:
                bot.send_document(message.chat.id, file, caption=text)
    if for_del:
        bot.send_message(message.chat.id, f'*напишите id заметки, которую надо удалить*\n'
                                          '(все, что до двоеточия)', parse_mode='Markdown',
                         reply_markup=restart_func())
        bot.register_next_step_handler(message, text_registration, note=note_class, removal=True)


def add_importance(message: object, note: object) -> None:
    """Adding importance of note"""
    if message.text not in ['1', '2', '3']:
        bot.send_message(message.chat.id, 'Введено некорректное значение. Повторите попытку')
        bot.register_next_step_handler(message, add_importance, note)
    else:
        if note is t:
            t.importance = message.text
            t.add_data(t.mes, t.importance, t)
        elif note in [i, d]:
            i.importance = message.text
            i.add_data(i.mes, i.importance, note)
        bot.send_message(message.chat.id, 'заметка успешно добавлена!')


@bot.message_handler(commands=['start'])
def start_func(message: object) -> None:
    """Start menu. Create data bases"""

    t.user_id = str(message.chat.id)

    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton('добавить заметку', callback_data='add')
    btn2 = types.InlineKeyboardButton('удалить заметку', callback_data='del')
    btn3 = types.InlineKeyboardButton('показать заметки', callback_data='show')
    markup.add(btn1, btn2, btn3)

    bot.send_message(message.chat.id, 'Выбери то, что хочешь сделать', reply_markup=markup)

    conn = sqlite3.connect('DataBases/ToDoList_text.sql')
    conn1 = sqlite3.connect('DataBases/ToDoList_document.sql')
    conn2 = sqlite3.connect('DataBases/ToDoList_image.sql')
    cur = conn.cursor()
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    cur.execute(
        'CREATE TABLE IF NOT EXISTS \
        text (importance varchar(250), date varchar(250), data varchar(250), id varchar(250), user_id varchar(250))')
    cur1.execute(
        'CREATE TABLE IF NOT EXISTS \
        document (importance varchar(250), date varchar(250), data varchar(250), id varchar(250), user_id varchar(250))')
    cur2.execute(
        'CREATE TABLE IF NOT EXISTS \
        image (importance varchar(250), date varchar(250), data varchar(250), id varchar(250), user_id varchar(250))')
    conn.commit()
    conn1.commit()
    conn2.commit()
    cur.close()
    cur1.close()
    cur2.close()
    conn.close()
    conn1.close()
    conn2.close()


@bot.message_handler(content_types=['text'])
def text_registration(message: object, note: bool = None, removal: bool = False) -> None:
    """Reading a text note"""
    if removal:
        if t.del_data(message.text, note):
            bot.send_message(message.chat.id, 'заметка успешно удалена!')
        else:
            bot.send_message(message.chat.id, 'введено некорректное значение\nповторите попытку')
            bot.register_next_step_handler(message, text_registration, note, True)
    else:
        bot.reply_to(message, 'Выберите, насколько важно данное событие. 1-наименние важно, 3-наиболее важно',
                     reply_markup=restart_func())
        t.mes: object = message
        bot.register_next_step_handler(message, add_importance, t)


@bot.message_handler(content_types=['photo'])
def photo_registration(message: object) -> None:
    """Reading an image note"""
    bot.reply_to(message, 'Выберите, насколько важно данное событие. 1-наименние важно, 3-наиболее важно')
    i.mes: object = message
    bot.register_next_step_handler(message, add_importance, i)


@bot.message_handler(content_types=['document'])
def doc_registration(message: object) -> None:
    """Reading a document note"""
    bot.reply_to(message, 'Выберите, насколько важно данное событие. 1-наименние важно, 3-наиболее важно')
    i.mes: object = message
    bot.register_next_step_handler(message, add_importance, d)


@bot.callback_query_handler(func=lambda call: True)
def callback(call: object) -> None:
    """Operations of the buttons"""
    if call.data == 'add':
        bot.send_message(call.message.chat.id, 'отправьте то, что хотите сохранить',
                         reply_markup=restart_func())
    elif call.data == 'show':
        markup = types.InlineKeyboardMarkup(row_width=3)
        btn1 = types.InlineKeyboardButton('текстовые', callback_data='sh_text')
        btn2 = types.InlineKeyboardButton('изображения', callback_data='sh_image')
        btn3 = types.InlineKeyboardButton('документы', callback_data='sh_doc')
        btn4 = types.InlineKeyboardButton('назад в меню', callback_data='back')
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(call.message.chat.id, 'выберите, что хотите посмотреть', reply_markup=markup)
    elif call.data == 'sh_text':
        if t.show_data():
            bot.send_message(call.message.chat.id, f'*текстовые заметки:*', parse_mode='Markdown')
            bot.send_message(call.message.chat.id, t.info)
        else:
            bot.send_message(call.message.chat.id, f'*текстовые заметки не найдены*', parse_mode='Markdown')
    elif call.data == 'sh_image':
        if i.show_data(i):
            bot.send_message(call.message.chat.id, f'*заметки-изображения:*', parse_mode='Markdown')
            bot.send_message(call.message.chat.id, show_doc_and_img(call.message, i.info, i))
        else:
            bot.send_message(call.message.chat.id, f'*заметки-изображения не найдены*', parse_mode='Markdown')
    elif call.data == 'sh_doc':
        if i.show_data(d):
            bot.send_message(call.message.chat.id, f'*заметки-документы:*', parse_mode='Markdown')
            bot.send_message(call.message.chat.id, show_doc_and_img(call.message, i.info, d))
        else:
            bot.send_message(call.message.chat.id, f'*заметки-документы не найдены*', parse_mode='Markdown')
    elif call.data == 'del':
        markup = types.InlineKeyboardMarkup(row_width=3)
        btn1 = types.InlineKeyboardButton('текст', callback_data='del_text')
        btn2 = types.InlineKeyboardButton('изображение', callback_data='del_image')
        btn3 = types.InlineKeyboardButton('документ', callback_data='del_doc')
        btn4 = types.InlineKeyboardButton('назад в меню', callback_data='back')
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(call.message.chat.id, 'выберите, что хотите удалить', reply_markup=markup)
    elif call.data == 'del_text':
        if t.show_data():
            bot.send_message(call.message.chat.id, t.show_data(for_del=True))
            bot.send_message(call.message.chat.id, f'*напишите id заметки, которую надо удалить*\n'
                                                   '(все, что до двоеточия)', parse_mode='Markdown',
                             reply_markup=restart_func())
            bot.register_next_step_handler(call.message, text_registration, t, True)
        else:
            bot.send_message(call.message.chat.id, f'*текстовые заметки не найдены*', parse_mode='Markdown')
    elif call.data == 'del_image':
        if i.show_data(i):
            bot.send_message(call.message.chat.id, show_doc_and_img(call.message, i.info, i, for_del=True))
        else:
            bot.send_message(call.message.chat.id, f'*заметки-изображения не найдены*', parse_mode='Markdown')
    elif call.data == 'del_doc':
        if i.show_data(d):
            bot.send_message(call.message.chat.id, show_doc_and_img(call.message, i.info, d, for_del=True))
        else:
            bot.send_message(call.message.chat.id, f'*заметки-документы не найдены*', parse_mode='Markdown')
    elif call.data == 'back':
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
        start_func(call.message)


bot.infinity_polling()
