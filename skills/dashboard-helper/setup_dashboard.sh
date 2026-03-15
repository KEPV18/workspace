#!/bin/bash
# dashboard-helper: حل مشكلة ربط الداشبورد المتطور

set -e

echo "🚀 بدء إعداد الداشبورد المتطور..."
echo "========================================"

# الخطوة 1: الحصول على التوكن
echo "🔑 الخطوة 1: الحصول على التوكن من OpenClaw..."

TOKEN=""
ATTEMPTS=0
MAX_ATTEMPTS=3

while [ -z "$TOKEN" ] && [ $ATTEMPTS -lt $MAX_ATTEMPTS ]; do
    echo "   المحاولة $((ATTEMPTS+1)) من $MAX_ATTEMPTS..."
    
    # محاولة استخراج التوكن من openclaw dashboard
    DASHBOARD_OUTPUT=$(timeout 10 openclaw dashboard --no-open 2>&1 || true)
    
    # محاولة استخراج التوكن من الناتج
    if echo "$DASHBOARD_OUTPUT" | grep -q "token="; then
        TOKEN=$(echo "$DASHBOARD_OUTPUT" | grep -o "token=[a-f0-9]*" | head -1 | cut -d= -f2)
        echo "   ✅ تم استخراج التوكن: ${TOKEN:0:8}..."
    fi
    
    if [ -z "$TOKEN" ]; then
        # محاولة بديلة: البحث في ملفات OpenClaw
        echo "   ⚠️  لم أستطع استخراج التوكن، أجرب مصدر بديل..."
        if [ -f ~/.openclaw/identity/device-auth.json ]; then
            DEVICE_TOKEN=$(grep -o '"token":"[^"]*"' ~/.openclaw/identity/device-auth.json | cut -d'"' -f4 | head -1)
            if [ ! -z "$DEVICE_TOKEN" ]; then
                TOKEN="$DEVICE_TOKEN"
                echo "   ✅ استخدام توكن الجهاز: ${TOKEN:0:8}..."
            fi
        fi
    fi
    
    ATTEMPTS=$((ATTEMPTS+1))
    if [ -z "$TOKEN" ] && [ $ATTEMPTS -lt $MAX_ATTEMPTS ]; then
        sleep 2
    fi
done

if [ -z "$TOKEN" ]; then
    echo "❌ فشل في الحصول على التوكن!"
    echo "   حاول يدوياً: openclaw dashboard --no-open"
    exit 1
fi

echo "✅ تم الحصول على التوكن بنجاح!"

# الخطوة 2: الانتقال لمجلد الداشبورد
echo ""
echo "📁 الخطوة 2: الانتقال لمجلد الداشبورد..."

DASHBOARD_DIR="$HOME/.openclaw/workspace/skills/openclaw-dashboard"
if [ ! -d "$DASHBOARD_DIR" ]; then
    echo "❌ مجلد الداشبورد غير موجود!"
    echo "   قم بتثبيت المهارة أولاً: npx clawhub@latest install openclaw-dashboard"
    exit 1
fi

cd "$DASHBOARD_DIR"
echo "✅ الانتقال إلى: $(pwd)"

# الخطوة 3: إعداد ملف .env
echo ""
echo "⚙️  الخطوة 3: إعداد ملف البيئة..."

cat > .env << EOF
# ملف البيئة للداشبورد المتطور
# تم إنشاؤه تلقائياً بواسطة dashboard-helper
OPENCLAW_AUTH_TOKEN=$TOKEN
DASHBOARD_HOST=127.0.0.1
# البورت سيتم تحديده في الخطوة التالية
EOF

echo "✅ تم إنشاء ملف .env"

# الخطوة 4: إيجاد بورت متاح
echo ""
echo "🔌 الخطوة 4: البحث عن بورت متاح..."

START_PORT=18792
END_PORT=18850
AVAILABLE_PORT=""

for port in $(seq $START_PORT $END_PORT); do
    if ! lsof -i :$port > /dev/null 2>&1; then
        AVAILABLE_PORT=$port
        break
    fi
done

if [ -z "$AVAILABLE_PORT" ]; then
    echo "❌ لم أجد أي بورت متاح بين $START_PORT و $END_PORT!"
    exit 1
fi

echo "✅ البورت المتاح: $AVAILABLE_PORT"

# تحديث ملف .env بالبورت
echo "DASHBOARD_PORT=$AVAILABLE_PORT" >> .env

# الخطوة 5: إيقاف أي داشبورد قديم شغال
echo ""
echo "🛑 الخطوة 5: إيقاف الداشبوردات القديمة..."

pkill -f "node.*api-server.js" 2>/dev/null || true
sleep 1

# إيقاف أي عملية على البورت المحدد
if lsof -i :$AVAILABLE_PORT > /dev/null 2>&1; then
    kill $(lsof -t -i :$AVAILABLE_PORT) 2>/dev/null || true
    sleep 1
fi

# الخطوة 6: تشغيل الداشبورد
echo ""
echo "🚀 الخطوة 6: تشغيل الداشبورد على البورت $AVAILABLE_PORT..."

# إنشاء مجلد للسجلات
LOGS_DIR="/tmp/openclaw-dashboard-logs"
mkdir -p "$LOGS_DIR"
LOG_FILE="$LOGS_DIR/dashboard-$AVAILABLE_PORT-$(date +%Y%m%d-%H%M%S).log"

# تشغيل الداشبورد في الخلفية
DASHBOARD_PORT=$AVAILABLE_PORT node api-server.js > "$LOG_FILE" 2>&1 &
DASHBOARD_PID=$!

echo "   📝 PID: $DASHBOARD_PID"
echo "   📄 سجلات: $LOG_FILE"

# الخطوة 7: التحقق من التشغيل
echo ""
echo "🔍 الخطوة 7: التحقق من تشغيل الداشبورد..."

sleep 3

CHECK_COUNT=0
MAX_CHECKS=10
DASHBOARD_RUNNING=false

while [ $CHECK_COUNT -lt $MAX_CHECKS ]; do
    if curl -s "http://127.0.0.1:$AVAILABLE_PORT?token=$TOKEN" > /dev/null 2>&1; then
        DASHBOARD_RUNNING=true
        break
    fi
    CHECK_COUNT=$((CHECK_COUNT+1))
    sleep 1
done

if $DASHBOARD_RUNNING; then
    echo "✅ الداشبورد شغال بنجاح!"
    
    # عرض آخر 5 أسطر من السجلات للتحقق
    echo ""
    echo "📋 آخر السجلات:"
    tail -5 "$LOG_FILE"
else
    echo "❌ الداشبورد فشل في التشغيل!"
    echo "   تحقق من السجلات: $LOG_FILE"
    kill $DASHBOARD_PID 2>/dev/null || true
    exit 1
fi

# الخطوة 8: عرض المعلومات النهائية
echo ""
echo "========================================"
echo "🎉 تم إعداد الداشبورد المتطور بنجاح!"
echo ""
echo "🔗 الرابط:"
echo "   http://127.0.0.1:$AVAILABLE_PORT?token=$TOKEN"
echo ""
echo "📊 معلومات تقنية:"
echo "   البورت: $AVAILABLE_PORT"
echo "   التوكن: ${TOKEN:0:8}..."
echo "   PID: $DASHBOARD_PID"
echo "   السجلات: $LOG_FILE"
echo ""
echo "🔧 لإيقاف الداشبورد:"
echo "   kill $DASHBOARD_PID"
echo ""
echo "🔄 للتحديث:"
echo "   أعد تشغيل هذا السكريبت"
echo "========================================"

# حفظ المعلومات في ملف للذاكرة
INFO_FILE="$HOME/.openclaw/workspace/dashboard-info.json"
cat > "$INFO_FILE" << EOF
{
  "dashboard": {
    "port": $AVAILABLE_PORT,
    "token": "$TOKEN",
    "pid": $DASHBOARD_PID,
    "log_file": "$LOG_FILE",
    "url": "http://127.0.0.1:$AVAILABLE_PORT?token=$TOKEN",
    "setup_time": "$(date -Iseconds)",
    "setup_by": "dashboard-helper"
  }
}
EOF

echo "💾 تم حفظ المعلومات في: $INFO_FILE"