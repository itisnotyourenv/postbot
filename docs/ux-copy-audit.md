# PostMagnet UX/Copy Audit

> Date: 2026-02-12
> Status: Draft — awaiting review

---

## Current User Journey

```
/start -> Language selection -> "Hello, {name}!" -> [Create Post] [My Posts]
```

### Onboarding flow (new user)
1. `/start` -> "Please select your language:" (EN/RU)
2. Select language -> "Привет, {name}!" + main menu buttons
3. No explanation of what the bot does

### Returning user
1. `/start` -> "Привет, {name}!" + main menu buttons

### Post creation wizard
1. "Choose post type:" -> Photo / Video / Text / GIF
2. "Send me {type}..."
3. "Add inline buttons. Format: [Text + URL + color]..." (technical DSL)
4. Preview -> Confirm -> "Post saved! Use: @bot key"

---

## Problems & Recommendations

### 1. Onboarding is almost non-existent (HIGH impact)

**Current:** After language selection, new user only sees `"Привет, {name}!"` with two buttons. No explanation of what the bot does, why it's useful, how it works.

**Recommendation:** Show a welcome screen with value proposition after language selection.

```ftl
# EN
welcome = Hey, { $name }! I'm PostMagnet.

    I help you create beautiful posts with buttons and share them in any Telegram chat via inline mode.

    Tap "Create Post" to get started!

# RU
welcome = Привет, { $name }! Я — PostMagnet.

    Создавайте посты с кнопками и мгновенно делитесь ими в любом чате Telegram через инлайн-режим.

    Нажмите «Создать пост», чтобы начать!
```

---

### 2. DSL button syntax scares users (HIGH impact)

**Current:** Wall of text with technical syntax `[Text + URL + color]`. Colors are English words even in RU locale (`default, green, red`).

```ftl
# Current RU
send-buttons-dsl = Теперь добавьте инлайн-кнопки.
    Формат: [Текст + URL + цвет]
    Каждая строка = новый ряд. Цвета: default, green, red.
    Нажмите Пропустить, чтобы пропустить.
    Пример:
    [Купить + https://example.com + green]
    [Поддержка + https://help.com + red]
```

**Recommendation:** Simplify, make human-friendly. Color is optional — lead with the simple form first.

```ftl
# RU
send-buttons-dsl = Добавьте кнопки со ссылками.

    Каждая строка — одна кнопка:
    [Название + ссылка]

    Хотите цветную кнопку? Добавьте цвет:
    [Название + ссылка + green]

    Цвета: green, red, blue

    Пример:
    [Купить + https://example.com + green]
    [Помощь + https://help.com]

# EN
send-buttons-dsl = Add buttons with links.

    Each line is one button:
    [Label + URL]

    Want a colored button? Add color:
    [Label + URL + green]

    Colors: green, red, blue

    Example:
    [Buy + https://example.com + green]
    [Help + https://help.com]
```

---

### 3. Post-saved message doesn't explain what to do next (HIGH impact)

**Current:**
```
post-saved-header = Пост сохранён! Использование:
-> @bot_username abc12345
```
User doesn't understand what to do with this.

**Recommendation:**

```ftl
# RU
post-saved-header = Пост сохранён!

    Чтобы отправить его в любой чат, введите в поле сообщения:

# EN
post-saved-header = Post saved!

    To share it in any chat, type in the message field:
```

Optional new key with additional tip:
```ftl
# RU
post-saved-tip = Просто начните набирать @{ $bot_username } в любом чате, и выберите ваш пост из списка.

# EN
post-saved-tip = Just start typing @{ $bot_username } in any chat and pick your post from the list.
```

---

### 4. No progress indicator in wizard (MEDIUM impact)

**Current:** User doesn't know how many steps remain.

**Recommendation:** Add step numbers to wizard prompts.

```ftl
# RU
choose-post-type = Шаг 1 из 3 — Выберите тип поста:
send-text-content = Шаг 2 из 3 — Отправьте текст для поста:
send-photo-content = Шаг 2 из 3 — Отправьте фото (можно добавить подпись):
send-video-content = Шаг 2 из 3 — Отправьте видео (можно добавить подпись):
send-gif-content = Шаг 2 из 3 — Отправьте GIF (можно добавить подпись):
send-buttons-dsl = Шаг 3 из 3 — Добавьте кнопки...

# EN
choose-post-type = Step 1 of 3 — Choose post type:
send-text-content = Step 2 of 3 — Send me the text for your post:
send-photo-content = Step 2 of 3 — Send me a photo (you can add a caption):
send-video-content = Step 2 of 3 — Send me a video (you can add a caption):
send-gif-content = Step 2 of 3 — Send me a GIF (you can add a caption):
send-buttons-dsl = Step 3 of 3 — Add buttons...
```

---

### 5. Help text is too minimal (MEDIUM impact)

**Current:**
```
help-text = Этот бот позволяет создавать посты с инлайн-кнопками
и делиться ими через инлайн-режим. Используйте /start для начала.
```

**Recommendation:** Structured help with numbered steps.

```ftl
# RU
help-text = Как пользоваться PostMagnet:

    1. Нажмите «Создать пост» и выберите тип (текст, фото, видео, GIF)
    2. Отправьте контент
    3. Добавьте кнопки со ссылками (необязательно)
    4. Подтвердите — вы получите уникальный ключ

    Чтобы отправить пост в чат, введите @{ $bot_username } и ваш ключ в любом чате.

    /start — главное меню
    /settings — настройки
    /referral — реферальная ссылка

# EN
help-text = How to use PostMagnet:

    1. Tap "Create Post" and choose a type (text, photo, video, GIF)
    2. Send your content
    3. Add buttons with links (optional)
    4. Confirm — you'll get a unique key

    To share a post, type @{ $bot_username } and your key in any chat.

    /start — main menu
    /settings — settings
    /referral — referral link
```

Note: requires passing `$bot_username` variable to help-text in code.

---

### 6. Empty states don't motivate (MEDIUM impact)

**Current:** `my-posts-empty = У вас пока нет постов.`

**Recommendation:**

```ftl
# RU
my-posts-empty = У вас пока нет постов.
    Нажмите «Создать пост», чтобы создать первый!

# EN
my-posts-empty = You don't have any posts yet.
    Tap "Create Post" to create your first one!
```

---

### 7. Button labels can be more informative (MEDIUM impact)

| Current (RU)  | Recommendation (RU)  | Current (EN) | Recommendation (EN) |
|---------------|----------------------|--------------|----------------------|
| Пропустить    | Без кнопок           | Skip         | No buttons           |
| Подтвердить   | Сохранить пост       | Confirm      | Save post            |
| Изменить      | Начать заново        | Edit         | Start over           |
| Отмена        | Отмена (ok)          | Cancel       | Cancel (ok)          |

---

### 8. Preview screen needs clearer CTA (MEDIUM impact)

**Current:** `preview-title = Предпросмотр:` + hint about resending buttons

**Recommendation:**

```ftl
# RU
preview-title = Так будет выглядеть ваш пост.

    Всё верно? Нажмите «Сохранить пост».
    Хотите поменять кнопки? Отправьте их заново в формате [Текст + ссылка].

# EN
preview-title = Here's how your post will look.

    Happy with it? Tap "Save post".
    Want to change buttons? Send them again in [Label + URL] format.
```

---

### 9. Error messages don't help (LOW impact)

**Current:** `invalid-dsl = Не удалось разобрать кнопки.`

**Recommendation:**

```ftl
# RU
invalid-dsl = Неверный формат кнопок.
    Проверьте, что каждая кнопка в формате:
    [Текст + https://ссылка]

# EN
invalid-dsl = Invalid button format.
    Make sure each button follows this format:
    [Label + https://url]
```

---

## Priority Matrix

| #  | What                                  | Impact | Effort | Files affected        |
|----|---------------------------------------|--------|--------|-----------------------|
| 1  | Welcome screen with value proposition | HIGH   | LOW    | `locales/*/start.ftl` |
| 2  | Simplified DSL hint                   | HIGH   | LOW    | `locales/*/post.ftl`  |
| 3  | Post-saved with clear instructions    | HIGH   | LOW    | `locales/*/post.ftl`  |
| 4  | Wizard step indicators (1/2/3)        | MEDIUM | LOW    | `locales/*/post.ftl`  |
| 5  | Structured help text                  | MEDIUM | LOW    | `locales/*/post.ftl` + code change |
| 6  | Motivating empty states               | MEDIUM | LOW    | `locales/*/post.ftl`  |
| 7  | Better button labels                  | MEDIUM | LOW    | `locales/*/post.ftl`  |
| 8  | Clearer preview screen                | MEDIUM | LOW    | `locales/*/post.ftl`  |
| 9  | Helpful error messages                | LOW    | LOW    | `locales/*/post.ftl`  |

---

## Code Changes Required

Most changes are text-only (FTL files). The only code changes needed:

1. **help-text** (`commands.py`): Pass `bot_username` to `i18n.get("help-text", bot_username=config.telegram.bot_username)` — requires injecting `Config` into `command_help_handler`.

2. **post-saved-tip** (optional new key): If adding the tip, add it to `post_wizard.py` in `confirm_post`.

---

## Implementation Notes

- All FTL changes are backward-compatible (key names stay the same)
- Step numbers (Step X of 3) can be added without code changes — just edit FTL text
- Button label changes (`btn-skip`, `btn-confirm`, `btn-edit`) affect the whole app — verify all usages before changing
- Test the multiline FTL strings (indentation matters in Fluent)
