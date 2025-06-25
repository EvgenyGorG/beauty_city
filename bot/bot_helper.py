from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard(action_type, button_rows):
    keyboard = [
        [InlineKeyboardButton(text=button_label, callback_data=f"{action_type}_{row_index}")]
        for row_index, [button_label] in enumerate(button_rows)
    ]
    return InlineKeyboardMarkup(keyboard)
