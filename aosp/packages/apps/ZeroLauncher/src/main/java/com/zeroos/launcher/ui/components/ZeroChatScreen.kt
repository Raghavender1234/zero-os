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
    val attachmentType: String? = null,
    val attachmentName: String? = null,
    val attachmentSize: String? = null
)

data class ZeroChatContact(
    val id: String,
    val name: String,
    val handle: String,
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
    val waDarkBg = Color(0xFF0B141A)
    val waSurface = Color(0xFF1F2C34)
    val waSentBubble = Color(0xFF005C4B)
    val waReceivedBubble = Color(0xFF202C33)
    val waAccentGreen = Color(0xFF00A884)
    val waSecondaryText = Color(0xFF8696A0)
    val waTickBlue = Color(0xFF53BDEB)

    var activeChatContact by remember { mutableStateOf<ZeroChatContact?>(null) }
    var inputText by remember { mutableStateOf("") }

    val sampleContacts = remember {
        mutableStateListOf(
            ZeroChatContact("1", "Alex Rivera", "@alex.0", "+1 555-0192", "alex4k7p...onion", true, "Sent the encrypted budget spreadsheet over Tor", "12:42 PM", 2, true),
            ZeroChatContact("2", "Dr. Maya Chen", "@maya.0", "+44 7700-900821", "maya9x2m...onion", true, "Voice note: Lab results (0:34)", "Yesterday", 0, false),
            ZeroChatContact("3", "David Kumar (Unpaired)", "@david.0", "+91 98765-43210", null, false, "Tap to pair via 1-time silent SMS handshake", "Oct 28", 0, false)
        )
    }

    val sampleMessages = remember {
        mutableStateListOf(
            ZeroChatMessage("m1", "Alex Rivera", "Hey! Is this connection completely serverless?", "12:38 PM", false, 3),
            ZeroChatMessage("m2", "Me", "Yes 100%. We are communicating directly device-to-device over Tor v3 onion routing. No Meta, no Google, no servers exist.", "12:40 PM", true, 3),
            ZeroChatMessage("m3", "Alex Rivera", "Here is the project proposal PDF. Streaming directly to your phone storage.", "12:41 PM", false, 3, "file", "ZeroOS_Whitepaper_v1.pdf", "4.2 MB"),
            ZeroChatMessage("m4", "Alex Rivera", "Sent the encrypted budget spreadsheet over Tor", "12:42 PM", false, 3)
        )
    }

    Box(modifier = modifier.fillMaxSize().background(waDarkBg)) {
        if (activeChatContact == null) {
            Column(modifier = Modifier.fillMaxSize()) {
                Surface(color = waSurface, modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text("ZeroChat", fontSize = 22.sp, fontWeight = FontWeight.Bold, color = Color.White)
                                Spacer(modifier = Modifier.width(10.dp))
                                Box(
                                    modifier = Modifier.clip(RoundedCornerShape(12.dp)).background(Color(0xFF103B2B)).padding(horizontal = 8.dp, vertical = 3.dp)
                                ) {
                                    Text("🟢 Tor v3 • 0 Servers", fontSize = 10.sp, fontWeight = FontWeight.SemiBold, color = waAccentGreen, fontFamily = FontFamily.Monospace)
                                }
                            }
                            IconButton(onClick = onDismiss) {
                                Text("✕", fontSize = 20.sp, color = waSecondaryText)
                            }
                        }
                        Spacer(modifier = Modifier.height(12.dp))
                        Text("Direct peer-to-peer messaging. No central server. No metadata logged.", fontSize = 12.sp, color = waSecondaryText)
                    }
                }

                LazyColumn(modifier = Modifier.fillMaxSize()) {
                    items(sampleContacts) { contact ->
                        Row(
                            modifier = Modifier.fillMaxWidth().clickable { activeChatContact = contact }.padding(horizontal = 16.dp, vertical = 12.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Box(
                                modifier = Modifier.size(50.dp).clip(CircleShape).background(if (contact.isPaired) waAccentGreen.copy(alpha = 0.2f) else Color(0xFF333333)),
                                contentAlignment = Alignment.Center
                            ) {
                                Text(contact.name.take(1), fontSize = 20.sp, fontWeight = FontWeight.Bold, color = if (contact.isPaired) waAccentGreen else Color.LightGray)
                            }
                            Spacer(modifier = Modifier.width(14.dp))
                            Column(modifier = Modifier.weight(1f)) {
                                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                                    Text(contact.name, fontSize = 16.sp, fontWeight = FontWeight.SemiBold, color = Color.White)
                                    Text(contact.lastMessageTime, fontSize = 12.sp, color = if (contact.unreadCount > 0) waAccentGreen else waSecondaryText)
                                }
                                Spacer(modifier = Modifier.height(4.dp))
                                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                                    Text(contact.lastMessage, fontSize = 13.sp, color = waSecondaryText, maxLines = 1, modifier = Modifier.weight(1f))
                                    if (contact.unreadCount > 0) {
                                        Box(modifier = Modifier.size(20.dp).clip(CircleShape).background(waAccentGreen), contentAlignment = Alignment.Center) {
                                            Text("${contact.unreadCount}", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = Color.Black)
                                        }
                                    } else if (!contact.isPaired) {
                                        Text("PAIR", fontSize = 10.sp, fontWeight = FontWeight.Bold, color = Color(0xFFF59E0B), fontFamily = FontFamily.Monospace)
                                    }
                                }
                            }
                        }
                        Divider(color = Color(0xFF1B2428), thickness = 0.5.dp, modifier = Modifier.padding(start = 80.dp))
                    }
                }
            }
        } else {
            val currentContact = activeChatContact!!
            Column(modifier = Modifier.fillMaxSize()) {
                Surface(color = waSurface, modifier = Modifier.fillMaxWidth()) {
                    Row(
                        modifier = Modifier.fillMaxWidth().padding(horizontal = 8.dp, vertical = 8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        IconButton(onClick = { activeChatContact = null }) {
                            Text("←", fontSize = 22.sp, color = Color.White)
                        }
                        Box(
                            modifier = Modifier.size(38.dp).clip(CircleShape).background(waAccentGreen.copy(alpha = 0.3f)),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(currentContact.name.take(1), fontSize = 16.sp, fontWeight = FontWeight.Bold, color = waAccentGreen)
                        }
                        Spacer(modifier = Modifier.width(10.dp))
                        Column(modifier = Modifier.weight(1f)) {
                            Text(currentContact.name, fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Color.White)
                            Text(if (currentContact.isPaired) "online over Tor v3" else "Unpaired • Carrier SMS bootstrap ready", fontSize = 11.sp, color = if (currentContact.isPaired) waAccentGreen else Color(0xFFF59E0B))
                        }
                        Text("🔒 P2P", fontSize = 12.sp, color = waSecondaryText, fontFamily = FontFamily.Monospace)
                    }
                }

                LazyColumn(modifier = Modifier.weight(1f).padding(horizontal = 12.dp)) {
                    item {
                        Box(modifier = Modifier.fillMaxWidth().padding(vertical = 12.dp), contentAlignment = Alignment.Center) {
                            Surface(color = Color(0xFF182229), shape = RoundedCornerShape(8.dp)) {
                                Text("🔒 Messages and files are end-to-end encrypted directly device-to-device over Tor v3. No central servers exist.", fontSize = 11.sp, color = Color(0xFFFFD279), modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp))
                            }
                        }
                    }

                    items(sampleMessages) { msg ->
                        Box(
                            modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
                            contentAlignment = if (msg.isMe) Alignment.CenterEnd else Alignment.CenterStart
                        ) {
                            Surface(
                                color = if (msg.isMe) waSentBubble else waReceivedBubble,
                                shape = RoundedCornerShape(12.dp),
                                modifier = Modifier.widthIn(max = 300.dp)
                            ) {
                                Column(modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp)) {
                                    if (msg.attachmentType == "file") {
                                        Surface(color = Color(0xFF121B22), shape = RoundedCornerShape(6.dp), modifier = Modifier.fillMaxWidth().padding(bottom = 6.dp)) {
                                            Row(modifier = Modifier.padding(8.dp), verticalAlignment = Alignment.CenterVertically) {
                                                Text("📄", fontSize = 24.sp)
                                                Spacer(modifier = Modifier.width(8.dp))
                                                Column {
                                                    Text(msg.attachmentName ?: "File", fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = Color.White)
                                                    Text("${msg.attachmentSize} • Tor P2P", fontSize = 11.sp, color = waSecondaryText)
                                                }
                                            }
                                        }
                                    }
                                    Text(msg.text, fontSize = 14.sp, color = Color.White)
                                    Row(modifier = Modifier.align(Alignment.End), verticalAlignment = Alignment.CenterVertically) {
                                        Text(msg.timestamp, fontSize = 11.sp, color = waSecondaryText)
                                        if (msg.isMe) {
                                            Spacer(modifier = Modifier.width(4.dp))
                                            Text(if (msg.status == 3) "✓✓" else "✓", fontSize = 13.sp, fontWeight = FontWeight.Bold, color = if (msg.status == 3) waTickBlue else waSecondaryText)
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                Surface(color = waSurface, modifier = Modifier.fillMaxWidth()) {
                    Row(modifier = Modifier.fillMaxWidth().padding(horizontal = 8.dp, vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
                        TextField(
                            value = inputText,
                            onValueChange = { inputText = it },
                            placeholder = { Text("Message", fontSize = 14.sp, color = waSecondaryText) },
                            colors = TextFieldDefaults.colors(
                                focusedContainerColor = Color(0xFF2A3942),
                                unfocusedContainerColor = Color(0xFF2A3942),
                                focusedTextColor = Color.White,
                                unfocusedTextColor = Color.White
                            ),
                            shape = RoundedCornerShape(24.dp),
                            modifier = Modifier.weight(1f).height(48.dp)
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Box(
                            modifier = Modifier.size(44.dp).clip(CircleShape).background(waAccentGreen).clickable {
                                if (inputText.isNotBlank()) {
                                    sampleMessages.add(ZeroChatMessage("m_${System.currentTimeMillis()}", "Me", inputText, "Now", true, 3))
                                    inputText = ""
                                }
                            },
                            contentAlignment = Alignment.Center
                        ) {
                            Text(if (inputText.isNotBlank()) "➤" else "🎙️", fontSize = 18.sp, color = Color.Black)
                        }
                    }
                }
            }
        }
    }
}
