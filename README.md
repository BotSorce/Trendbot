# ربات تلگرام ترند-یاب

ربات فارسی تلگرام برای دریافت موضوعات داغ بر اساس کشور. نسخهٔ فعلی Google Trends را از RSS عمومی می‌خواند و Reddit را به‌عنوان یک سیگنال جداگانهٔ محبوبیت جامعه نمایش می‌دهد. امتیاز Reddit حجم جست‌وجو نیست.

## قابلیت‌ها

- انتخاب کشور و سپس منبع از داخل تلگرام
- دریافت ترندها از Google Trends و پست‌های محبوب Reddit
- نرمال‌سازی پاسخ‌ها و نمایش مرتب همراه لینک منبع
- کش Redis با TTL مستقل برای هر منبع (Google Trends: پنج دقیقه، Reddit: ده دقیقه)
- ذخیرهٔ هر دریافت موفق به‌صورت snapshot در SQLite یا PostgreSQL
- به‌روزرسانی زمان‌بندی‌شده با ARQ، هر ۳۰ دقیقه برای کشورهایی که در `REFRESH_COUNTRIES` مشخص شده‌اند
- retry برای خطاهای موقت شبکه، گزارش خطا با Loguru و فایل لاگ روزانه

## راه‌اندازی محلی

1. با [@BotFather](https://t.me/BotFather) یک بات بسازید و توکن آن را در `.env` قرار دهید. توکن را در Git یا پیام عمومی ذخیره نکنید.
2. `.env.example` را به `.env` کپی کنید.
3. وابستگی‌ها را نصب کنید:

   ```bash
   uv sync
   ```

4. Redis را اجرا کنید و سپس در دو ترمینال جداگانه بات و worker را شروع کنید:

   ```bash
   python main.py
   uv run arq trend_finder.worker.WorkerSettings
   ```

SQLite به‌صورت پیش‌فرض در `data/trend_finder.db` ساخته می‌شود.

## اجرا با Docker Compose

```bash
cp .env.example .env
# TELEGRAM_BOT_TOKEN را در .env تنظیم کنید
docker compose up --build -d
docker compose logs -f bot
```

Compose شامل بات، worker زمان‌بندی‌شده و Redis است. داده‌های SQLite و لاگ‌ها در volume باقی می‌مانند.

### استفاده از PostgreSQL

سرویس PostgreSQL در profile جدا قرار دارد. مقدار `TREND_FINDER_DATABASE_URL` را در `.env` تنظیم کنید:

```env
TREND_FINDER_DATABASE_URL=postgresql+asyncpg://trend_finder:change-me@postgres:5432/trend_finder
POSTGRES_PASSWORD=change-me
```

سپس اجرا کنید:

```bash
docker compose --profile postgres up --build -d
```

برای استقرار واقعی، رمز پیش‌فرض را عوض کنید و آن را در Secrets نگه دارید.

## دستورات ربات

- `/start` — انتخاب کشور و منبع
- `/trends` — شروع دوبارهٔ انتخاب
- `/help` — راهنمای کوتاه

کشورهای فعلی: آمریکا، بریتانیا، آلمان، فرانسه، کانادا، استرالیا، هند، ژاپن، برزیل، ترکیه، ایران، امارات، عربستان سعودی، اسپانیا، ایتالیا، هلند، کره جنوبی، مکزیک، اندونزی و روسیه.

## کیفیت و تست

```bash
uv run pytest
uv run ruff check .
uv run black --check .
uv run mypy trend_finder
```

## ساختار

```text
trend_finder/
  cache.py                 # Redis و TTL
  config.py                # تنظیمات Pydantic
  database/                # مدل‌ها و راه‌اندازی SQLAlchemy async
  handlers.py              # جریان گفت‌وگوی تلگرام
  sources/                 # آداپترهای مستقل هر منبع
  services/trend_service.py
  worker.py                # زمان‌بندی ARQ
tests/
```

## نکات منابع

- Google Trends از RSS عمومی Trending Now استفاده می‌کند؛ ممکن است در برخی کشورها یا زمان‌ها خالی یا موقتاً در دسترس نباشد.
- Reddit با پارامتر منطقه درخواست می‌شود، اما ممکن است این فیلتر را اعمال نکند؛ نتیجه همچنان «پست‌های محبوب» است و نباید به‌عنوان ترند جست‌وجو یا آمار قطعی کشور تعبیر شود.
- هر منبع جدید باید آداپتر مستقلی با `key`، `label`، `ttl_seconds` و `fetch(country_code)` داشته باشد و در `trend_finder/sources/__init__.py` ثبت شود. منابع نیازمند API key فقط پس از افزودن کلید امن و پیاده‌سازی adapter فعال شوند.
