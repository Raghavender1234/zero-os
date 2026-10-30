package com.zeroos.launcher.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

data class MessageThread(
    val sender: String,
    val initial: String,
    val avatarBg: Color,
    val preview: String,
    val timeAgo: String
)

/**
 * ZeroMessages Screen
 * 
 * Features:
 * • 1-Tap 2FA / OTP Auto-Cleanup (Copies verification code, schedules auto-delete after 15m)
 * • Decoupled Push & Privacy (Zero link-preview tracking or advertising analytics)
 * • Anti-Spam Calm Digest Filter (Promotional SMS silenced automatically)
 */
@Composable
fun ZeroMessagesView(
    onToast: (String) -> Unit
) {
    var isOtpCopied by remember { mutableStateOf(false) }

    val threads = listOf(
        MessageThread("Mom", "M", Color(0xFF2563EB), "Call me when you get home this evening!", "4m ago"),
        MessageThread("Sarah Jenkins", "S", Color(0xFFEA580C), "Are we still on for lunch tomorrow afternoon?", "1h ago"),
        MessageThread("Alex Rivera", "A", Color(0xFF059669), "Sent you the project documents over email.", "Yesterday")
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black)
            .padding(horizontal = 16.dp, vertical = 20.dp)
    ) {
        // 1. HERO 1-TAP 2FA / OTP AUTO-CLEANUP CARD
        Card(
            shape = RoundedCornerShape(18.dp),
            colors = CardDefaults.cardColors(containerColor = Color(0xFF121212)),
            border = CardDefaults.outlinedCardBorder().copy(
                brush = androidx.compose.ui.graphics.SolidColor(Color(0xFF30D158).copy(alpha = 0.4f))
            ),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(14.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "🔐 BANKING 2FA / OTP DETECTED",
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF30D158)
                    )
                    Text(
                        text = "1m ago",
                        fontSize = 11.sp,
                        color = Color(0xFF8E8E93)
                    )
                }

                Spacer(modifier = Modifier.height(6.dp))

                Text(
                    text = "HDFC Bank / Chase: Use code 849 201 to verify online transaction.",
                    fontSize = 13.sp,
                    color = Color.White
                )

                Spacer(modifier = Modifier.height(10.dp))

                if (!isOtpCopied) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Button(
                            onClick = {
                                isOtpCopied = true
                                onToast("📋 Copied OTP 849201! Message will auto-delete in 15 minutes.")
                            },
                            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF30D158)),
                            shape = RoundedCornerShape(12.dp),
                            contentPadding = PaddingValues(horizontal = 14.dp, vertical = 6.dp)
                        ) {
                            Text(
                                text = "📋 Copy 849201 & Auto-Delete in 15m",
                                color = Color.Black,
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }
                        Text(
                            text = "Expires in 14m",
                            fontSize = 10.sp,
                            color = Color(0xFF8E8E93)
                        )
                    }
                } else {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(Color(0xFF1C1C1E), RoundedCornerShape(10.dp))
                            .padding(8.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = "✓ Copied! Auto-delete timer running (14m 58s remaining to self-destruct)",
                            fontSize = 11.sp,
                            color = Color(0xFF30D158)
                        )
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // 2. CONVERSATION THREADS
        LazyColumn(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            items(threads.size) { index ->
                val thread = threads[index]
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { onToast("💬 Opened chat with ${thread.sender}") }
                        .padding(vertical = 10.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Box(
                        modifier = Modifier
                            .size(42.dp)
                            .background(thread.avatarBg, CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = thread.initial,
                            color = Color.White,
                            fontWeight = FontWeight.Bold,
                            fontSize = 15.sp
                        )
                    }

                    Spacer(modifier = Modifier.width(12.dp))

                    Column(modifier = Modifier.weight(1f)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(
                                text = thread.sender,
                                fontSize = 14.sp,
                                fontWeight = FontWeight.SemiBold,
                                color = Color.White
                            )
                            Text(
                                text = thread.timeAgo,
                                fontSize = 11.sp,
                                color = Color(0xFF8E8E93)
                            )
                        }
                        Spacer(modifier = Modifier.height(2.dp))
                        Text(
                            text = thread.preview,
                            fontSize = 12.sp,
                            color = Color(0xFF8E8E93),
                            maxLines = 1
                        )
                    }
                }
            }
        }

        // 3. CALM DIGEST MARKETING SMS SPAM FILTER BANNER
        Card(
            shape = RoundedCornerShape(14.dp),
            colors = CardDefaults.cardColors(containerColor = Color(0xFF171717)),
            border = CardDefaults.outlinedCardBorder().copy(
                brush = androidx.compose.ui.graphics.SolidColor(Color(0xFF27272A))
            ),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(modifier = Modifier.padding(12.dp)) {
                Text(
                    text = "🔕 Calm Digest Filter Active",
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFFFFD60A)
                )
                Spacer(modifier = Modifier.height(2.dp))
                Text(
                    text = "3 marketing SMS (Uber, Domino's, Telecom) held quietly without vibration or unprompted screen wakes.",
                    fontSize = 11.sp,
                    color = Color(0xFF8E8E93)
                )
            }
        }
    }
}
