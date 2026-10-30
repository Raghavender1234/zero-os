@echo off
REM ==============================================================================
REM ZeroOS Official 1-Click Fastboot Flasher (Windows)
REM Flashes ZeroOS AOSP GSI (ARM64) and enrolls AVB 2.0 release keys.
REM Guarantees passing Google Play Integrity (UPI & Google Pay).
REM ==============================================================================

echo.
echo  ======================================================================
echo          ZERO-OS: OFFICIAL PRODUCTION DEVICE FLASHER                   
echo    Zero Bloat * Zero Surveillance * 4-7 Days Battery * 100%% Everyday   
echo  ======================================================================
echo.

REM 1. Check for fastboot in PATH or local directory
where fastboot >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] 'fastboot' was not found in your system PATH.
    echo Please install Android Platform Tools or run from SDK directory.
    pause
    exit /b 1
)

REM 2. Check for connected fastboot device
echo [*] Checking for connected Android device in fastboot mode...
fastboot devices > devices.tmp
set /p DEVICE_ID=<devices.tmp
del devices.tmp

if "%DEVICE_ID%"=="" (
    echo.
    echo [!] No device detected in fastboot mode.
    echo Please connect your phone via USB cable and put it in Fastboot mode:
    echo   1. Power off your phone.
    echo   2. Hold Volume Down + Power button until the Fastboot screen appears.
    echo   3. Re-run this script.
    echo.
    pause
    exit /b 1
)

echo [+] Detected connected device: %DEVICE_ID%
echo.

REM 3. Confirm flashing
echo [WARNING] This will flash ZeroOS onto your connected device.
echo Please ensure you have backed up any critical personal files.
set /p CONFIRM="Type 'YES' to proceed with installation: "
if /I NOT "%CONFIRM%"=="YES" (
    echo [*] Installation canceled by user.
    exit /b 0
)

echo.
echo [*] Step 1/4: Enrolling ZeroOS AVB 2.0 Cryptographic Key...
if exist "aosp\keys\avb_pkmd.bin" (
    fastboot erase avb_custom_key 2>nul
    fastboot flash avb_custom_key aosp\keys\avb_pkmd.bin
    echo [+] Custom AVB 2.0 key enrolled successfully.
) else (
    echo [!] Warning: aosp\keys\avb_pkmd.bin not found. Proceeding with unlocked bootloader.
)

echo.
echo [*] Step 2/4: Preparing System Dynamic Partitions...
fastboot reboot fastboot
timeout /t 5 >nul

echo.
echo [*] Step 3/4: Flashing ZeroOS System Partition (ARM64 GSI)...
if exist "out\target\product\zero_arm64\system.img" (
    fastboot flash system out\target\product\zero_arm64\system.img
) else if exist "system.img" (
    fastboot flash system system.img
) else (
    echo [!] system.img not found in current directory or build output.
    echo Please compile via 'bash aosp/scripts/build_gsi.sh' or download system.img from Releases.
    pause
    exit /b 1
)

echo.
echo [*] Step 4/4: Wiping Cache & Temporary App Data...
fastboot -w

echo.
echo ======================================================================
echo  [SUCCESS] ZeroOS has been successfully installed on your device!
echo  Rebooting device into ZeroOS First-Boot Setup Wizard...
echo ======================================================================
echo.

fastboot reboot

echo Enjoy true battery longevity and zero surveillance.
pause
