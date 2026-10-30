# ZeroOS Seamless Data Migration Guide

Switching to ZeroOS does **not** mean losing your personal data. ZeroOS is engineered to import your contacts, messages, photos, and chat histories locally—without routing your personal life through corporate cloud scrapers.

---

## 1. Migrating from an Existing Android Phone (Samsung, Pixel, OnePlus, Xiaomi)

### A. Contacts (Offline VCF Export)
1. On your old phone, open **Contacts** $\rightarrow$ **Settings / Fix & Manage** $\rightarrow$ **Export to file (`contacts.vcf`)**.
2. Save `contacts.vcf` to a USB drive or transfer via USB-C cable to your computer.
3. On ZeroOS, open **ZeroPhone** $\rightarrow$ **Contacts** $\rightarrow$ **Import from .vcf**.
4. All contacts are restored instantly to your phone's encrypted on-device SQLite database.

### B. SMS & Call History
1. On your old phone, install **SMS Backup & Restore** (free on Play Store) or open-source **SmsBack** from F-Droid.
2. Export SMS threads and call logs as an XML file.
3. On ZeroOS, open **ZeroMessages** $\rightarrow$ **Import XML**.
4. All historical threads are indexed locally with immediate 0-delay search.

### C. Photos & Media
1. Connect your old phone to your PC via USB-C cable (File Transfer / MTP mode).
2. Copy your `DCIM/Camera`, `Pictures`, and `Music` folders to your PC.
3. Connect your ZeroOS phone and paste the folders directly into `/sdcard/DCIM/` and `/sdcard/Music/`.
4. ZeroOS's local media scanner indexes your photos and albums automatically.

### D. WhatsApp & Signal Chats
1. **WhatsApp Local Transfer:**
   * On old phone: **Settings** $\rightarrow$ **Chats** $\rightarrow$ **Transfer Chats** $\rightarrow$ **Transfer to new Android phone** (direct Wi-Fi P2P transfer).
   * Alternatively: Copy `/sdcard/Android/media/com.whatsapp/WhatsApp/Databases/msgstore.db.crypt14` to the same folder on ZeroOS before logging in.
2. **Signal:**
   * On old phone: **Settings** $\rightarrow$ **Chats** $\rightarrow$ **Chat backups** $\rightarrow$ **Turn on**.
   * Note down the 30-digit passphrase and copy the backup file to your ZeroOS phone.

---

## 2. Migrating from an iPhone (iOS to ZeroOS)

### A. Contacts & Calendars
1. Go to [iCloud.com](https://www.icloud.com) on your computer and log in with your Apple ID.
2. Click **Contacts** $\rightarrow$ Press `Ctrl + A` (or `Cmd + A`) $\rightarrow$ Click the **Settings Gear** at bottom-left $\rightarrow$ Select **Export vCard...**.
3. Transfer the downloaded `.vcf` file to your ZeroOS phone and tap to import.

### B. Photos & Videos
1. Connect your iPhone to your Windows or Mac PC via Lightning/USB-C cable.
2. Open Windows Photos or Apple Image Capture and export all full-resolution photos to your hard drive.
3. Connect your ZeroOS device and copy the images to `/sdcard/DCIM/Camera/`.

### C. WhatsApp Chats (Direct Cable Transfer)
1. Connect your iPhone and ZeroOS phone using a **USB-C to Lightning** cable (or USB-C to USB-C).
2. During the ZeroOS **Setup Wizard (OOBE)**, select **Transfer from iPhone**.
3. Open WhatsApp on iPhone $\rightarrow$ **Settings** $\rightarrow$ **Chats** $\rightarrow$ **Move Chats to Android**.
4. Scan the QR code shown on ZeroOS; chats, media, and voice notes will transfer over the high-speed USB cable.

---

## 3. Post-Migration Privacy Verification Check

Once your data is transferred:
1. Long-press the power button to open the **ZeroOS Command Center**.
2. Type: `show impact stats`.
3. Verify:
   * **Trackers Blocked:** Background ad beacons from newly installed apps will immediately start getting rejected by the Linux kernel netfilter.
   * **Background Data:** 0 B/s data transmitted when apps are minimized.
   * **Storage Encryption:** Hardware TrustZone FBE (File-Based Encryption) active.
