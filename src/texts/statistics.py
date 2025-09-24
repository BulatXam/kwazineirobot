user_statistic = lambda user, statistic_text: f"""
<b>Пользователь №{user.id}</b>

Имя: <b>{user.first_name}</b>
Фамиля: <b>{user.last_name}</b>
Никнейм: <b>{user.username}</b>

Осталось текстовых запросов: <b>{round(user.daily_text_limit)}</b>
Осталось запросов изображений: <b>{round(user.daily_image_limit)}</b>

{statistic_text}
"""

user_history = lambda current_page, pages_count, neiro_responses_in_page_len, all_neiro_responses_count: f"""
Страница: <b>{current_page}</b>
Всего страниц:<b>{pages_count}</b>
Запросов в странице: <b>{neiro_responses_in_page_len}</b>
Всего запросов в нейросеть: {all_neiro_responses_count}
"""

user_history_response = lambda neiro_response: f"""
Модель: <b>{neiro_response.model}</b>

Промпт: <b>{neiro_response.prompt}</b>
Ответ: <b><code>{neiro_response.content}</code></b>

Потрачено токенов: <b>{neiro_response.total_tokens}</b>
"""
