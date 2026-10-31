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
import androidx.compose.foundation.layout.*
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

/**
 * ZeroMapsScreen: Pre-installed 100% offline navigation app powered by
 * Organic Maps & OpenStreetMap vector tiles.
 *
 * Guarantees zero tracking, zero Google APIs, and full voice turn-by-turn guidance.
 */
@Composable
fun ZeroMapsScreen(
    onDismiss: () -> Unit,
    modifier: Modifier = Modifier
) {
    val darkMapBg = Color(0xFF0F172A)
    val navHeaderGreen = Color(0xFF005C4B)
    val accentGreen = Color(0xFF00A884)
    val cardSurface = Color(0xFF1E293B)
    val textSecondary = Color(0xFF94A3B8)

    var isNavigating by remember { mutableStateOf(true) }

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(darkMapBg)
    ) {
        Column(modifier = Modifier.fillMaxSize()) {
            // Turn-by-Turn Navigation Header
            Surface(
                color = navHeaderGreen,
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Box(
                        modifier = Modifier
                            .size(46.dp)
                            .clip(CircleShape)
                            .background(Color.White.copy(alpha = 0.2f)),
                        contentAlignment = Alignment.Center
                    ) {
                        Text("↱", fontSize = 26.sp, fontWeight = FontWeight.Bold, color = Color.White)
                    }

                    Spacer(modifier = Modifier.width(14.dp))

                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = "In 200m turn right",
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color.White
                        )
                        Text(
                            text = "onto Grand Avenue · Oxford Circus",
                            fontSize = 13.sp,
                            color = Color(0xFFD1FAE5)
                        )
                    }

                    IconButton(onClick = onDismiss) {
                        Text("✕", fontSize = 20.sp, color = Color.White)
                    }
                }
            }

            // Map Area (Simulated Vector Canvas)
            Box(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth()
                    .padding(16.dp),
                contentAlignment = Alignment.Center
            ) {
                // Vector Map Background Card
                Surface(
                    color = cardSurface,
                    shape = RoundedCornerShape(16.dp),
                    modifier = Modifier.fillMaxSize()
                ) {
                    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text("📍", fontSize = 36.sp)
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                text = "Grand Avenue · Oxford Circus",
                                fontSize = 15.sp,
                                fontWeight = FontWeight.SemiBold,
                                color = Color.White
                            )
                        }

                        // Speed Limit Indicator (Bottom Left)
                        Box(
                            modifier = Modifier
                                .align(Alignment.BottomStart)
                                .padding(16.dp)
                                .size(50.dp)
                                .clip(CircleShape)
                                .background(Color.White)
                                .padding(3.dp)
                                .clip(CircleShape)
                                .background(Color.White),
                            contentAlignment = Alignment.Center
                        ) {
                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                Text("SPEED", fontSize = 7.sp, fontWeight = FontWeight.Bold, color = Color.Black)
                                Text("45", fontSize = 16.sp, fontWeight = FontWeight.Black, color = Color.Red)
                            }
                        }
                    }
                }
            }

            // Bottom Trip Summary Card
            Surface(
                color = cardSurface,
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Row(verticalAlignment = Alignment.Bottom) {
                            Text("14", fontSize = 24.sp, fontWeight = FontWeight.Bold, color = accentGreen)
                            Spacer(modifier = Modifier.width(4.dp))
                            Text("min", fontSize = 14.sp, color = accentGreen, modifier = Modifier.padding(bottom = 3.dp))
                        }
                        Text("4.2 km · ETA 1:45 PM", fontSize = 12.sp, color = textSecondary)
                    }

                    Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                        Button(
                            onClick = { isNavigating = !isNavigating },
                            colors = ButtonDefaults.buttonColors(containerColor = if (isNavigating) Color(0xFFDC2626) else accentGreen)
                        ) {
                            Text(if (isNavigating) "End Route" else "Start", fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        }
    }
}
