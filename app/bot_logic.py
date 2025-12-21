import re
import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class Movie:
    title: str
    genres: Tuple[str, ...]
    year: int
    rating: float  # условный рейтинг 0..10
    mood: Tuple[str, ...] = ()
    tags: Tuple[str, ...] = ()


class MovieRecommenderBot:
    """Логика бота для рекомендации фильмов (расширенная версия, рандомная выдача)"""

    def __init__(self):
        self.keywords_patterns: Dict[str, List[str]] = {
            "greeting": [r"\b(привет|здравствуй|добрый день|хай|hello|hi)\b"],
            "help": [r"\b(помощь|help|что умеешь|возможности|команд)\b"],
            "bye": [r"\b(пока|до свидания|увидимся|bye|goodbye)\b"],
            "thanks": [r"\b(спасибо|thanks|thx)\b"],

            # Жанры
            "comedy": [r"\b(комеди[яи]|смешн|юмор|весел(ый|о)|посмеяться)\b"],
            "action": [r"\b(боевик|экшен|action|драк|стрелялк)\b"],
            "drama": [r"\b(драм[аы]|серьезн|глубок)\b"],
            "horror": [r"\b(ужас|хоррор|horror|страшн)\b"],
            "fantasy": [r"\b(фантасти[кч]|фэнтези|fantasy|маг|волшебн)\b"],
            "romance": [r"\b(романтик|любов|мелодрам)\b"],
            "detective": [r"\b(детектив|расследован|thriller|триллер|загадк)\b"],

            # Настроение/пожелания
            "mood_fun": [r"\b(весел|легк|поднять настроение|расслаб)\b"],
            "mood_dark": [r"\b(мрачн|темн|жестк|жутк)\b"],
            "mood_inspiring": [r"\b(вдохнов|мотивац|доброе|теплое)\b"],
            "mood_brain": [r"\b(умн|головоломк|подумать|сюжетн)\b"],

            # Фильтры
            "filter_new": [r"\b(нов(ое|ый|ые)|свежее|последн(ее|ий))\b"],
            "filter_old": [r"\b(стар(ое|ый|ые)|классик)\b"],
            "filter_short": [r"\b(коротк|до\s*90\s*мин)\b"],
            "filter_long": [r"\b(длинн|эпик|3\s*час)\b"],
        }

        self.catalog: List[Movie] = [
            Movie("Назад в будущее", ("comedy", "fantasy"), 1985, 8.5, mood=("mood_fun", "mood_inspiring")),
            Movie("Маска", ("comedy", "fantasy"), 1994, 6.9, mood=("mood_fun",)),
            Movie("Один дома", ("comedy",), 1990, 7.6, mood=("mood_fun",)),
            Movie("Джентльмены удачи", ("comedy",), 1971, 8.2, mood=("mood_fun",)),
            Movie("Служебный роман", ("comedy", "romance"), 1977, 8.1, mood=("mood_fun", "mood_inspiring")),
            Movie("Ла-Ла Ленд", ("romance", "drama"), 2016, 8.0, mood=("mood_inspiring",)),
            Movie("Перед рассветом", ("romance", "drama"), 1995, 8.1, mood=("mood_brain",)),
            Movie("Зеленая миля", ("drama",), 1999, 9.0, mood=("mood_inspiring",)),
            Movie("Побег из Шоушенка", ("drama",), 1994, 9.3, mood=("mood_inspiring",)),
            Movie("1+1", ("drama", "comedy"), 2011, 8.5, mood=("mood_inspiring", "mood_fun")),
            Movie("Матрица", ("action", "fantasy"), 1999, 8.7, mood=("mood_brain",)),
            Movie("Джон Уик", ("action",), 2014, 7.4, mood=("mood_dark",)),
            Movie("Безумный Макс: Дорога ярости", ("action",), 2015, 8.1, mood=("mood_dark",)),
            Movie("Тёмный рыцарь", ("action", "drama"), 2008, 9.0, mood=("mood_dark", "mood_brain")),
            Movie("Остров проклятых", ("detective", "drama"), 2010, 8.2, mood=("mood_brain", "mood_dark")),
            Movie("Семь", ("detective", "drama"), 1995, 8.6, mood=("mood_dark",)),
            Movie("Исчезнувшая", ("detective", "drama"), 2014, 8.1, mood=("mood_brain",)),
            Movie("Молчание ягнят", ("detective", "drama"), 1991, 8.6, mood=("mood_dark", "mood_brain")),
            Movie("Тихое место", ("horror",), 2018, 7.5, mood=("mood_dark",)),
            Movie("Заклятие", ("horror",), 2013, 7.5, mood=("mood_dark",)),
            Movie("Наследственное", ("horror",), 2018, 7.3, mood=("mood_dark",)),
            Movie("Властелин колец: Братство кольца", ("fantasy", "action"), 2001, 8.8, mood=("mood_inspiring",)),
            Movie("Гарри Поттер и философский камень", ("fantasy",), 2001, 7.6, mood=("mood_inspiring", "mood_fun")),

            Movie("Иван Васильевич меняет профессию", ("comedy", "fantasy"), 1973, 8.8, mood=("mood_fun",)),
            Movie("Кавказская пленница", ("comedy",), 1967, 8.5, mood=("mood_fun",)),
            Movie("Операция «Ы» и другие приключения Шурика", ("comedy",), 1965, 8.7, mood=("mood_fun",)),
            Movie("Бриллиантовая рука", ("comedy",), 1968, 8.7, mood=("mood_fun",)),
            Movie("12 стульев", ("comedy",), 1971, 8.3, mood=("mood_fun",)),
            Movie("Some Like It Hot / В джазе только девушки", ("comedy", "romance"), 1959, 8.2, mood=("mood_fun",)),
            Movie("The Grand Budapest Hotel / Отель «Гранд Будапешт»", ("comedy",), 2014, 8.1, mood=("mood_fun", "mood_brain")),
            Movie("The Hangover / Мальчишник в Вегасе", ("comedy",), 2009, 7.7, mood=("mood_fun",)),
            Movie("Groundhog Day / День сурка", ("comedy", "fantasy"), 1993, 8.0, mood=("mood_fun", "mood_inspiring")),
            Movie("The Truman Show / Шоу Трумана", ("comedy", "drama"), 1998, 8.2, mood=("mood_brain", "mood_inspiring")),
            Movie("Jojo Rabbit / Кролик Джоджо", ("comedy", "drama"), 2019, 7.9, mood=("mood_inspiring", "mood_fun")),
            Movie("Knives Out / Достать ножи", ("comedy", "detective"), 2019, 7.9, mood=("mood_brain", "mood_fun")),
            Movie("The Intouchables / 1+1 (дубль)", ("drama", "comedy"), 2011, 8.5, mood=("mood_inspiring", "mood_fun")),

            Movie("Forrest Gump / Форрест Гамп", ("drama", "romance"), 1994, 8.8, mood=("mood_inspiring",)),
            Movie("The Godfather / Крестный отец", ("drama",), 1972, 9.2, mood=("mood_dark", "mood_brain")),
            Movie("The Godfather Part II / Крестный отец 2", ("drama",), 1974, 9.0, mood=("mood_dark", "mood_brain")),
            Movie("Schindler's List / Список Шиндлера", ("drama",), 1993, 9.0, mood=("mood_inspiring", "mood_dark")),
            Movie("Fight Club / Бойцовский клуб", ("drama",), 1999, 8.8, mood=("mood_dark", "mood_brain")),
            Movie("Whiplash / Одержимость", ("drama",), 2014, 8.5, mood=("mood_inspiring", "mood_brain")),
            Movie("The Pianist / Пианист", ("drama",), 2002, 8.5, mood=("mood_dark", "mood_inspiring")),
            Movie("A Beautiful Mind / Игры разума", ("drama",), 2001, 8.2, mood=("mood_inspiring", "mood_brain")),
            Movie("Joker / Джокер", ("drama",), 2019, 8.4, mood=("mood_dark",)),
            Movie("Parasite / Паразиты", ("drama",), 2019, 8.6, mood=("mood_dark", "mood_brain")),
            Movie("The Prestige / Престиж", ("drama", "detective"), 2006, 8.5, mood=("mood_brain", "mood_dark")),
            Movie("Interstellar / Интерстеллар", ("drama", "fantasy"), 2014, 8.6, mood=("mood_inspiring", "mood_brain")),

            Movie("Titanic / Титаник", ("romance", "drama"), 1997, 7.9, mood=("mood_inspiring",)),
            Movie("Pride & Prejudice / Гордость и предубеждение", ("romance", "drama"), 2005, 7.8, mood=("mood_inspiring",)),
            Movie("The Notebook / Дневник памяти", ("romance", "drama"), 2004, 7.8, mood=("mood_inspiring",)),
            Movie("Her / Она", ("romance", "drama"), 2013, 8.0, mood=("mood_brain",)),
            Movie("Eternal Sunshine of the Spotless Mind / Вечное сияние чистого разума", ("romance", "drama"), 2004, 8.3, mood=("mood_brain", "mood_inspiring")),
            Movie("About Time / Бойфренд из будущего", ("romance", "comedy", "fantasy"), 2013, 7.8, mood=("mood_inspiring", "mood_fun")),
            Movie("500 Days of Summer / (500) дней лета", ("romance", "drama"), 2009, 7.7, mood=("mood_brain",)),
            Movie("Notting Hill / Ноттинг Хилл", ("romance", "comedy"), 1999, 7.2, mood=("mood_fun",)),

            Movie("Gladiator / Гладиатор", ("action", "drama"), 2000, 8.5, mood=("mood_inspiring", "mood_dark")),
            Movie("Inception / Начало", ("action", "drama"), 2010, 8.8, mood=("mood_brain",)),
            Movie("The Lord of the Rings: The Two Towers / ВК: Две крепости", ("fantasy", "action"), 2002, 8.7, mood=("mood_inspiring",)),
            Movie("The Lord of the Rings: The Return of the King / ВК: Возвращение короля", ("fantasy", "action"), 2003, 9.0, mood=("mood_inspiring",)),
            Movie("Terminator 2: Judgment Day / Терминатор 2", ("action",), 1991, 8.6, mood=("mood_dark",)),
            Movie("Die Hard / Крепкий орешек", ("action",), 1988, 8.2, mood=("mood_fun", "mood_dark")),
            Movie("The Bourne Identity / Идентификация Борна", ("action",), 2002, 7.9, mood=("mood_dark", "mood_brain")),
            Movie("The Raid / Рейд", ("action",), 2011, 7.6, mood=("mood_dark",)),
            Movie("Logan / Логан", ("action", "drama"), 2017, 8.1, mood=("mood_dark", "mood_inspiring")),
            Movie("Spider-Man: Into the Spider-Verse / Человек-паук: Через вселенные", ("action", "fantasy"), 2018, 8.4, mood=("mood_fun", "mood_inspiring")),

            Movie("Star Wars: Episode IV / Звёздные войны: Новая надежда", ("fantasy", "action"), 1977, 8.6, mood=("mood_inspiring", "mood_fun")),
            Movie("Avatar / Аватар", ("fantasy", "action"), 2009, 7.8, mood=("mood_inspiring",)),
            Movie("Dune / Дюна", ("fantasy", "drama"), 2021, 8.0, mood=("mood_brain", "mood_dark")),
            Movie("Dune: Part Two / Дюна: Часть вторая", ("fantasy", "action"), 2024, 8.6, mood=("mood_inspiring", "mood_dark")),
            Movie("Blade Runner / Бегущий по лезвию", ("fantasy", "drama"), 1982, 8.1, mood=("mood_dark", "mood_brain")),
            Movie("Blade Runner 2049 / Бегущий по лезвию 2049", ("fantasy", "drama"), 2017, 8.0, mood=("mood_dark", "mood_brain")),
            Movie("Arrival / Прибытие", ("fantasy", "drama"), 2016, 7.9, mood=("mood_brain", "mood_inspiring")),
            Movie("Ex Machina / Из машины", ("fantasy", "drama"), 2014, 7.7, mood=("mood_brain", "mood_dark")),
            Movie("The Fifth Element / Пятый элемент", ("fantasy", "action", "comedy"), 1997, 7.7, mood=("mood_fun", "mood_inspiring")),
            Movie("Harry Potter and the Prisoner of Azkaban / ГП и узник Азкабана", ("fantasy",), 2004, 7.9, mood=("mood_inspiring", "mood_fun")),
            Movie("Harry Potter and the Deathly Hallows: Part 2 / ГП и Дары Смерти 2", ("fantasy",), 2011, 8.1, mood=("mood_inspiring",)),

            Movie("The Girl with the Dragon Tattoo / Девушка с татуировкой дракона", ("detective", "drama"), 2011, 7.8, mood=("mood_dark", "mood_brain")),
            Movie("Prisoners / Пленницы", ("detective", "drama"), 2013, 8.1, mood=("mood_dark", "mood_brain")),
            Movie("Zodiac / Зодиак", ("detective", "drama"), 2007, 7.7, mood=("mood_brain", "mood_dark")),
            Movie("Memento / Помни", ("detective", "drama"), 2000, 8.4, mood=("mood_brain",)),
            Movie("The Usual Suspects / Подозрительные лица", ("detective", "drama"), 1995, 8.5, mood=("mood_brain", "mood_dark")),
            Movie("Oldboy / Олдбой", ("detective", "drama"), 2003, 8.4, mood=("mood_dark", "mood_brain")),
            Movie("No Country for Old Men / Старикам тут не место", ("detective", "drama"), 2007, 8.2, mood=("mood_dark",)),
            Movie("Shutter Island / Остров проклятых (дубль)", ("detective", "drama"), 2010, 8.2, mood=("mood_brain", "mood_dark")),

            Movie("The Shining / Сияние", ("horror",), 1980, 8.4, mood=("mood_dark", "mood_brain")),
            Movie("Alien / Чужой", ("horror", "fantasy"), 1979, 8.5, mood=("mood_dark",)),
            Movie("Aliens / Чужие", ("horror", "action"), 1986, 8.4, mood=("mood_dark", "mood_fun")),
            Movie("Get Out / Прочь", ("horror",), 2017, 7.7, mood=("mood_dark", "mood_brain")),
            Movie("It / Оно", ("horror",), 2017, 7.3, mood=("mood_dark",)),
            Movie("The Conjuring 2 / Заклятие 2", ("horror",), 2016, 7.3, mood=("mood_dark",)),
            Movie("A Quiet Place: Part II / Тихое место 2", ("horror",), 2020, 7.2, mood=("mood_dark",)),
            Movie("The Ring / Звонок", ("horror",), 2002, 7.1, mood=("mood_dark",)),
            Movie("The Exorcist / Изгоняющий дьявола", ("horror",), 1973, 8.1, mood=("mood_dark",)),
        ]

        self.responses: Dict[str, List[str]] = {
            "greeting": [
                "Привет! Напиши жанр (комедия/боевик/драма/ужасы/фэнтези/романтика/детектив) или настроение (веселое/мрачное/вдохновляющее/умное).",
            ],
            "help": [
                "Команды: жанр (комедия, боевик, драма, ужасы, фэнтези, романтика, детектив), настроение (веселое, мрачное, вдохновляющее, умное), фильтры (новое/классика). Пример: «хочу мрачный детектив, что-нибудь новое».",
            ],
            "bye": ["Пока! Если захочешь — напиши жанр или настроение, подберу кино."],
            "thanks": ["Пожалуйста! Хочешь ещё 3 варианта в этом же стиле?"],
            "default": [
                "Не совсем понял. Напиши жанр или настроение. Пример: «легкая комедия» или «умный триллер».",
            ],
        }

        self.last_intent: Dict[str, Optional[str]] = {"genre": None, "mood": None}

    # ---------- Разбор запроса ----------

    def _match_categories(self, text: str) -> List[str]:
        found = []
        for category, patterns in self.keywords_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    found.append(category)
                    break
        return found

    def _extract_intent(self, categories: List[str]) -> Tuple[Optional[str], Optional[str]]:
        genre = None
        mood = None
        for c in categories:
            if c in {"comedy", "action", "drama", "horror", "fantasy", "romance", "detective"}:
                genre = c
            if c.startswith("mood_"):
                mood = c
        return genre, mood

    def _extract_filters(self, categories: List[str]) -> Dict[str, bool]:
        return {
            "new": "filter_new" in categories,
            "old": "filter_old" in categories,
            "short": "filter_short" in categories,
            "long": "filter_long" in categories,
        }

    # ---------- Подбор ----------

    def _apply_filters(self, movies: List[Movie], filters: Dict[str, bool]) -> List[Movie]:
        if filters["new"] and not filters["old"]:
            movies = [m for m in movies if m.year >= 2010]
        if filters["old"] and not filters["new"]:
            movies = [m for m in movies if m.year <= 2005]
        return movies

    def recommend(self, user_message: str, k: int = 4) -> List[Movie]:
        text = user_message.lower()
        categories = self._match_categories(text)
        genre, mood = self._extract_intent(categories)
        filters = self._extract_filters(categories)

        # Память: если жанр/настроение не указаны — пробуем восстановить
        if genre is None:
            genre = self.last_intent["genre"]
        if mood is None:
            mood = self.last_intent["mood"]

        # Если всё равно ничего — вернем пусто
        if genre is None and mood is None:
            return []

        # Обновим память
        self.last_intent["genre"] = genre
        self.last_intent["mood"] = mood

        candidates = self._apply_filters(self.catalog[:], filters)

        # Если жанр задан — сужаем по жанру (если есть хоть кто-то), иначе оставляем всех
        if genre:
            genre_candidates = [m for m in candidates if genre in m.genres]
            if genre_candidates:
                candidates = genre_candidates

        # Если настроение задано — сужаем по настроению (если есть хоть кто-то)
        if mood:
            mood_candidates = [m for m in candidates if mood in m.mood]
            if mood_candidates:
                candidates = mood_candidates

        # ВАЖНО: рандомная выдача каждый раз
        random.shuffle(candidates)
        return candidates[: min(k, len(candidates))]

    # ---------- Ответ ----------

    def get_response(self, user_message: str) -> str:
        text = user_message.lower()
        categories = self._match_categories(text)

        for c in ("greeting", "help", "bye", "thanks"):
            if c in categories:
                return random.choice(self.responses[c])

        recs = self.recommend(user_message, k=4)
        if not recs:
            return random.choice(self.responses["default"])

        lines = ["Вот что могу посоветовать:"]
        for m in recs:
            genres = ", ".join(m.genres)
            lines.append(f"- {m.title} ({m.year}) — {genres}, рейтинг ~{m.rating:.1f}/10")
        lines.append("Хочешь ещё варианты или уточни: жанр/настроение/«новое»/«классика».")

        return "\n".join(lines)


# Singleton экземпляр бота
bot = MovieRecommenderBot()