import os
import re

auth_ts_path = '/home/mohamed/MyAtelier_pro/frontend/src/text/auth.ts'
login_path = '/home/mohamed/MyAtelier_pro/frontend/src/pages/LoginPage.tsx'
twofa_path = '/home/mohamed/MyAtelier_pro/frontend/src/features/auth/components/TwoFASetupModal.tsx'

with open(auth_ts_path, 'w', encoding='utf-8') as f:
    f.write("""import { useLocalizedText } from './useText';

const authText = {
  ar: {
    fallbackError: 'تعذر تسجيل الدخول',
    helper: 'عند تشغيل قاعدة بيانات جديدة لأول مرة يتم إنشاء المستخدم الافتراضي:',
    password: 'كلمة المرور',
    subtitle: 'سجّل الدخول لبدء استخدام MyAtelier Pro',
    submitting: 'جارٍ تسجيل الدخول...',
    submit: 'تسجيل الدخول',
    title: 'مرحبًا بك',
    username: 'اسم المستخدم',
    loginTitle: 'MyAtelier Pro',
    loginSubtitle: 'سجل دخولك لإدارة ورشتك بكفاءة',
    twoFA_Title: 'التحقق الثنائي',
    twoFA_Subtitle: 'يرجى إدخال رمز التحقق الإضافي للمتابعة',
    backupCodeTitle: 'كود الطوارئ',
    twoFA_CodeLabel: 'رمز التحقق (6 أرقام)',
    backupCodeLabel: 'كود النسخ الاحتياطي',
    useAppCode: 'استخدام رمز التطبيق',
    useBackupCode: 'استخدم كود النسخ الاحتياطي',
    confirmCode: 'تأكيد الرمز',
    setupTitle: 'تفعيل التحقق الثنائي',
    stepSetup: 'الإعداد',
    stepScan: 'المسح الضوئي',
    stepVerify: 'التحقق',
    stepSecurity: 'الأمان الإضافي',
    startSetupFailed: 'فشل بدء إعداد التحقق الثنائي',
    invalidCode: 'رمز التحقق غير صحيح',
    enhanceSecurityTitle: 'عزز أمان حسابك',
    enhanceSecurityDesc: 'يحمي التحقق الثنائي حسابك عبر طلب رمز إضافي عند تسجيل الدخول من جهاز جديد. ستحتاج إلى تطبيق مثل Google Authenticator أو Microsoft Authenticator.',
    phoneApp: 'تطبيق الهاتف',
    protectedAccount: 'حساب محمي',
    startSetupNow: 'بدء الإعداد الآن',
    scanQROrManual: '1. امسح رمز QR من هاتفك',
    manualEntryDesc: 'أو أدخل الرمز يدوياً إذا كنت لا تستطيع المسح:',
    scannedNext: 'تم المسح، التالي',
    enterCodeTitle: '2. أدخل الرمز المكون من 6 أرقام',
    enterCodeDesc: 'أدخل الرمز الذي يظهر الآن في تطبيق المصادقة الخاص بك.',
    back: 'رجوع',
    confirmActivation: 'تأكيد التفعيل',
    importantKeepCodes: 'هام: احتفظ بهذه الأكواد في مكان آمن للغاية. لن نتمكن من عرضها لك مرة أخرى!',
    copyAll: 'نسخ الكل',
    downloadAsFile: 'تحميل كملف',
    completeAndFinish: 'إكمال وإنهاء',
    cancel: 'إلغاء',
  },
  en: {
    fallbackError: 'Unable to sign in',
    helper: 'On a fresh database, the default account is created as:',
    password: 'Password',
    subtitle: 'Sign in to start using MyAtelier Pro',
    submitting: 'Signing in...',
    submit: 'Sign in',
    title: 'Welcome back',
    username: 'Username',
    loginTitle: 'MyAtelier Pro',
    loginSubtitle: 'Sign in to manage your atelier efficiently',
    twoFA_Title: 'Two-Factor Auth',
    twoFA_Subtitle: 'Please enter the additional verification code to proceed',
    backupCodeTitle: 'Backup Code',
    twoFA_CodeLabel: 'Verification Code (6 digits)',
    backupCodeLabel: 'Backup Code',
    useAppCode: 'Use App Code',
    useBackupCode: 'Use Backup Code',
    confirmCode: 'Confirm Code',
    setupTitle: 'Enable Two-Factor Authentication',
    stepSetup: 'Setup',
    stepScan: 'Scan',
    stepVerify: 'Verify',
    stepSecurity: 'Extra Security',
    startSetupFailed: 'Failed to start 2FA setup',
    invalidCode: 'Invalid verification code',
    enhanceSecurityTitle: 'Enhance Your Account Security',
    enhanceSecurityDesc: '2FA protects your account by requiring an additional code when logging in from a new device. You will need an app like Google Authenticator or Microsoft Authenticator.',
    phoneApp: 'Phone App',
    protectedAccount: 'Protected Account',
    startSetupNow: 'Start Setup Now',
    scanQROrManual: '1. Scan the QR code from your phone',
    manualEntryDesc: 'Or enter the code manually if you cannot scan:',
    scannedNext: 'Scanned, Next',
    enterCodeTitle: '2. Enter the 6-digit code',
    enterCodeDesc: 'Enter the code that now appears in your authenticator app.',
    back: 'Back',
    confirmActivation: 'Confirm Activation',
    importantKeepCodes: 'IMPORTANT: Keep these codes in a very safe place. We will not be able to show them to you again!',
    copyAll: 'Copy All',
    downloadAsFile: 'Download as File',
    completeAndFinish: 'Complete and Finish',
    cancel: 'Cancel',
  },
} as const;

export function useLoginText() {
  return useLocalizedText(authText);
}
""")

with open(login_path, 'r', encoding='utf-8') as f:
    login_content = f.read()

login_content = login_content.replace(
    "{is2FARequired ? (useBackupCode ? 'كود الطوارئ' : 'التحقق الثنائي') : 'MyAtelier Pro'}",
    "{is2FARequired ? (useBackupCode ? loginText.backupCodeTitle : loginText.twoFA_Title) : loginText.loginTitle}"
)
login_content = login_content.replace(
    "is2FARequired \n                      ? 'يرجى إدخال رمز التحقق الإضافي للمتابعة' \n                      : 'سجل دخولك لإدارة ورشتك بكفاءة'",
    "is2FARequired ? loginText.twoFA_Subtitle : loginText.loginSubtitle"
)
login_content = login_content.replace(
    "{is2FARequired \n                      ? 'يرجى إدخال رمز التحقق الإضافي للمتابعة' \n                      : 'سجل دخولك لإدارة ورشتك بكفاءة'}",
    "{is2FARequired ? loginText.twoFA_Subtitle : loginText.loginSubtitle}"
)
login_content = login_content.replace(
    "{useBackupCode ? 'كود النسخ الاحتياطي' : 'رمز التحقق (6 أرقام)'}",
    "{useBackupCode ? loginText.backupCodeLabel : loginText.twoFA_CodeLabel}"
)
login_content = login_content.replace(
    "{useBackupCode ? 'استخدام رمز التطبيق' : 'استخدم كود النسخ الاحتياطي'}",
    "{useBackupCode ? loginText.useAppCode : loginText.useBackupCode}"
)
login_content = login_content.replace(
    "{is2FARequired ? 'تأكيد الرمز' : loginText.submit}",
    "{is2FARequired ? loginText.confirmCode : loginText.submit}"
)

with open(login_path, 'w', encoding='utf-8') as f:
    f.write(login_content)


with open(twofa_path, 'r', encoding='utf-8') as f:
    twofa_content = f.read()

twofa_content = twofa_content.replace(
    "import { setup2FA, activate2FA, type TwoFASetupResponse } from '../api';",
    "import { setup2FA, activate2FA, type TwoFASetupResponse } from '../api';\nimport { useLoginText } from '../../text/auth';"
)
twofa_content = twofa_content.replace(
    "const steps = ['الإعداد', 'المسح الضوئي', 'التحقق', 'الأمان الإضافي'];",
    "// steps handled in component"
)

# Insert auth text hook
twofa_content = twofa_content.replace(
    "const theme = useTheme();",
    "const theme = useTheme();\n  const authText = useLoginText();\n  const steps = [authText.stepSetup, authText.stepScan, authText.stepVerify, authText.stepSecurity];"
)

twofa_content = twofa_content.replace("'فشل بدء إعداد التحقق الثنائي'", "authText.startSetupFailed")
twofa_content = twofa_content.replace("'رمز التحقق غير صحيح'", "authText.invalidCode")

twofa_content = twofa_content.replace("تفعيل التحقق الثنائي", "{authText.setupTitle}")
twofa_content = twofa_content.replace("عزز أمان حسابك", "{authText.enhanceSecurityTitle}")
twofa_content = twofa_content.replace(
    "يحمي التحقق الثنائي حسابك عبر طلب رمز إضافي عند تسجيل الدخول من جهاز جديد. \n                    ستحتاج إلى تطبيق مثل Google Authenticator أو Microsoft Authenticator.",
    "{authText.enhanceSecurityDesc}"
)
twofa_content = twofa_content.replace("يحمي التحقق الثنائي حسابك عبر طلب رمز إضافي عند تسجيل الدخول من جهاز جديد. ستحتاج إلى تطبيق مثل Google Authenticator أو Microsoft Authenticator.", "{authText.enhanceSecurityDesc}")

twofa_content = twofa_content.replace("تطبيق الهاتف", "{authText.phoneApp}")
twofa_content = twofa_content.replace("حساب محمي", "{authText.protectedAccount}")
twofa_content = twofa_content.replace("بدء الإعداد الآن", "{authText.startSetupNow}")
twofa_content = twofa_content.replace("1. امسح رمز QR من هاتفك", "{authText.scanQROrManual}")
twofa_content = twofa_content.replace("أو أدخل الرمز يدوياً إذا كنت لا تستطيع المسح:", "{authText.manualEntryDesc}")
twofa_content = twofa_content.replace("تم المسح، التالي", "{authText.scannedNext}")
twofa_content = twofa_content.replace("2. أدخل الرمز المكون من 6 أرقام", "{authText.enterCodeTitle}")
twofa_content = twofa_content.replace("أدخل الرمز الذي يظهر الآن في تطبيق المصادقة الخاص بك.", "{authText.enterCodeDesc}")
twofa_content = twofa_content.replace("رجوع", "{authText.back}")
twofa_content = twofa_content.replace("تأكيد التفعيل", "{authText.confirmActivation}")
twofa_content = twofa_content.replace("هام: احتفظ بهذه الأكواد في مكان آمن للغاية. لن نتمكن من عرضها لك مرة أخرى!", "{authText.importantKeepCodes}")
twofa_content = twofa_content.replace("نسخ الكل", "{authText.copyAll}")
twofa_content = twofa_content.replace("تحميل كملف", "{authText.downloadAsFile}")
twofa_content = twofa_content.replace("إكمال وإنهاء", "{authText.completeAndFinish}")
twofa_content = twofa_content.replace("إلغاء", "{authText.cancel}")

with open(twofa_path, 'w', encoding='utf-8') as f:
    f.write(twofa_content)

print("i18n replaced successfully.")
