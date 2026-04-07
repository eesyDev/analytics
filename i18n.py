locales = {
    "RU": {
        # app.py
        "⚙️ Settings": "⚙️ Настройки",
        "🌐 Language / Язык": "🌐 Language / Язык",
        "Client / Site Name": "Клиент / Название сайта",
        "My Site": "Мой сайт",
        "Intent Classification": "Классификация интента",
        "Brand terms (one per line)": "Брендовые запросы (с новой строки)",
        "Informational terms (one per line)": "Информационные запросы",
        "how to\nwhat is\nmake money\ndepreciation\nfinancing\nhow long\nhow much\ncan you\nis a\nstarting a\nclearing land\nhourly rate\nguide\ntips\nvs\nreviews": "как\nчто такое\nguide\ntips\nvs\nотзывы",
        "URL keywords → Blog page (one per line)": "Ключевые слова URL → Блог",
        "how-to\nwhat-is\nguide\ntips\nblog\narticle": "how-to\nguide\nblog\narticle\nстатья",
        "📁 Current Period — GSC": "📁 Текущий период — GSC",
        "Google Search Console → Performance → Export CSV": "Google Search Console → Эффективность → Скачать CSV",
        "Queries.csv": "Queries.csv",
        "Pages.csv": "Pages.csv",
        "Devices.csv": "Devices.csv",
        "Countries.csv": "Countries.csv",
        "Chart.csv (time series)": "Chart.csv (time series)",
        "📁 Previous Period — GSC": "📁 Предыдущий период — GSC",
        "Same exports for the prior period (WoW / MoM)": "Те же отчеты за прошлый период (WoW / MoM)",
        "Queries.csv (prev)": "Queries.csv (previous)",
        "Pages.csv (prev)": "Pages.csv (previous)",
        "Chart.csv (prev)": "Chart.csv (previous)",
        "🔍 Cannibalization": "🔍 Каннибализация",
        "GSC → Performance → add Pages + Queries dimensions → export": "GSC → Эффективность → Вкладка 'Страницы'+'Запросы' → Экспорт",
        "Query+Page export CSV": "Query + Page export CSV",
        "🎥 Hotjar (optional)": "🎥 Hotjar (опционально)",
        "Funnel export CSV": "Funnel export CSV",
        "Homepage heatmap": "Тепловая карта: Главная",
        "Product page heatmap": "Тепловая карта: Страница товара",
        "Cart page heatmap": "Тепловая карта: Корзина",
        "Universal SEO Audit Tool · Built with Streamlit + Plotly": "Универсальный SEO-аудит · Создан на Streamlit + Plotly",
        "⬆️  Upload GSC CSV files in the sidebar to get started.": "⬆️ Загрузите CSV файлы GSC в панели слева для старта.",
        "Or place CSV files in the `data/` directory next to app.py.": "Или поместите CSV файлы в папку `data/`.",
        "## 📊 {client_name} — SEO Performance Audit": "## 📊 {client_name} — SEO Аудит (Performance)",
        "**Period:** {date_range} &nbsp;|&nbsp; **Source:** Google Search Console &nbsp;|&nbsp; **Queries analyzed:** {q_count:,}": "**Период:** {date_range} &nbsp;|&nbsp; **Источник:** Google Search Console &nbsp;|&nbsp; **Запросов разобрано:** {q_count:,}",
        "<small style='color:#888'>Audit generated · {date_range} · Source: Google Search Console · Built with Streamlit + Plotly</small>": "<small style='color:#888'>Сгенерировано · {date_range} · Источник: Google Search Console · Streamlit + Plotly</small>",

        # hotjar.py
        "🎥 User Behavior Analysis (Hotjar)": "🎥 Анализ поведения пользователей (Hotjar)",
        "Hotjar data not yet connected.": "Данные Hotjar пока не загружены.",
        "GSC shows *who finds the site* — Hotjar reveals *why they don't convert.*": "GSC показывает, *кто приходит*, а Hotjar — *почему они не покупают*.",
        "Upload a funnel CSV and/or heatmap screenshots in the sidebar.": "Загрузите CSV воронки и/или скриншоты тепловых карт слева.",
        "**Conversion Funnel**": "**Конверсионная Воронка**",
        "Conversion Funnel (Hotjar)": "Конверсионная Воронка (Hotjar)",
        "Недостаточно данных для анализа bottleneck.": "Недостаточно данных для анализа 'бутылочного горлышка'.",
        "Hotjar CSV missing required columns: **Step** and **Users**. Please export the funnel report with these headers.": "В CSV Hotjar отсутствуют колонки: **Step** и **Users**.",
        "**Heatmaps**": "**Тепловые карты**",

        # tldr.py
        "📋 TL;DR — Executive Summary": "📋 TL;DR — Краткая сводка",
        "**🔴 Top Problems**": "**🔴 Главные проблемы**",
        "No critical issues found.": "Критичных проблем не найдено.",
        "**✅ Priority Actions**": "**✅ Приоритетные действия**",
        "**{count:,} impressions** go to waste — site ranks but users don't click (0 clicks on {n} queries)": "**{count:,} показов** сгорают — сайт в топе, но кликов нет (0 кликов у {n} запросов)",
        "Rewrite title tags for top {n} zero-click queries → est. **+{opp:,} clicks/period** at zero cost": "Перепишите title для топ-{n} запросов без кликов → привнесет **+{opp:,} кликов** бесплатно",
        "**{pct:.0f}% of clicks** land on blog/informational pages with no purchase path": "**{pct:.0f}% кликов** падает на блог/статьи без пути к покупке",
        "Add product CTAs to every blog post → convert existing traffic without new content": "Добавьте продуктовые кнопки CTA в каждую статью",
        "Desktop ranks at **position {dt:.1f}** vs mobile **{mob:.1f}** — B2B buyers can't find the site": "Рейтинг десктопа **{dt:.1f}** сильно ниже мобильного **{mob:.1f}** — B2B клиенты вас не находят",
        "Run desktop technical SEO audit (Core Web Vitals, structured data)": "Проведите технический SEO-аудит десктопа (Core Web Vitals)",
        "**{count} featured snippet opportunities** (pos 2–5, informational) → format as Q&A / bullet lists to capture answer boxes": "**{count} потенциальных snippet-ов** (информ. запросы на 2-5 местах) → оформите в виде Q&A",
        "**{count} cannibalizing queries** — multiple pages competing, splitting authority": "**{count} каннибализированных запросов** — страницы конкурируют друг с другом",
        "Total estimated missed clicks: **~{opp:,}**. Quick wins alone could recover **{r1:,}–{r2:,} clicks** without new content or backlinks.": "Упущено кликов: **~{opp:,}**. Только быстрые решения вернут **{r1:,}–{r2:,} кликов** без новых ссылок.",

        # kpis.py
        "📌 KPIs": "📌 Главные метрики (KPI)",
        "Total Clicks": "Всего Кликов",
        "Total Impressions": "Всего Показов",
        "Weighted CTR": "Взвешенный CTR",
        "Weighted Avg Position": "Средняя Позиция",
        "Estimated Missed Clicks": "Упущенные клики (потенциал)",
        "Impressions-weighted CTR — more accurate than simple average": "CTR, взвешенный по показам (точнее обычного)",
        "Lower = better. Green delta = position improved.": "Меньше = лучше. Зеленая дельта = рост позиций.",
        "Additional clicks if all queries reached benchmark CTR for their position": "Клики, если бы CTR достигал нормы для позиций",
        "⚠️ GSC sampling: on high-traffic properties Google may show only a fraction of actual data. Treat all figures as directional — export to BigQuery for exact counts.": "⚠️ Сэмплинг GSC: на сайтах с высоким трафиком Google может показывать лишь часть реальных данных. Воспринимайте цифры как ориентировочные — для точных значений используйте экспорт в BigQuery.",

        # trend.py
        "📈 Traffic Trend": "📈 Тренд трафика",
        "Clicks": "Клики",
        "Impressions": "Показы",
        "Date": "Дата",
        "Day": "День",
        "📊 Period-over-Period Comparison": "📊 Сравнение периодов",
        "Current period": "Текущий период",
        "Previous period": "Прошлый период",
        "**Top growing queries**": "**Топ растущих запросов**",
        "**Top declining queries**": "**Топ падающих запросов**",
        "**Page movers**": "**Изменения по страницам**",
        "Click change vs previous period": "Динамика кликов к прошлому периоду",
        "**New queries this period**": "**Новые запросы в этом периоде**",
        "**Queries that dropped out**": "**Запросы, выпавшие из выдачи**",
        "⚠️ Statistical note: query-level changes over short periods (7–14 days) reflect normal ranking variance as much as real trends. Focus on directional patterns across groups, not individual query swings.": "⚠️ Статистика: изменения на уровне отдельных запросов за короткий период (7–14 дней) могут быть просто шумом, а не настоящим трендом. Смотрите на общие паттерны, а не на отдельные скачки.",

        # findings.py
        "🔴 Critical Findings": "🔴 Критические наблюдения",
        "Blog / informational pages drive **{pct:.0f}%** of clicks but have no direct purchase intent. Only **{diff:.0f}%** of clicks land on product or category pages.": "Инфо-страницы собирают **{pct:.0f}%** кликов без покупательского спроса. Ишь **{diff:.0f}%** уходит на товары/категории.",
        "**{imp:,} impressions** across **{n}** queries received zero clicks. The site ranks — but users don't click. Title tags and meta descriptions need immediate attention.": "**{imp:,} показов** и **{n}** запросов собрали ноль кликов. Сайт в выдаче, но его игнорируют. Срочно обновите Title и Meta.",
        "**{pct:.0f}%** of clicks are branded queries. Non-brand organic traffic is critically low — almost all traffic comes from users who already know the brand.": "**{pct:.0f}%** кликов — это запросы бренда. Органика почти нулевая, трафик идет только от тех, кто вас уже знает.",
        "Desktop ranking ({dt:.1f}) is significantly worse than mobile ({mob:.1f}) — a gap of {gap:.1f} positions. B2B buyers who research on desktop see you below competitors.": "Десктоп ({dt:.1f}) сильно отстает от мобильных устройств ({mob:.1f}). Разрыв {gap:.1f} позиций. B2B клиенты видят вас ниже конкурентов.",
        "**{n}** queries with 20+ impressions achieve less than half the benchmark CTR for their ranking position. These pages rank well but fail to attract clicks.": "**{n}** запросов с 20+ показами имеют CTR в два раза ниже нормы для их позиций. Страницы в топе, но не забирают клики.",
        "No critical issues detected based on current data.": "Критичных проблем в данный момент не выявлено.",

        # opportunities.py
        "**Opportunity Score** = estimated additional clicks if CTR reaches benchmark for current position. This is a directional estimate — actual results depend on SERP features, competition, and content quality.": "**Упущенный потенциал** = добавочные клики при достижении нормы CTR для данной позиции. Это ориентировочная оценка — фактический результат зависит от SERP-формата, конкуренции и качества контента.",
        "⚠️ Note: queries with 0 clicks but high impressions may rank in featured snippets, knowledge panels, or below multiple ads — where organic clicks are structurally lower. Verify in GSC before prioritizing.": "⚠️ Важно: запросы с 0 кликов при высоких показах могут занимать featured snippets, knowledge panel или находиться ниже нескольких рекламных блоков — там органических кликов меньше по природе. Проверьте в GSC перед тем, как ставить их в приоритет.",
        "🎯 Opportunity Matrix — CTR vs Position": "🎯 Матрица Потенциала (CTR / Позиция)",
        "Queries below the red benchmark line are underperforming. Size = Impressions.": "Запросы ниже красной линии нормы — отстающие.",
        "Each bubble = one query (≥5 impressions)": "Каждая точка — запрос (≥5 показов)",
        "Avg. Position (lower = better)": "Средн. Позиция (меньше = лучше)",
        "CTR %": "CTR %",
        "Industry benchmark CTR": "Отраслевая норма CTR",
        "💡 Prioritized Quick Wins": "💡 Быстрые победы (Quick Wins)",
        "**Opportunity Score** = estimated additional clicks if CTR reaches benchmark for current position.": "**Упущенный потенциал** = добавочные клики при достижении среднеотраслевого CTR.",
        "Total estimated missed clicks: **~{opp:,}**. Fixing title tags for the top 10 queries can recover a significant share at zero cost.": "Потенциал потерянных кликов: **~{opp:,}**. Оптимизация заголовков у топ-10 запросов вернет солидную долю совершенно бесплатно.",
        "No opportunity data — check that Queries.csv has Position and CTR columns.": "Нет данных (проверьте, что в Queries.csv есть столбцы Position и CTR).",

        # cannibalization.py
        "⚠️ Keyword Cannibalization": "⚠️ Каннибализация ключевых слов",
        "**To detect cannibalization:** In GSC → Performance, click the *Pages* tab, add the *Queries* dimension, and export. Upload the result in the sidebar.": "**Для поиска каннибализации:** Сделайте выгрузку из GSC одновременно по Страницам и Запросам.",
        "Queries where 2+ pages compete for the same keyword — Google picks one, others dilute authority.": "Две и более страниы соревнуются за 1 запрос — они поедают рейтинги друг друга.",
        "No cannibalization detected.": "Каннибализации не обнаружено.",
        "Cannibalizing queries": "Число конфликтов",
        "Impressions at risk": "Показов под угрозой",
        "Clicks at risk": "Кликов под угрозой",
        "**Top cannibalizing queries (by impressions)**": "**Топ запросов-каннибалов**",
        "**How to fix:** For each group, pick one canonical page and consolidate content there. 301-redirect or noindex the weaker pages.": "**Как исправить:** Выберите одну каноническую страницу. Настройте на нее 301 редирект или проставьте canonical со слабых страниц.",

        # Pages / Categories
        "📄 Top Pages — Performance & Type": "📄 Топ Страницы — Показатели и Интент",
        "Top 20 pages — red = informational/blog": "Топ 20 страниц (красным — информационные)",
        "**CTR & Position for top pages**": "**Позиции и CTR главных страниц**",

        # Intents
        "🎯 Search Intent Distribution": "🎯 Распределение Интента",
        "Share of impressions by intent": "Доля показов по интентам",
        "Impressions vs Clicks by intent": "Показы и Клики по интентам",
        "Commercial / Product queries represent only **{pct:.0f}%** of impressions. The SEO strategy is optimised for awareness, not purchase intent.": "Коммерческие запросы занимают лишь **{pct:.0f}%** показов. Стратегия работает на 'узнаваемость', а не на реальные продажи.",

        # Position / Length
        "📊 Ranking Position Distribution": "📊 Распределение по позициям",
        "Distribution of ranking positions": "Распределение рейтинга",
        "Page 2 boundary": "Граница 2-й страницы",
        "**Queries by position tier**": "**Запросы по ярусам позиций**",
        "**{p11}** queries on page 2 vs **{p4}** on page 1. Content updates could push many to page 1.": "**{p11}** запросов на 2-й стр. Google против **{p4}** на 1-й. Точечное обновление контента перенесет их в ТОП-10.",
        "🔤 Query Length Analysis (Head vs Long-Tail)": "🔤 Анализ длины запросов",
        "Longer queries = lower volume but higher purchase intent and easier to rank for.": "Длинные запросы = меньше объем, но выше конверсия.",
        "Impressions by query length": "Показы по длине запроса",
        "Avg CTR % and Position by query length": "CTR и Позиции по длине запроса",
        "Long-tail queries (3+ words) make up **{pct:.0f}%** of impressions but convert at **{ctr:.2f}% CTR** vs **{ht:.2f}%** for head terms. Targeting long-tail keywords is a high-ROI strategy.": "Длинные 'Long-tail' запросы (3+ слова) - это **{pct:.0f}%** показов, их кликабельность **{ctr:.2f}% CTR** против **{ht:.2f}%**. Отличная стратегия для высокого ROI.",
        "Long-tail queries (3+ words) account for **{pct:.0f}%** of impressions.": "Доля 'Long-tail' запросов (3+ слов) составляет **{pct:.0f}%** показов.",
        
        # Snippets
        "⭐ Featured Snippet Opportunities": "⭐ Потенциал Featured Snippets (Блока ответов)",
        "Queries ranking **position 2–5** with informational intent — prime candidates for answer boxes.": "Инфо-запросы на **позициях 2–5** — идеальные кандидаты для блока быстрых ответов (Position Zero).",
        "**How to capture the snippet:**": "**Как захватить сниппет:**",
        "1. Add a direct 40–60 word answer at the top of the page\n2. Use the exact query phrase as an H2 header\n3. For list queries: use `<ul>` / `<ol>` with concise items\n4. For definition queries: bolded term + 1-sentence definition\n5. Add FAQ schema markup\n6. Internal links with anchor text = the query": "1. Добавьте прямой ответ (40-60 слов) в начало страницы\n2. Сделайте H2 с точной формулировкой запроса\n3. Если это список — используйте `<ul>` или `<ol>`\n4. Добавьте разметку FAQ Schema\n5. Укрепите внутренними ссылками с нужными анкорами",
        "**{n}** opportunities. Top: *\"{q}\"* — pos {pos:.1f}, {imp:,} impressions.": "**{n}** возможностей. Топ: *\"{q}\"* — поз. {pos:.1f}, {imp:,} показов.",
        "No snippet opportunities found (need queries at position 2–5, informational intent, 10+ impressions).": "Нет кандидатов на сниппеты (нужны инфо-запросы на 2-5 местах с 10+ показами).",

        # Devices & Geo
        "📱 Device Performance": "📱 Эффективность по Устройствам",
        "Clicks vs Impressions by device": "Клики и Показы по устройствам",
        "Avg. ranking position by device (lower = better)": "Средняя позиция по устройствам",
        "Desktop position {dt:.1f} vs mobile {mob:.1f} — gap of {gap:.1f} positions. Run a dedicated desktop technical audit: Core Web Vitals, structured data, PageSpeed.": "Десктоп ({dt:.1f}) проигрывает мобильным ({mob:.1f}) на {gap:.1f} пунктов. Нужен строгий тех-аудит десктопа.",
        "Desktop ({dt:.1f}) slightly weaker than mobile ({mob:.1f}). Monitor for widening.": "Десктоп ({dt:.1f}) слегка слабее мобильной ({mob:.1f}) версии. Продолжайте наблюдение.",
        "🌍 Geographic Performance": "🌍 География",
        "Top 10 countries — color = CTR%": "Топ 10 стран — цвет означает CTR%",
        "**Country CTR breakdown**": "**Разбивка CTR по странам**",
        "**{c} drives {pct:.0f}% of clicks.** Markets with above-average CTR: **{names}** — geo-targeted content may unlock disproportionate growth here.": "**{c} дает {pct:.0f}% кликов.** Рынки с CTR выше среднего: **{names}** — локализованный контент даст здесь мощный рост.",

        # Recs & Export
        "✅ Prioritized Recommendations": "✅ Приоритетные Рекомендации",
        "⬇️ Export": "⬇️ Скачать отчеты",
        "📥 Quick Wins (CSV)": "📥 Быстрые победы (CSV)",
        "📥 Recommendations (CSV)": "📥 Все рекомендации (CSV)",
        "📥 All Queries Scored (CSV)": "📥 Все разобранные запросы (CSV)",

        # Recommendations list items
        "URGENT": "СРОЧНО",
        "HIGH": "ВЫСОКО",
        "LOW": "НИЗКО",
        "Rewrite title tags & meta descriptions for zero-click queries": "Переписать Title и Meta Description для запросов без кликов",
        "{imp:,} impressions, 0 clicks. Start with Quick Wins table top 10 — these already rank, fixing CTR costs nothing.": "{imp:,} показов, 0 кликов. Исправление CTR вернет органику абсолютно бесплатно.",
        "Add product CTAs to all informational / blog pages": "Добавить продуктовые CTA (формы) в блог-статьи",
        "{pct:.0f}% of clicks land on blog pages with no path to purchase. Add contextually relevant product banners and internal links to every article.": "{pct:.0f}% кликов идёт в статьи без пути к покупке. Срочно внедрить продуктовые баннеры.",
        "Desktop SEO technical audit": "Технический SEO аудит десктопной версии",
        "Desktop ranks at {dt:.1f} vs mobile {mob:.1f}. Audit Core Web Vitals, structured data, and PageSpeed for desktop.": "Рейтинг десктопа - {dt:.1f}, мобильных - {mob:.1f}. Проведите проверку Core Web Vitals.",
        "Set up Hotjar conversion funnel tracking": "Настроить трекинг конверсионной воронки (Hotjar)",
        "Install: Product → Add to Cart → Checkout → Order confirmation. This identifies the single biggest conversion bottleneck.": "Повесьте шаги: Товар → Выбор → Корзина → Заказ. Выясните главную 'дыру' воронки.",
        "Create dedicated commercial landing pages": "Создать коммерческие посадочные страницы",
        "Only {pct:.0f}% of impressions are commercial (buyer) queries. Build pages targeting product + intent keywords (\"X for sale\", \"X price\", etc.).": "Только {pct:.0f}% коммерческих показов. Создайте страницы под интенты покупки (цена, прайс, купить).",
        "Fix keyword cannibalization": "Устранить каннибализацию ключей",
        "{n} queries have 2+ competing pages. Consolidate to one canonical per topic, redirect the rest.": "{n} запросов делят 2+ страниц. Нужно оставить по канонической странице на 1 тему.",
        "Expand into high-CTR international markets": "Расширить влияние в новые ГЕО",
        "{names} show above-average CTR. Geo-targeted content or hreflang could yield disproportionate growth.": "ГЕО: {names} показывают высокий CTR. Настройте Hreflang для роста.",
    }
}

def get_text(lang, key, *args, **kwargs):
    """
    args[0] = positional fallback string (used when key is a short lookup key).
    kwargs  = format arguments.
    """
    text = locales.get(lang, {}).get(key, args[0] if args else key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
