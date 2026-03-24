function applyAiFormat(actionType) {
    const textarea = document.querySelector('textarea[name="content"]');
    const selectedText = textarea.value.substring(textarea.selectionStart, textarea.selectionEnd);

    if (!selectedText && actionType !== 'создай таблицу') {
        alert("Сначала выделите текст!");
        return;
    }

    // Отправляем запрос на сервер к нашему View
    fetch("/ai-format/", {
        method: "POST",
        headers: {
            "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: `text=${encodeURIComponent(selectedText)}&action=${actionType}`
    })
    .then(response => response.json())
    .then(data => {
        // Заменяем выделенный текст на ответ от нейросети (HTML)
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        textarea.setRangeText(data.result, start, end, 'select');
    });
}