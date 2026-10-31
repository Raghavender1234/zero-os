/*
 * Copyright (C) 2026 ZeroOS Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.zeroos.launcher.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

data class ZeroChatMessage(
    val id: String,
    val sender: String,
    val text: String,
    val timestamp: String,
    val isMe: Boolean,
    val status: Int, // 1 = Sent (✓), 2 = Delivered (✓✓ grey), 3 = Read (✓✓ blue)
    val attachmentType: String? = null, // "image", "audio", "file", null
    val attachmentName: String? = null,
    val attachmentSize: String? = null
)

data class ZeroChatContact(
    val id: String,
    val name: String,
    val handle: String, // e.g. "@alex.0"
    val phoneNumber: String,
    val onionAddress: String?,
    val isPaired: Boolean,
    val lastMessage: String,
    val lastMessageTime: String,
    val unreadCount: Int = 0,
    val isOnline: Boolean = true
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ZeroChatScreen(
    onDismiss: () -> Unit,
    modifier: Modifier = Modifier
) {
    // WhatsApp Dark Theme Palette
    val waDarkBg = Color(0xFF0B141A)
    val waSurface = Color(0xFF1F2C34)
    val waSentBubble = Color(0xFF005C4B)
    val waReceivedBubble = Color(0xFF202C33)
    val waAccentGreen = Color(0xFF00A884)
    val waSecondaryText = Color(0xFF8696A0)
    val waTickBlue = Color(0xFF53BDEB)

    var activeChatContact by remember { mutableStateOf<ZeroChatContact?>(null) }
    var inputText by remember { mutableStateOf("") }
    var showAttachmentSheet by remember { mutableStateOf(false) }

    val sampleContacts = remember {
        mutableStateListOf(
            ZeroChatContact(
                id = "1",
                name = "Alex Rivera",
                handle = "@alex.0",
                phoneNumber = "+1 555-0192",
                onionAddress = "alex4k7p...onion",
                isPaired = true,
                lastMessage = "Sent the encrypted budget spreadsheet over Tor",
                lastMessageTime = "12:42 PM",
                unreadCount = 2,
                isOnline = true
            ),
            ZeroChatContact(
                id = "2",
                name = "Dr. Maya Chen",
                handle = "@maya.0",
                phoneNumber = "+44 7700-900821",
                onionAddress = "maya9x2m...onion",
                isPaired = true,
                lastMessage = "Voice note: Lab results (0:34)",
                lastMessageTime = "Yesterday",
                unreadCount = 0,
                isOnline = false
            ),
            ZeroChatContact(
                id = "3",
                name = "David Kumar (Unpaired)",
                handle = "@david.0",
                phoneNumber = "+91 98765-43210",
                onionAddress = null,
                isPaired = false,
                lastMessage = "Tap to pair via 1-time silent SMS handshake",
                lastMessageTime = "Oct 28",
                unreadCount = 0,
                isOnline = false
            )
        )
    }

    val sampleMessages = remember {
        mutableStateListOf(
            ZeroChatMessage(
                id = "m1",
                sender = "Alex Rivera",
                text = "Hey! Is this connection completely serverless?",
                timestamp = "12:38 PM",
                isMe = false,
                status = 3
            ),
            ZeroChatMessage(
                id = "m2",
                sender = "Me",
                text = "Yes 100%. We are communicating directly device-to-device over Tor v3 onion routing. No Meta, no Google, no servers exist.",
                timestamp = "12:40 PM",
                isMe = true,
                status = 3
            ),
            ZeroChatMessage(
                id = "m3",
                sender = "Alex Rivera",
                text = "Here is the project proposal PDF. Streaming directly to your phone storage.",
                timestamp = "12:41 PM",
                isMe = false,
                status = 3,
                attachmentType = "file",
                attachmentName = "ZeroOS_Whitepaper_v1.pdf",
                attachmentSize = "4.2 MB"
            ),
            ZeroChatMessage(
                id = "m4",
                sender = "Alex Rivera",
                text = "Sent the encrypted budget spreadsheet over Tor",
                timestamp = "12:42 PM",
                isMe = false,
                status = 3
            )
        )
    }

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(waDarkBg)
    ) {
        if (activeChatContact == null) {
            // ==========================================
            // CHATS LIST VIEW (WHATSAPP STYLE)
            // ==========================================
            Column(modifier = Modifier.fillMaxSize()) {
                // Top App Bar
                Surface(
                    color = waSurface,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text(
                                    text = "ZeroChat",
                                    fontSize = 22.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = Color.White
                                )
                                Spacer(modifier = Modifier.width(10.dp))
                                // P2P Peer Status Pill
                                Box(
                                    modifier = Modifier
                                        .clip(RoundedCornerShape(12.dp))
                                        .background(Color(0xFF103B2B))
                                        .padding(horizontal = 8.dp, vertical = 3.dp)
                                ) {
                                    Text(
                                        text = "🟢 Tor v3 • 0 Servers",
                                        fontSize = 10.sp,
                                        fontWeight = FontWeight.SemiBold,
                                        color = waAccentGreen,
                                        fontFamily = FontFamily.Monospace
                                    )
                                }
                            }

                            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                Button(
                                    onClick = onDismiss,
                                    colors = ButtonDefaults.buttonColors(containerColor = Color.Transparent),
                                    contentPadding = PaddingValues(0.dp)
                                ) {
                                    Text("✕", fontSize = 20.sp, color = waSecondaryText)
                                }
                            }
                        }

                        Spacer(modifier = Modifier.height(12.dp))

                        // Security Hero Info
                        Text(
                            text = "Direct peer-to-peer messaging. No central server. No metadata logged.",
                            fontSize = 12.sp,
                            color = waSecondaryText
                        )
                    }
                }

                // Contact List
                LazyColumn(modifier = Modifier.fillMaxSize()) {
                    items(sampleContacts) { contact ->
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clickable { activeChatContact = contact }
                                .padding(horizontal = 16.dp, vertical = 12.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            // Avatar
                            Box(
                                modifier = Modifier
                                    .size(50.dp)
                                    .clip(CircleShape)
                                    .background(if (contact.isPaired) waAccentGreen.copy(alpha = 0.2f) else Color(0xFF333333)),
                                contentAlignment = Alignment.Center
                            ) {
                                Text(
                                    text = contact.name.take(1),
                                    fontSize = 20.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = if (contact.isPaired) waAccentGreen else Color.LightGray
                                )
                            }

                            Spacer(modifier = Modifier.width(14.dp))

                            // Contact info
                            Column(modifier = Modifier.weight(1f)) {
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween
                                ) {
                                    Text(
                                        text = contact.name,
                                        fontSize = 16.sp,
                                        fontWeight = FontWeight.SemiBold,
                                        color = Color.White
                                    )
                                    Text(
                                        text = contact.lastMessageTime,
                                        fontSize = 12.sp,
                                        color = if (contact.unreadCount > 0) waAccentGreen else waSecondaryText
                                    )
                                }

                                Spacer(modifier = Modifier.height(4.dp))

                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Text(
                                        text = contact.lastMessage,
                                        fontSize = 13.sp,
                                        color = waSecondaryText,
                                        maxLines = 1,
                                        modifier = Modifier.weight(1f)
                                    )

                                    if (contact.unreadCount > 0) {
                                        Box(
                                            modifier = Modifier
                                                .size(20.dp)
                                                .clip(CircleShape)
                                                .background(waAccentGreen),
                                            contentAlignment = Alignment.Center
                                        ) {
                                            Text(
                                                text = "${contact.unreadCount}",
                                                fontSize = 11.sp,
                                                fontWeight = FontWeight.Bold,
                                                color = Color.Black
                                            )
                                        }
                                    } else if (!contact.isPaired) {
                                        Text(
                                            text = "PAIR",
                                            fontSize = 10.sp,
                                            fontWeight = FontWeight.Bold,
                                            color = Color(0xFFF59E0B),
                                            fontFamily = FontFamily.Monospace
                                        )
                                    }
                                }
                            }
                        }
                        Divider(color = Color(0xFF1B2428), thickness = 0.5.dp, modifier = Modifier.padding(start = 80.dp))
                    }
                }
            }
        } else {
            // ==========================================
            // ACTIVE CONVERSATION VIEW (WHATSAPP STYLE)
            // ==========================================
            val currentContact = activeChatContact!!

            Column(modifier = Modifier.fillMaxSize()) {
                // Chat Header Bar
                Surface(
                    color = waSurface,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 8.dp, vertical = 8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        // Back Arrow
                        IconButton(onClick = { activeChatContact = null }) {
                            Text("←", fontSize = 22.sp, color = Color.White)
                        }

                        // Avatar
                        Box(
                            modifier = Modifier
                                .size(38.dp)
                                .clip(CircleShape)
                                .background(waAccentGreen.copy(alpha = 0.3f)),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                text = currentContact.name.take(1),
                                fontSize = 16.sp,
                                fontWeight = FontWeight.Bold,
                                color = waAccentGreen
                            )
                        }

                        Spacer(modifier = Modifier.width(10.dp))

                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = currentContact.name,
                                fontSize = 16.sp,
                                fontWeight = FontWeight.Bold,
                                color = Color.White
                            )
                            Text(
                                text = if (currentContact.isPaired) "online over Tor v3" else "Unpaired • Carrier SMS bootstrap ready",
                                fontSize = 11.sp,
                                color = if (currentContact.isPaired) waAccentGreen else Color(0xFFF59E0B)
                            )
                        }

                        Text("🔒 P2P", fontSize = 12.sp, color = waSecondaryText, fontFamily = FontFamily.Monospace)
                    }
                }

                // Chat Messages Scroll
                LazyColumn(
                    modifier = Modifier
                        .weight(1f)
                        .padding(horizontal = 12.dp),
                    reverseLayout = false
                ) {
                    // E2E Security Banner
                    item {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 12.dp),
                            contentAlignment = Alignment.Center
                        ) {
                            Surface(
                                color = Color(0xFF182229),
                                shape = RoundedCornerShape(8.dp)
                            ) {
                                Text(
                                    text = "🔒 Messages and files are end-to-end encrypted directly device-to-device over Tor v3. No central servers exist.",
                                    fontSize = 11.sp,
                                    color = Color(0xFFFFD279),
                                    textAlign = androidx.compose.ui.text.style.TextAlign.Center,
                                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp)
                                )
                            }
                        }
                    }

                    // Handshake card if unpaired
                    if (!currentContact.isPaired) {
                        item {
                            Surface(
                                color = Color(0xFF1E2830),
                                shape = RoundedCornerShape(12.dp),
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(vertical = 8.dp)
                            ) {
                                Column(modifier = Modifier.padding(16.dp)) {
                                    Text(
                                        text = "⚡ 1-Time Silent SMS Handshake",
                                        fontSize = 14.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = Color.White
                                    )
                                    Spacer(modifier = Modifier.height(6.dp))
                                    Text(
                                        text = "Send an invisible carrier SMS to exchange Tor v3 onion keys. Once paired, carrier SMS is never used again.",
                                        fontSize = 12.sp,
                                        color = waSecondaryText
                                    )
                                    Spacer(modifier = Modifier.height(12.dp))
                                    Button(
                                        onClick = {
                                            // Trigger silent carrier handshake
                                        },
                                        colors = ButtonDefaults.buttonColors(containerColor = waAccentGreen)
                                    ) {
                                        Text("🤝 Initiate 1-Time Handshake", color = Color.Black, fontWeight = FontWeight.Bold)
                                    }
                                }
                            }
                        }
                    }

                    // Message Bubbles
                    items(sampleMessages) { msg ->
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 4.dp),
                            contentAlignment = if (msg.isMe) Alignment.CenterEnd else Alignment.CenterStart
                        ) {
                            Surface(
                                color = if (msg.isMe) waSentBubble else waReceivedBubble,
                                shape = RoundedCornerShape(
                                    topStart = 12.dp,
                                    topEnd = 12.dp,
                                    bottomStart = if (msg.isMe) 12.dp else 2.dp,
                                    bottomEnd = if (msg.isMe) 2.dp else 12.dp
                                ),
                                modifier = Modifier.widthIn(max = 300.dp)
                            ) {
                                Column(modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp)) {
                                    // Attachment preview if present
                                    if (msg.attachmentType == "file") {
                                        Surface(
                                            color = Color(0xFF121B22),
                                            shape = RoundedCornerShape(6.dp),
                                            modifier = Modifier
                                                .fillMaxWidth()
                                                .padding(bottom = 6.dp)
                                        ) {
                                            Row(
                                                modifier = Modifier.padding(8.dp),
                                                verticalAlignment = Alignment.CenterVertically
                                            ) {
                                                Text("📄", fontSize = 24.sp)
                                                Spacer(modifier = Modifier.width(8.dp))
                                                Column {
                                                    Text(
                                                        text = msg.attachmentName ?: "File",
                                                        fontSize = 13.sp,
                                                        fontWeight = FontWeight.SemiBold,
                                                        color = Color.White
                                                    )
                                                    Text(
                                                        text = "${msg.attachmentSize} • Tor P2P",
                                                        fontSize = 11.sp,
                                                        color = waSecondaryText
                                                    )
                                                }
                                            }
                                        }
                                    }

                                    // Message text
                                    Text(
                                        text = msg.text,
                                        fontSize = 14.sp,
                                        color = Color.White
                                    )

                                    // Timestamp and ticks
                                    Row(
                                        modifier = Modifier.align(Alignment.End),
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Text(
                                            text = msg.timestamp,
                                            fontSize = 11.sp,
                                            color = waSecondaryText
                                        )
                                        if (msg.isMe) {
                                            Spacer(modifier = Modifier.width(4.dp))
                                            Text(
                                                text = if (msg.status == 3) "✓✓" else "✓",
                                                fontSize = 13.sp,
                                                fontWeight = FontWeight.Bold,
                                                color = if (msg.status == 3) waTickBlue else waSecondaryText
                                            )
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                // Bottom Input Bar (WhatsApp style)
                Surface(
                    color = waSurface,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 8.dp, vertical = 8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        // Attachment Paperclip
                        IconButton(onClick = { showAttachmentSheet = !showAttachmentSheet }) {
                            Text("📎", fontSize = 20.sp)
                        }

                        // Text Field
                        TextField(
                            value = inputText,
                            onValueChange = { inputText = it },
                            placeholder = { Text("Message via Tor P2P...", fontSize = 14.sp, color = waSecondaryText) },
                            colors = TextFieldDefaults.colors(
                                focusedContainerColor = Color(0xFF2A3942),
                                unfocusedContainerColor = Color(0xFF2A3942),
                                focusedTextColor = Color.White,
                                unfocusedTextColor = Color.White,
                                focusedIndicatorColor = Color.Transparent,
                                unfocusedIndicatorColor = Color.Transparent
                            ),
                            shape = RoundedCornerShape(24.dp),
                            modifier = Modifier
                                .weight(1f)
                                .height(48.dp)
                        )

                        Spacer(modifier = Modifier.width(6.dp))

                        // Send / Voice Note Button
                        Box(
                            modifier = Modifier
                                .size(44.dp)
                                .clip(CircleShape)
                                .background(waAccentGreen)
                                .clickable {
                                    if (inputText.isNotBlank()) {
                                        sampleMessages.add(
                                            ZeroChatMessage(
                                                id = "m_${System.currentTimeMillis()}",
                                                sender = "Me",
                                                text = inputText,
                                                timestamp = "Now",
                                                isMe = true,
                                                status = 3 // Double blue tick
                                            )
                                        )
                                        inputText = ""
                                    }
                                },
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                text = if (inputText.isNotBlank()) "➤" else "🎙️",
                                fontSize = 18.sp,
                                color = Color.Black
                            )
                        }
                    }
                }
            }
        }
    }
}
