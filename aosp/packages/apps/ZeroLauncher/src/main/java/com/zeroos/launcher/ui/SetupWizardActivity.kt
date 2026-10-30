package com.zeroos.launcher.ui

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.zeroos.launcher.ui.theme.ZeroTheme

/**
 * SetupWizardActivity (OOBE - Out of the Box Experience)
 * 
 * First-boot onboarding experience for new ZeroOS users:
 * • Step 1: Language & Welcome (Zero bloat manifesto)
 * • Step 2: Wi-Fi & Offline Freedom (No forced accounts)
 * • Step 3: Privacy & Air-Gap Policy selection
 * • Step 4: Display Profile (Color vs. DIA Mode Monochrome)
 */
class SetupWizardActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            ZeroTheme {
                var currentStep by remember { mutableStateOf(1) }
                var selectedLanguage by remember { mutableStateOf("English (US)") }
                var isAirGapDefault by remember { mutableStateOf(true) }
                var isDiaModePreferred by remember { mutableStateOf(false) }

                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(Color.Black)
                        .padding(24.dp)
                ) {
                    when (currentStep) {
                        1 -> StepWelcome(
                            selectedLang = selectedLanguage,
                            onSelectLang = { selectedLanguage = it },
                            onNext = { currentStep = 2 }
                        )
                        2 -> StepConnectivity(
                            onNext = { currentStep = 3 }
                        )
                        3 -> StepPrivacyPolicy(
                            isAirGap = isAirGapDefault,
                            onToggleAirGap = { isAirGapDefault = !isAirGapDefault },
                            onNext = { currentStep = 4 }
                        )
                        4 -> StepDisplayProfile(
                            isDiaMode = isDiaModePreferred,
                            onSelectMode = { isDiaModePreferred = it },
                            onFinish = {
                                // Complete setup and launch main shell
                                val intent = Intent(this@SetupWizardActivity, ZeroLauncherActivity::class.java)
                                startActivity(intent)
                                finish()
                            }
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun StepWelcome(
    selectedLang: String,
    onSelectLang: (String) -> Unit,
    onNext: () -> Unit
) {
    Column(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.SpaceBetween,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Spacer(modifier = Modifier.height(40.dp))
            Text(
                text = "ZERO·OS",
                fontSize = 28.sp,
                fontWeight = FontWeight.Bold,
                color = Color.White,
                fontFamily = FontFamily.Monospace,
                letterSpacing = 3.sp
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "Zero Bloat. Zero Surveillance. 4 to 7 Days Battery.",
                fontSize = 13.sp,
                color = Color(0xFF8E8E93),
                textAlign = TextAlign.Center
            )
        }

        Column(modifier = Modifier.fillMaxWidth()) {
            Text(
                text = "SELECT LANGUAGE",
                fontSize = 11.sp,
                color = Color(0xFF8E8E93),
                fontFamily = FontFamily.Monospace,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(bottom = 8.dp)
            )

            val languages = listOf("English (US)", "Español", "Deutsch", "Français", "हिन्दी (Hindi)")
            languages.forEach { lang ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { onSelectLang(lang) }
                        .padding(vertical = 10.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(lang, color = Color.White, fontSize = 15.sp)
                    if (lang == selectedLang) {
                        Text("✓", color = Color(0xFF30D158), fontWeight = FontWeight.Bold)
                    }
                }
            }
        }

        Button(
            onClick = onNext,
            modifier = Modifier.fillMaxWidth().height(52.dp),
            colors = ButtonDefaults.buttonColors(containerColor = Color.White),
            shape = RoundedCornerShape(16.dp)
        ) {
            Text("Get Started ›", color = Color.Black, fontSize = 15.sp, fontWeight = FontWeight.Bold)
        }
    }
}

@Composable
fun StepConnectivity(onNext: () -> Unit) {
    Column(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.SpaceBetween
    ) {
        Column {
            Spacer(modifier = Modifier.height(30.dp))
            Text("Network & Freedom", fontSize = 24.sp, fontWeight = FontWeight.Bold, color = Color.White)
            Text(
                "You are never required to sign into an account to use ZeroOS. No Google account, no ZeroOS account.",
                fontSize = 13.sp,
                color = Color(0xFF8E8E93),
                modifier = Modifier.padding(top = 6.dp)
            )

            Spacer(modifier = Modifier.height(24.dp))

            Card(
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = Color(0xFF121212)),
                border = CardDefaults.outlinedCardBorder().copy(brush = androidx.compose.ui.graphics.SolidColor(Color(0xFF27272A))),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(14.dp)) {
                    Text("📶 Connect to Wi-Fi", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = Color.White)
                    Text("Home-5G (Saved)", fontSize = 12.sp, color = Color(0xFF30D158), modifier = Modifier.padding(top = 2.dp))
                }
            }
        }

        Column(modifier = Modifier.fillMaxWidth()) {
            Button(
                onClick = onNext,
                modifier = Modifier.fillMaxWidth().height(52.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Color.White),
                shape = RoundedCornerShape(16.dp)
            ) {
                Text("Continue ›", color = Color.Black, fontSize = 15.sp, fontWeight = FontWeight.Bold)
            }
            Spacer(modifier = Modifier.height(8.dp))
            TextButton(
                onClick = onNext,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Use 100% Offline (No Internet)", color = Color(0xFF8E8E93), fontSize = 13.sp)
            }
        }
    }
}

@Composable
fun StepPrivacyPolicy(
    isAirGap: Boolean,
    onToggleAirGap: () -> Unit,
    onNext: () -> Unit
) {
    Column(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.SpaceBetween
    ) {
        Column {
            Spacer(modifier = Modifier.height(30.dp))
            Text("User-Intent Policy", fontSize = 24.sp, fontWeight = FontWeight.Bold, color = Color.White)
            Text(
                "Choose how the OS handles apps when you close them.",
                fontSize = 13.sp,
                color = Color(0xFF8E8E93),
                modifier = Modifier.padding(top = 6.dp)
            )

            Spacer(modifier = Modifier.height(20.dp))

            Card(
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = if (isAirGap) Color(0xFF171717) else Color(0xFF121212)),
                border = CardDefaults.outlinedCardBorder().copy(brush = androidx.compose.ui.graphics.SolidColor(if (isAirGap) Color.White else Color(0xFF27272A))),
                modifier = Modifier.fillMaxWidth().clickable { onToggleAirGap() }
            ) {
                Column(modifier = Modifier.padding(14.dp)) {
                    Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
                        Text("🛡️ Auto Air-Gap (Recommended)", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = Color.White)
                        if (isAirGap) Text("✓", color = Color(0xFF30D158), fontWeight = FontWeight.Bold)
                    }
                    Text(
                        "When you close an app, network sockets are instantly dropped. 0 background tracking, 4 to 7 days battery.",
                        fontSize = 12.sp,
                        color = Color(0xFF8E8E93),
                        modifier = Modifier.padding(top = 4.dp)
                    )
                }
            }
        }

        Button(
            onClick = onNext,
            modifier = Modifier.fillMaxWidth().height(52.dp),
            colors = ButtonDefaults.buttonColors(containerColor = Color.White),
            shape = RoundedCornerShape(16.dp)
        ) {
            Text("Next ›", color = Color.Black, fontSize = 15.sp, fontWeight = FontWeight.Bold)
        }
    }
}

@Composable
fun StepDisplayProfile(
    isDiaMode: Boolean,
    onSelectMode: (Boolean) -> Unit,
    onFinish: () -> Unit
) {
    Column(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.SpaceBetween
    ) {
        Column {
            Spacer(modifier = Modifier.height(30.dp))
            Text("Display Profile", fontSize = 24.sp, fontWeight = FontWeight.Bold, color = Color.White)
            Text(
                "Select your default display identity. You can change this anytime with a single tap.",
                fontSize = 13.sp,
                color = Color(0xFF8E8E93),
                modifier = Modifier.padding(top = 6.dp)
            )

            Spacer(modifier = Modifier.height(20.dp))

            // Option 1: Full OLED Color
            Card(
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = if (!isDiaMode) Color(0xFF171717) else Color(0xFF121212)),
                border = CardDefaults.outlinedCardBorder().copy(brush = androidx.compose.ui.graphics.SolidColor(if (!isDiaMode) Color.White else Color(0xFF27272A))),
                modifier = Modifier.fillMaxWidth().clickable { onSelectMode(false) }
            ) {
                Column(modifier = Modifier.padding(14.dp)) {
                    Text("🎨 Full Color OLED (120Hz)", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = Color.White)
                    Text("Smooth, beautiful, standard color palette with true pitch black backgrounds.", fontSize = 12.sp, color = Color(0xFF8E8E93), modifier = Modifier.padding(top = 2.dp))
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Option 2: DIA Mode Monochrome
            Card(
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = if (isDiaMode) Color(0xFF171717) else Color(0xFF121212)),
                border = CardDefaults.outlinedCardBorder().copy(brush = androidx.compose.ui.graphics.SolidColor(if (isDiaMode) Color.White else Color(0xFF27272A))),
                modifier = Modifier.fillMaxWidth().clickable { onSelectMode(true) }
            ) {
                Column(modifier = Modifier.padding(14.dp)) {
                    Text("🔋 DIA Mode (Monochrome)", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = Color.White)
                    Text("Deep-Idle Architecture: 1-bit high contrast monochrome for 5 to 7 days of battery longevity.", fontSize = 12.sp, color = Color(0xFF8E8E93), modifier = Modifier.padding(top = 2.dp))
                }
            }
        }

        Button(
            onClick = onFinish,
            modifier = Modifier.fillMaxWidth().height(52.dp),
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF30D158)),
            shape = RoundedCornerShape(16.dp)
        ) {
            Text("🚀 Enter ZeroOS", color = Color.Black, fontSize = 15.sp, fontWeight = FontWeight.Bold)
        }
    }
}
