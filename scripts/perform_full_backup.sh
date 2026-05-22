#!/bin/bash
# سكربت النسخ الاحتياطي المتكامل لبيئة Linux Mint (MyAtelier Pro)
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="storage/backups"
DB_CONTAINER="myatelier_db"
DB_USER="beauty"
DB_NAME="myatelier_pro"
ZIP_NAME="FULL_PRO_BACKUP_$TIMESTAMP.zip"
STAGING_DIR="/tmp/backup_staging_$TIMESTAMP"

echo "🔄 بدء عملية النسخ الاحتياطي الكامل..."

# 1. إنشاء المجلدات المؤقتة والمحلية
mkdir -p "$STAGING_DIR"
mkdir -p "$BACKUP_DIR"

# 2. تصدير قاعدة البيانات من حاوية Docker
echo "💾 تصدير قاعدة البيانات..."
if docker ps --format '{{.Names}}' | grep -Eq "^${DB_CONTAINER}$"; then
    docker exec $DB_CONTAINER pg_dump -U $DB_USER -d $DB_NAME > "$STAGING_DIR/database_dump.sql"
    echo "✅ تم تصدير قاعدة البيانات بنجاح."
else
    echo "⚠️ حاوية قاعدة البيانات $DB_CONTAINER غير قيد التشغيل. محاولة التصدير المحلي إن وجد..."
    if command -v pg_dump &> /dev/null; then
        pg_dump -U $DB_USER -d $DB_NAME > "$STAGING_DIR/database_dump.sql"
        echo "✅ تم التصدير المحلي بنجاح."
    else
        echo "❌ لم يتم العثور على وسيلة لتصدير قاعدة البيانات!"
    fi
fi

# 3. نسخ المرفقات وملفات الكود الأساسية (باستثناء الملفات غير الهامة)
echo "📂 نسخ الملفات والمرفقات..."
rsync -av --exclude='.git' \
          --exclude='node_modules' \
          --exclude='backend/venv' \
          --exclude='__pycache__' \
          --exclude='.pytest_cache' \
          --exclude='storage/backups' \
          . "$STAGING_DIR/"

# 4. ضغط المجلد بالكامل
echo "🤐 ضغط الملفات..."
if command -v zip &> /dev/null; then
    zip -r "$BACKUP_DIR/$ZIP_NAME" "$STAGING_DIR" > /dev/null
    echo "✅ تم ضغط الملفات بنجاح في حزمة: $BACKUP_DIR/$ZIP_NAME"
else
    echo "⚠️ أداة zip غير مثبتة. استخدام tar.gz بدلاً منها..."
    tar -czf "$BACKUP_DIR/FULL_PRO_BACKUP_$TIMESTAMP.tar.gz" -C "$STAGING_DIR" .
    ZIP_NAME="FULL_PRO_BACKUP_$TIMESTAMP.tar.gz"
fi

# 5. الرفع السحابي باستخدام rclone لـ Google Drive
if command -v rclone &> /dev/null; then
    echo "☁️ جاري الرفع لـ Google Drive عبر rclone..."
    rclone copy "$BACKUP_DIR/$ZIP_NAME" "gdrive:MyAtelier_Backups" --progress
    echo "✅ اكتمل الرفع السحابي."
else
    echo "⚠️ تنبيه: rclone غير مثبت. تم حفظ النسخة محلياً فقط في $BACKUP_DIR/$ZIP_NAME"
fi

# 6. تنظيف العمل المؤقت
rm -rf "$STAGING_DIR"
echo "✅ اكتملت عملية النسخ الاحتياطي بالكامل."
