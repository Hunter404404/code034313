import telebot
import db
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = '7703568590:AAH7g7xwoX-KUvb-Ouhk1DzKGc-z-eOunwQ'
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    db.save_user_choice(user_id, 'prologue', None, None)  # Сохранение начального этапа
    scenario = db.get_scenario('prologue')
    bot.send_message(user_id, "---------Code:034313---------")

    if scenario:
        text, choice1, _, _, choice2, _, _, choice3, _, _ = scenario
        markup = create_choices_inline_keyboard(choice1, choice2, choice3)
        sent_message = bot.send_message(user_id, text, reply_markup=markup)
        db.save_user_choice(user_id, 'prologue', None, sent_message.message_id)



@bot.callback_query_handler(func=lambda call: True)
def handle_choice(call):
    user_id = call.message.chat.id
    user_data = db.get_user_data(user_id)

    if not user_data:
        bot.answer_callback_query(call.id, "Ошибка. Введите /start, чтобы начать игру.")
        return

    current_stage, _, message_id = user_data
    scenario = db.get_scenario(current_stage)

    if scenario:
        text, choice1, choice1_result, choice1_end, choice2, choice2_result, choice2_end, choice3, choice3_result, choice3_end = scenario

        if call.data == "choice1":
            next_stage = choice1_result
            end_text = choice1_end
        elif call.data == "choice2":
            next_stage = choice2_result
            end_text = choice2_end
        elif call.data == "choice3":
            next_stage = choice3_result
            end_text = choice3_end
        else:
            bot.answer_callback_query(call.id, "Ошибка. Выберите вариант.")
            return

        if next_stage == "end_game":
            bot.edit_message_text(chat_id=user_id, message_id=message_id,
                                  text=end_text + "\n"
                                                  "Конец игры. Введите /start, чтобы начать заново.")
            db.save_user_choice(user_id, None, None, None)
        else:
            next_scenario = db.get_scenario(next_stage)
            if next_scenario:
                next_text, next_choice1, _, _, next_choice2, _, _, next_choice3, _, _ = next_scenario
                markup = create_choices_inline_keyboard(next_choice1, next_choice2, next_choice3)
                bot.edit_message_text(chat_id=user_id, message_id=message_id, text=next_text, reply_markup=markup)
                db.save_user_choice(user_id, next_stage, call.data, message_id)
            else:
                bot.edit_message_text(chat_id=user_id, message_id=message_id,
                                      text=end_text + "\nКонец игры. Введите /start, чтобы начать заново.")
                db.save_user_choice(user_id, None, None, None)



def create_choices_inline_keyboard(choice1, choice2=None, choice3=None):
    markup = InlineKeyboardMarkup()
    if choice1:
        markup.add(InlineKeyboardButton(choice1, callback_data="choice1"))
    if choice2:
        markup.add(InlineKeyboardButton(choice2, callback_data="choice2"))
    if choice3:
        markup.add(InlineKeyboardButton(choice3, callback_data="choice3"))
    return markup



if __name__ == "__main__":
    db.init_db()
    db.populate_scenarios()
    bot.polling(none_stop=True)
