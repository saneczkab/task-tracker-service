import httpx
import os
from datetime import datetime
from app.schemas.analytics import TaskAnalytics, UserTaskStats, TaskBrief


class AIReportService:

    YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID", "")
    YANDEX_API_KEY = os.getenv("YANDEX_API_KEY", "")

    @staticmethod
    def generate_summary(
        analytics: TaskAnalytics,
        users_stats: list[UserTaskStats],
        tasks: list[TaskBrief],
        team_name: str,
        period: str = None,
    ) -> str:
        """Генерация аналитического резюме с персональными данными"""

        period_text = {"week": "за последнюю неделю", "month": "за последний месяц"}.get(period, "за весь период")

        users_text = ""
        for user in users_stats:
            if user.total_tasks > 0:
                users_text += f"\n- {user.nickname}: выполнено {user.completed_tasks}/{user.total_tasks}, просрочено {user.overdue_tasks}"

        overdue_tasks = [t for t in tasks if t.deadline and t.deadline < datetime.now() and t.status_id != 4]
        tasks_text = ""
        if overdue_tasks:
            tasks_text = "\nПросроченные задачи:\n"
            for task in overdue_tasks[:50]:
                users = ", ".join(task.assigned_users) if task.assigned_users else "не назначены"
                tasks_text += f"- {task.name} (исполнители: {users})\n"

        prompt = f"""
        Ты — аналитик проектов. Проанализируй данные по команде "{team_name}" {period_text}.

        Общая статистика:
        - Всего задач: {analytics.total_tasks}
        - Выполнено вовремя: {analytics.completed_on_time} ({analytics.completion_rate}%)
        - В работе: {analytics.in_progress}
        - Просрочено: {analytics.overdue}

        Статистика по участникам:{users_text}
        {tasks_text}

        Напиши короткое аналитическое резюме (3-4 предложения). Выдели:
        1. Общую картину по команде
        2. Кто из участников нуждается в поддержке (много просрочек или невыполненных задач)
        3. Конкретную рекомендацию по улучшению ситуации

        Используй профессиональный, но простой язык. Без лишнего текста.
        """

        body = {
            "modelUri": f"gpt://{AIReportService.YANDEX_FOLDER_ID}/yandexgpt-lite",
            "completionOptions": {"stream": False, "temperature": 0.5, "maxTokens": 250},
            "messages": [
                {"role": "system", "text": "Ты — помощник, эксперт по управлению проектами. Отвечай кратко и по делу."},
                {"role": "user", "text": prompt},
            ],
        }

        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        headers = {"Authorization": f"Api-Key {AIReportService.YANDEX_API_KEY}", "Content-Type": "application/json"}

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, headers=headers, json=body)
                response.raise_for_status()

                result = response.json()
                if "result" in result and "alternatives" in result["result"]:
                    return result["result"]["alternatives"][0]["message"]["text"].strip()

                print(f"Неожиданный формат ответа от YandexGPT: {result}")
                return AIReportService._fallback_summary(analytics, team_name, period)

        except httpx.TimeoutException:
            print("Ошибка: Таймаут при запросе к YandexGPT API")
        except httpx.HTTPStatusError as e:
            print(f"Ошибка HTTP при запросе к YandexGPT: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            print(f"Общая ошибка при запросе к YandexGPT: {e}")

        return AIReportService._fallback_summary(analytics, team_name, period)

    @staticmethod
    def _fallback_summary(analytics: TaskAnalytics, team_name: str, period: str = None) -> str:
        """Простая текстовая заглушка на случай ошибки или отсутствия API-ключа."""
        period_text = "за этот период"
        if analytics.overdue > 0:
            return f"Есть {analytics.overdue} просроченных задач. Рекомендуется пересмотреть дедлайны."
        elif analytics.completion_rate > 70:
            return f"Отличный результат! {analytics.completion_rate}% задач выполнено {period_text}."
        else:
            return f"Выполнено {analytics.completed_on_time} из {analytics.total_tasks} задач {period_text}. Ускорьте работу над активными задачами."
