# Skill: Dashboard Helper (مساعد الداشبورد)

## Description
مهارة مساعدة لربط وإعداد لوحات تحكم OpenClaw بشكل تلقائي. تحل مشكلة "الداشبورد المثبت لكن غير المربوط".

## Created By
- **المبدع:** أسترو 🤖✨ (الروبوت المساعد الذكي)
- **للمدير:** أحمد خالد
- **التاريخ:** 2026-03-15
- **السياق:** إصلاح مشكلة ربط الداشبورد المتطور بعد التثبيت

## Problem Statement (بيان المشكلة)

### المشكلة الأصلية:
1. مستخدم يثبت مهارة `openclaw-dashboard` من ClawHub
2. الداشبورد يشتغل لكن **لا يرتبط بـ OpenClaw Gateway**
3. **لا تظهر بيانات العميل** في الداشبورد
4. التعليمات في `SKILL.md` **لا تشرح كيفية الحصول على التوكن تلقائياً**

### السبب:
- التوكن (`OPENCLAW_AUTH_TOKEN`) **غير مضبوط تلقائياً**
- الداشبورد **لا يعرف كيفية الحصول على التوكن** من OpenClaw
- المستخدم يضطر للبحث يدوياً عن التوكن

## Capabilities

### 1. الحصول التلقائي على التوكن
- استخدام `openclaw dashboard --no-open` لاستخراج التوكن
- معالجة الناتج واستخراج التوكن تلقائياً
- التعامل مع حالات الفشل

### 2. إعداد ملف البيئة
- إنشاء أو تحديث ملف `.env`
- ضبط `OPENCLAW_AUTH_TOKEN` بالتوكن الصحيح
- إضافة متغيرات بيئة أخرى إذا لزم الأمر

### 3. إيجاد بورت متاح
- البحث عن بورت غير مستخدم
- تجنب تعارض المنافذ
- استخدام نطاق منافذ آمن

### 4. تشغيل الداشبورد
- تشغيل `api-server.js` في الخلفية
- التحقق من التشغيل الناجح
- توفير الرابط النهائي للمستخدم

### 5. توفير الرابط الصحيح
- تضمين التوكن في الرابط (`?token=xxx`)
- التأكد من أن الرابط يعمل
- توفير تعليمات فتح المتصفح

## Workflow

### الخطوة 1: الحصول على التوكن
```bash
# محاولة استخراج التوكن من openclaw dashboard
TOKEN=$(openclaw dashboard --no-open 2>&1 | grep -o "token=[a-f0-9]*" | cut -d= -f2 | head -1)

# إذا فشل، استخدام التوكن من device-auth.json
if [ -z "$TOKEN" ]; then
  TOKEN=$(grep -o '"token":"[^"]*"' ~/.openclaw/identity/device-auth.json | cut -d'"' -f4 | head -1)
fi
```

### الخطوة 2: إعداد ملف .env
```bash
cd ~/.openclaw/workspace/skills/openclaw-dashboard
echo "OPENCLAW_AUTH_TOKEN=$TOKEN" > .env
echo "DASHBOARD_HOST=127.0.0.1" >> .env
```

### الخطوة 3: إيجاد بورت متاح
```bash
for port in {18792..18850}; do
  if ! lsof -i :$port > /dev/null 2>&1; then
    AVAILABLE_PORT=$port
    break
  fi
done
```

### الخطوة 4: تشغيل الداشبورد
```bash
cd ~/.openclaw/workspace/skills/openclaw-dashboard
DASHBOARD_PORT=$AVAILABLE_PORT node api-server.js > /tmp/openclaw-dashboard.log 2>&1 &
DASHBOARD_PID=$!
```

### الخطوة 5: التحقق والتقرير
```bash
sleep 2
if curl -s "http://127.0.0.1:$AVAILABLE_PORT?token=$TOKEN" > /dev/null; then
  echo "✅ Dashboard running on: http://127.0.0.1:$AVAILABLE_PORT?token=$TOKEN"
  echo "📊 PID: $DASHBOARD_PID"
else
  echo "❌ Dashboard failed to start"
fi
```

## Integration with openclaw-dashboard Skill

### الحل المثالي:
يجب أن يقوم مطور `openclaw-dashboard` بإضافة هذه الوظائف تلقائياً إلى `SKILL.md`:

```yaml
agent_instructions: |
  After installing openclaw-dashboard, you must:
  1. Get the auth token automatically using openclaw dashboard --no-open
  2. Create .env file with OPENCLAW_AUTH_TOKEN
  3. Find an available port and start the server
  4. Provide the complete URL to the user
```

### الحل الحالي (البديل):
هذه المهارة (`dashboard-helper`) هي حل بديل حتى يتم إصلاح المهارة الأصلية.

## Usage Examples

### مثال 1: إعداد الداشبورد تلقائياً
```
"أسترو، ربط لي الداشبورد المتطور بالـ Gateway"
```

### مثال 2: الحصول على التوكن فقط
```
"أسترو، أعطني التوكن الحقيقي لـ OpenClaw"
```

### مثال 3: تشغيل على بورت محدد
```
"أسترو، شغل الداشبورد على البورت 18888"
```

### مثال 4: التحقق من التشغيل
```
"أسترو، هل الداشبورد شغال؟"
```

## التنفيذ العملي

### السكريبت الجاهز: `setup_dashboard.sh`
يوجد سكريبت كامل في `skills/dashboard-helper/setup_dashboard.sh` يقوم بـ:

1. الحصول التلقائي للتوكن
2. إعداد ملف `.env`
3. البحث عن بورت متاح
4. تشغيل الداشبورد
5. التحقق من التشغيل
6. توفير الرابط النهائي

### كيفية الاستخدام:
```bash
cd ~/.openclaw/workspace/skills/dashboard-helper
./setup_dashboard.sh
```

## التعليمات للروبوت (لأسترو)

### عندما يطلب المستخدم "ربط الداشبورد":
1. تحقق من وجود مهارة `openclaw-dashboard`
2. إذا غير موجودة: `npx clawhub@latest install openclaw-dashboard`
3. نفذ السكريبت: `./skills/dashboard-helper/setup_dashboard.sh`
4. قدم الرابط النهائي للمستخدم

### عندما يطلب المستخدم "التوكن فقط":
1. استخدم: `openclaw dashboard --no-open`
2. استخرج التوكن من الناتج
3. قدم التوكن مع ملاحظة أنه قد يتغير

### عندما يطلب المستخدم "البورت X":
1. تحقق من أن البورت متاح
2. عدل السكريبت ليناسب البورت المطلوب
3. شغل الداشبورد على ذلك البورت

## Notes

### لماذا هذه المشكلة تحدث؟
1. **فجوة تصميمية:** ClawHub skills مصممة للاستخدام اليدوي، ليس للروبوتات
2. **افتقار للتعليمات:** لا توجد تعليمات مخصصة للروبوتات في `SKILL.md`
3. **التوكن الديناميكي:** التوكن يتغير مع الوقت، يحتاج تحديث تلقائي

### دروس مستفادة:
- مهارات OpenClaw يجب أن تحتوي على **تعليمات للروبوت** وليس فقط للمستخدم
- **التوكن يجب أن يُحصل عليه تلقائياً** بعد كل تثبيت
- **الروبوت يجب أن يتحقق** من عمل الداشبورد بعد التشغيل

---

**🤖 توقيع:** أسترو - الذي اكتشف فجوة في نظام المهارات وحلها بطريقة مبتكرة!